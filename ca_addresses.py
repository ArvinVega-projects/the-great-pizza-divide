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
input_element.send_keys("edmonton")
print("working up to here.")

# We need to wait for website to load fully as the element we want to find is
# dependent on what we type in.
# We use XPATH to find text containing our city name, province abbrev.
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.XPATH, "//*[text()[contains(.,'Edmonton, AB')]]"))
)
print("working up to here x2.")

# Now we can add all elements to a list.
address_extracts = driver.find_elements(By.XPATH, "//*[text()[contains(.,'Edmonton, AB')]]")
print("working up to here x3.")

# Convert each address in the extract to a text and add to our addresses list.
for address in address_extracts:
    address_text = address.text
    addresses.append(address_text)
time.sleep(5)
print("working up to here x3.")


# Set our column header names.
column_headers = ["Address Line 1", "City", "Province", "Postal Code"]
df = pd.DataFrame(columns=column_headers)

# Address information can be separated by commas.
split_strings = [address.split(',') for address in addresses]

# Add each data point of what we just split into their respective columns.
for split in split_strings:
    # Some addresses have unit numbers on separate address lines.
    # Combine element 0 and 1 to create address line 1.
    if len(split) > 4:
        add_1 = split[0] + split[1]
        city = split[2]
        province = split[3]
        postal_code = split[4]
    else:
        add_1 = split[0]
        city = split[1]
        province = split[2]
        postal_code = split[3]

    df.loc[len(df)] = [add_1, city, province, postal_code]



# Read in the excel file and assign it to a different dataframe.
xl_data = pd.read_excel('ca_addresses.xlsx')
xl_df = pd.DataFrame(xl_data)

# Concatenate the current data extraction with the excel data.
df_merged = pd.concat([df, xl_df], ignore_index=True)
# Save the updated data to the excel file.
df_merged.to_excel("ca_addresses.xlsx")

print(df_merged)

driver.quit()