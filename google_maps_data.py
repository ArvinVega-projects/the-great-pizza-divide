from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException

import pandas as pd
import time


# Read in the excel file and append each address_1 to addresses list.
xl_data = pd.read_excel('addresses_final_v3.xlsx')
xl_df = pd.DataFrame(xl_data)
# Get the values of address line 1 column.
addresses = xl_df["Address Line 1"].values

# Create a dict to hold location reviews data.
location_reviews_data = {}

# Create lists to collect Google URL, Google Address, Rating, Review Count.
map_urls = []
gmaps_addresses = []
ratings = []
review_counts = []

# https://sites.google.com/chromium.org/driver/
service = Service(executable_path="/Users/arvinvega/PycharmProjects/The Great Pizza Divide/chromedriver")
driver = webdriver.Chrome(service=service)

driver.get("https://google.com/maps")
# Website needs time to load elements. Wait 5 seconds.
time.sleep(5)

def search_listing(address):
    """Search the address for the Google listing and collect URL."""
    # Locate search box element by ID.
    # Input (pizza hut + address_1) in search box element.
    # The "\n" is syntax to mimic hitting enter key.
    input_element = driver.find_element(By.ID, "searchboxinput")
    # Clear previous entry.
    input_element.clear()
    input_element.send_keys("pizza hut " + f"{address}" + "\n")
    # Website needs time to load elements. Wait 5 seconds.
    time.sleep(5)

    # Retrieve Google Maps url so that we can extract lat/lng from this.
    maps_url = driver.current_url
    map_urls.append(maps_url)
    

    # Wait for address line element to appear.
    # Assign to variable to cross reference with the file address.
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='Io6YTe fontBodyMedium kR99db fdkmkc ']"))
        )
        gmaps_address = driver.find_element(By.CSS_SELECTOR, "div[class='Io6YTe fontBodyMedium kR99db fdkmkc ']").text
        gmaps_addresses.append(gmaps_address)
    except TimeoutException:
        # if the listing doesn't exist, fill in address as the file address.
        print(f"The Google listing for {address} could not be found.")
        gmaps_address = address
        gmaps_addresses.append(gmaps_address)
        

def get_rating_review(address):
    """Collect the rating and review count."""
    try:
        # Wait for rating class element to appear. Then assign it to variable and update
        # type to float.
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "fontDisplayLarge"))
        )
        rating_raw = driver.find_element(By.CLASS_NAME, "fontDisplayLarge").text
        print(rating_raw)
        ratings.append(float(rating_raw))

        # Wait for review count element to appear. Then assign it to variable.
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, "//span[text()[contains(.,'review')]]"))
        )
        review_count_raw = driver.find_element(By.XPATH, "//span[text()[contains(.,'review')]]").text
        # Remove thousands separator if it exists to update value to int.
        if "," in review_count_raw:
            review_count = review_count_raw.replace(",", "")
            review_count = review_count.replace(" reviews", "")
        else:
            review_count = review_count_raw.replace(" reviews", "")

        # Applying the int will get us ValueError if there is one.
        review_counts.append(int(review_count))

        # If we get a ValueError, it's because this listing has Q&A which is
        # also in a span tag and precedes the review_count on a listing.
        # Need to skip the Q&A element to retrieve review_count.

    except ValueError:
        print(f"This listing: {address} triggered ValueError.")
        # Check first if it's because there's only 1 review.
        if review_count_raw == "1 review":
            review_count = 1
            
        # Create a list to hold all elements that contain 'reviews' so that we
        # can make each element text.
        else:
            r_list = []
            # Note that we are finding all elements where span contains 'reviews'.
            review_count_raw = driver.find_elements(By.XPATH, "//span[text()[contains(.,'reviews')]]")
            for r in review_count_raw:
                r_text = r.text
                r_list.append(r_text)
            # The review_count is index 1.
            review_count_raw = r_list[1]
            # # Remove thousands separator if it exists to update value to int.
            if "," in review_count_raw:
                review_count = review_count_raw.replace(",", "")
                review_count = review_count.replace(" reviews", "")
            else:
                review_count = review_count_raw.replace(" reviews", "")


        review_counts.append(int(review_count))

    except TimeoutException:
        # if the listing doesn't exist, fill in data as N/A.
        rating_raw = "N/A"
        review_count = "N/A"
        ratings.append(rating_raw)
        review_counts.append(review_count)

    print(review_count)
            

for address in addresses:
    search_listing(address)
    get_rating_review(address)


# Create all necessary keys and values.
location_reviews_data["Address_1"] = gmaps_addresses
location_reviews_data["Rating"] = ratings
location_reviews_data["Review_count"] = review_counts
location_reviews_data["Gmaps_URL"] = map_urls


df =pd.DataFrame({'Address': [x for x in location_reviews_data.get("Address_1")],
                  'Rating': [x for x in location_reviews_data.get("Rating")],
                  'Review Count': [x for x in location_reviews_data.get("Review_count")],
                  'Google Maps URL': [x for x in location_reviews_data.get("Gmaps_URL")],})

df.to_excel("google_maps_data.xlsx", index=False)


driver.quit()