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
    
    options.set_preference("browser.download.folderList", 2)  # custom location
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

def main():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    driver = load_driver()
    wait = WebDriverWait(driver, 20)

    try:
        driver.get("https://cfpub.epa.gov/ghgdata/inventoryexplorer/#allsectors/allsectors/allgas/gas/all")
        dismiss_popup(driver)
        time.sleep(5)

        # Select the Geography dropdown by its correct ID
        select_element = wait.until(EC.presence_of_element_located((By.ID, "geographytype")))
        select = Select(select_element)

        for i in range(len(select.options)):
            option_text = select.options[i].text.strip().replace(" ", "_")
            print(f"Downloading for: {option_text}")
            select.select_by_index(i)
            time.sleep(3)

            # Click the download button, using a the CSS selector that targets it.
            download_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.export"))
            )
            download_btn.click()

            # Wait for the file to appear (polling for up to ~15 seconds)
            csv_path = os.path.join(DOWNLOAD_DIR, "data.csv")
            for _ in range(30):
                if os.path.exists(csv_path):
                    break
                time.sleep(0.5)
            else:
                print(f"Download timed out for {option_text}")
                continue

            # Once downloaded, rename the file to append the state name.
            renamed_path = os.path.join(DOWNLOAD_DIR, f"data_{option_text}.csv")
            shutil.move(csv_path, renamed_path)
            print(f"Saved: {renamed_path}")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
