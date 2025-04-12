import os
import time
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from dotenv import load_dotenv

DOWNLOAD_DIR = os.path.join(os.getcwd(), "data")

def load_driver() -> WebDriver:
    load_dotenv()
    driver_location = os.getenv("DRIVER_LOCATION")
    options = Options()
    options.headless = True

    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.dir", DOWNLOAD_DIR)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "text/csv,application/csv,application/octet-stream")
    options.set_preference("pdfjs.disabled", True)

    service = Service(driver_location)
    return webdriver.Firefox(service=service, options=options)

def dismiss_popup(driver: WebDriver):
    try:
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.ui-button"))
        ).click()
        print("Popup dismissed via OK button.")
    except Exception as e:
        print(f"No popup to dismiss or already handled: {e}")

def wait_for_download_complete(timeout: int = 30) -> bool:
    csv_path = os.path.join(DOWNLOAD_DIR, "data.csv")
    part_path = csv_path + ".part"
    start_time = time.time()

    while time.time() - start_time < timeout:
        if os.path.exists(csv_path) and not os.path.exists(part_path):
            return True
        time.sleep(0.5)
    return False

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    driver = load_driver()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://cfpub.epa.gov/ghgdata/inventoryexplorer/#allsectors/allsectors/allgas/gas/all")
        dismiss_popup(driver)
        time.sleep(5)

        select_element = wait.until(EC.presence_of_element_located((By.ID, "geographytype")))
        select = Select(select_element)

        for i in range(len(select.options)):
            option_text = select.options[i].text.strip().replace(" ", "_")
            print(f"Downloading for: {option_text}")
            select.select_by_index(i)
            time.sleep(3)

            # Clear previous download if it still exists (precaution)
            existing = os.path.join(DOWNLOAD_DIR, "data.csv")
            if os.path.exists(existing):
                os.remove(existing)

            # Trigger download
            download_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.export"))
            )
            download_btn.click()

            time.sleep(20)

            if wait_for_download_complete():
                renamed_path = os.path.join(DOWNLOAD_DIR, f"data_{option_text}.csv")
                shutil.move(os.path.join(DOWNLOAD_DIR, "data.csv"), renamed_path)
                print(f"Saved: {renamed_path}")
            else:
                print(f"Download timed out for {option_text}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
