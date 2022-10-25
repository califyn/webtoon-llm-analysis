from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import requests
from bisect import bisect

import subprocess

import traceback

from pathlib import Path

from time import sleep
import glob

'''
    dl.py:
        Scrapes webtoons from webtoon site, places into directories.
        First DAY_NUMBER eps of each day's webtoons on the homepage as well as DAY_NUMBER top completed webtoons.
        The first EP_NUMBER of episodes are downloaded.
        Sometimes messes up for unknown reasons, re-run in that case (it will not redo ones it's already done).
        Cannot handle the adult content warning.
'''

DAY_NUMBER = 10
EP_NUMBER = 10

driver = webdriver.Chrome()

try:
    # Find webtoons
    driver.get("https://www.webtoons.com/en/dailySchedule")
    daily_container = driver.find_elements(By.CLASS_NAME, "daily_card")
    toons = [[w for w in day.find_elements(By.XPATH, "*")] for day in daily_container]
    toons = [t[:DAY_NUMBER] for t in toons]
    toons = sum(toons, [])

    toons = [ {
        "title": toon.find_element(By.CLASS_NAME, "subj").get_attribute('innerText'),
        "genre": toon.find_element(By.CLASS_NAME, "genre").get_attribute('innerText'),
        "link": toon.find_element(By.XPATH, "*").get_attribute("href"), 
    } for toon in toons]
    driver.maximize_window()

    # Download each webtoon
    for toon in toons:
        try:
            folder_path = "./" + toon["title"].replace(" ", "_")
            Path(folder_path).mkdir(parents=True, exist_ok=True)

            with open(folder_path + "/info.txt", "w") as f:
                f.write(f"Title\t{toon['title']}\n")
                f.write(f"Genre\t{toon['genre']}")
            continue

            last_folder = Path(folder_path + "/ep-" + str(EP_NUMBER))
            if last_folder.exists() and sum(1 for _ in last_folder.glob("obj-*.*")) > 0:
                continue

            driver.get(toon["link"])
            driver.find_element(By.ID, "_btnEpisode").click()
            sleep(4)

            ep_index = 1
            for i in range(EP_NUMBER):
                img_folder_path = folder_path + "/ep-" + str(ep_index) + "/imgs"
                Path(img_folder_path).mkdir(parents=True, exist_ok=True)

                sleep(1.5)
                files = {}

                # Get requests
                for request in driver.requests:
                    if request.response:
                        files[request.url] = request.response.body

                # Download images/gifs
                img_container = driver.find_element(By.ID, "_imageList")
                imgs = img_container.find_elements(By.XPATH, "*")

                for idx, img in enumerate(imgs):
                    src = img.get_attribute('src')
                    img_path = img_folder_path + "/obj-" + str(idx)
                    
                    if ".jpg" in src.lower():
                        img_path = img_path + ".jpg"
                    elif ".gif" in src.lower():
                        img_path = img_path + ".gif"
                    elif ".png" in src.lower():
                        img_path = img_path + ".png"
                    else:
                        input(f"cannot recognize file format of {src}!")

                    with open(img_path, 'wb') as f:
                        f.write(files[src])

                print(f"Continuing to episode {ep_index + 1}")
                imgs[0].click()
                driver.find_element(By.XPATH, '//*[@title="Next Episode"]').click()
                ep_index += 1
        except Exception:
            print(traceback.format_exc())
            pass
        finally:
            print(f"Finished webtoon: {toon['title']}")
finally:
    driver.quit()
