from selenium import webdriver
from selenium.webdriver import Remote, ChromeOptions  
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection 
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os


def get_local_driver():
    # Get the chromedriver version that corresponds with your google chrome browser version.
    service = Service(executable_path="chromedriver.exe")
    driver = webdriver.Chrome(service=service)
    return driver


def get_top_20_nigeria_food_content_creators() -> None:
    driver = get_local_driver()
    driver.get('https://videos.feedspot.com/nigeria_food_youtube_channels/')
    try:
        WebDriverWait(
            driver, 
            20  # seconds
                    ).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ext"))
        )
    except TimeoutException:
        print("could not find youtuber title")
    youtuber_name_elements = driver.find_elements(By.CLASS_NAME, 'tlink.fd_lk')
    youtube_channel_elements = driver.find_elements(By.CLASS_NAME, 'ext')
    with open('top_20_nigerian_food_content_creators.txt', 'w', encoding='utf-8') as file:
        for name_element, channel_element in zip(
                youtuber_name_elements, youtube_channel_elements
                ):
            file.write(f"{name_element.text},{channel_element.get_attribute('href')}\n")


def main()-> None:
    get_top_20_nigeria_food_content_creators()

if __name__ == "__main__":
    main()
