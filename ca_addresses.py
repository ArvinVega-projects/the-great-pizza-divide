from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import time

addresses = []

# https://sites.google.com/chromium.org/driver/
service = Service(executable_path="/Users/arvinvega/PycharmProjects/The Great Pizza Divide/chromedriver")
driver = webdriver.Chrome(service=service)

driver.get("https://www.pizzahut.ca/huts")
# Website needs time to load elements. Wait 5 seconds.
time.sleep(5)

# Input city name in search box element.
# Locate search box element by ID.
input_element = driver.find_element(By.ID, ":r2:")
# Type in city name in search box.
input_element.send_keys("toronto")
print("working up to here.")

# We need to wait for website to load fully as the element we want to find is
# dependent on what we type in.
# We use XPATH to find text containing our city name, province abbrev.
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[text()[contains(.,'Toronto, ON')]]"))
)
print("working up to here x2.")

# Now we can add all elements to a list.
address_extracts = driver.find_elements(By.XPATH, "//*[text()[contains(.,'Toronto, ON')]]")
print("working up to here x3.")

# Convert each address in the extract to a text and add to our addresses list.
for address in address_extracts:
    address_text = address.text
    addresses.append(address_text)
time.sleep(5)
print("working up to here x3.")


split_strings = [address.split(',') for address in addresses]
column_headers = ["Address Line 1", "City", "Province", "Postal Code"]
df = pd.DataFrame(split_strings, columns=column_headers)
df.to_excel("ca_addresses.xlsx")
driver.quit()