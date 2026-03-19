"""Common utilities for CME expiration data.
"""
__copyright__ = "Copyright (C) 2021  Martin Blais"
__license__ = "Apache 2.0"

import itertools
import logging
import pathlib
import re
import time
from typing import Optional
from os import path

import petl
from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://www.cmegroup.com/tools-information/quikstrike/product-expiration-browser.html"


def get_expirations_filenames(directory: str) -> list[pathlib.Path]:
    """Find downloaded expiration files in the given directory."""
    return sorted(
        [
            p.absolute()
            for p in pathlib.Path(directory).iterdir()
            if re.match(r"Expirations.*\.csv$", p.name)
        ],
        key=lambda p: p.stat().st_mtime
    )


def fetch_expirations(tmpdir: str, headless: bool, username: str = None, password: str = None) -> None:
    # ... (rest of fetch_expirations content)
    """Fetch expirations for a subset of futures products using Selenium.
    """
    logging.info(f"Deleting previous files in {tmpdir}")
    for p in get_expirations_filenames(tmpdir):
        p.unlink()

    logging.info(f"Storing temporary files to {tmpdir}")

    # Create driver.
    opts = options.Options()
    if headless:
        opts.add_argument("--headless")
    opts.prompt_for_download = False
    prefs = {}
    opts.add_experimental_option("prefs", prefs)
    service = webdriver.ChromeService(executable_path="/usr/bin/chromedriver")
    driver = webdriver.Chrome(options=opts, service=service)

    try:
        # Perform login if credentials are provided.
        if username and password:
            logging.info("Logging into CME Group...")
            driver.get("https://login.cmegroup.com/")
            wait(driver, 20).until(
                lambda d: d.find_elements(By.ID, "user") or d.find_elements(By.ID, "username")
            )

            user_field = None
            for uid in ["user", "username"]:
                try:
                    user_field = driver.find_element(By.ID, uid)
                    break
                except:
                    continue
            if user_field:
                user_field.send_keys(username)

            pwd_field = None
            for pid in ["pwd", "password"]:
                try:
                    pwd_field = driver.find_element(By.ID, pid)
                    break
                except:
                    continue
            if pwd_field:
                pwd_field.send_keys(password)

            login_btn = None
            for bid in ["loginBtn", "login-btn"]:
                try:
                    login_btn = driver.find_element(By.ID, bid)
                    break
                except:
                    continue

            if not login_btn:
                try:
                    login_btn = driver.find_element(By.XPATH, "//button[contains(text(), 'Log In') or contains(text(), 'LOG IN')]")
                except:
                     login_btn = driver.find_element(By.XPATH, "//input[@type='submit']")

            if login_btn:
                login_btn.click()
                logging.info("Login button clicked, waiting for confirmation (up to 120s)...")
                wait(driver, 120).until(
                    lambda d: "login.cmegroup.com" not in d.current_url and "saml_login" not in d.current_url
                )
                logging.info(f"Login confirmed, current URL: {driver.current_url}")
            else:
                logging.error("Could not find login button.")

            logging.info("Waiting 10 seconds for session to settle...")
            time.sleep(10)

        logging.info(f"Navigating to {URL}")
        driver.get(URL)

        try:
            accept = wait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept.click()
            time.sleep(1)
        except:
            logging.info("Accept cookies button not found or already clicked.")

        logging.info("Searching for the correct QuikStrike iframe...")
        wait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        
        found_qs = False
        for i, frame in enumerate(iframes):
            try:
                src = frame.get_attribute("src")
                logging.info(f"Checking iframe {i}: {src}")
                driver.switch_to.frame(frame)
                time.sleep(1)
                tabs = driver.find_elements(By.CLASS_NAME, "cme-tabs")
                if tabs:
                     logging.info(f"Found cme-tabs in iframe {i}")
                     found_qs = True
                     break
                driver.switch_to.default_content()
            except Exception as e:
                logging.warning(f"Error checking iframe {i}: {e}")
                driver.switch_to.default_content()
                continue
                
        if not found_qs:
             logging.error("Could not find the QuikStrike iframe containing tabs.")
             return

        logging.info("Waiting for tabs to appear...")
        wait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "cme-tabs")))
        ul = driver.find_element(By.CLASS_NAME, "cme-tabs")
        links = ul.find_elements(By.TAG_NAME, "a")
        
        tab_titles = [a.get_attribute("title") for a in links]
        logging.info(f"Found tabs: {tab_titles}")
        
        for title in tab_titles:
            logging.info(f"Processing tab: {title}")
            try:
                ul = wait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "cme-tabs")))
                tab = ul.find_element(By.XPATH, f".//a[@title='{title}']")
                tab.click()
                time.sleep(3)
                
                download_btn = None
                for selector in ["btnExportToExcel", "btnExportToCSV", ".export-link"]:
                    try:
                        if selector.startswith("."):
                            download_btn = driver.find_element(By.CLASS_NAME, selector[1:])
                        else:
                            download_btn = driver.find_element(By.ID, selector)
                        if download_btn.is_displayed():
                            break
                    except:
                        continue
                
                if download_btn:
                    logging.info(f"Clicking download button for {title}")
                    download_btn.click()
                    time.sleep(5)
                else:
                    logging.error(f"Could not find download button for {title}")
            except Exception as e:
                logging.error(f"Error processing tab {title}: {e}")

    finally:
        logging.info("Closing driver.")
        driver.quit()


def ingest_expirations(download_dir: str, old_database: str, new_database: str, keep_files: bool = False) -> None:
    """Ingest downloaded expirations and update the database."""
    filenames = get_expirations_filenames(download_dir)
    if not filenames:
        logging.error(f"No files found in {download_dir}. Expected files matching Expirations.*.csv")
        return

    logging.info("Read prior database of expirations.")
    keyfields = ["Contract Type", "Symbol"]
    expirations = (
        petl.fromcsv(old_database) if path.exists(old_database) else petl.empty()
    )

    logging.info(f"Ingesting {len(filenames)} new files.")
    tables = [petl.fromcsv(filename) for filename in filenames]
    new_expirations = petl.cat(*tables)

    logging.info("Override old values from the original db.")
    expirations_dict = expirations.lookupone(keyfields)
    for rec in new_expirations.records():
        key = (rec["Contract Type"], rec["Symbol"])
        expirations_dict[key] = tuple(rec)
    
    # Rebuild the table with updated values.
    header = petl.header(expirations) if expirations.nrows() > 0 else petl.header(new_expirations)
    
    final_expirations = petl.wrap(
        itertools.chain([header], expirations_dict.values())
    ).sort(keyfields)

    logging.info(f"Writing updated database to {new_database}")
    final_expirations.tocsv(new_database)

    if not keep_files:
        logging.info("Cleaning up ingested files.")
        for p in filenames:
            p.unlink()
