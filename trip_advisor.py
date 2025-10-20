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
# Get the values of each column.
xl_addresses_1 = xl_df["Address Line 1"].values
xl_addresses_city = xl_df["City"].values
xl_addresses_state = xl_df["State/Province"].values
xl_addresses_post = xl_df["Postal Code"].values
xl_addresses_country = xl_df["Country"].values

xl_addresses = []

# Join each line and separate with comma to create full address line for each location.
for add_1, city, state, post, country in zip(
    xl_addresses_1, xl_addresses_city, xl_addresses_state, xl_addresses_post, xl_addresses_country):
    join_all = ", ".join([str(add_1),str(city),str(state),str(post),str(country)])

    xl_addresses.append(join_all)

# Create a dict to hold location reviews data.
location_reviews_data = {}

# Create lists to collect listing name, Bing Maps Address, Rating, Review Count.
listing_names = []
bing_addresses = []
ratings = []
review_counts = []

service = Service(executable_path="/Users/arvinvega/PycharmProjects/The Great Pizza Divide/chromedriver")
driver = webdriver.Chrome(service=service)

for address in xl_addresses:
    driver.get("https://www.bing.com/maps/search")
    time.sleep(2)

    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "maps_sb"))
        )
        input_element = driver.find_element(By.ID, "maps_sb")
        search_button_element = driver.find_element(By.CLASS_NAME, "searchIcon")
    except TimeoutException:
        # If Bing Maps redirects, elements are under different identifiers.
        input_element = driver.find_element(By.ID, "searchBoxInput")
        search_button_element = driver.find_element(
            By.CSS_SELECTOR, "button[class='roundedShape_t4d4o mediumSize_nLnBq transparentAppearance_SAZbb normalFont_cSriT button_OdmHt searchButton_WjLH9']")
    input_element.clear()
    input_element.send_keys(f"pizza hut {address}")
    search_button_element.click()

    # Get listing name.
    no_listing = False
    try:
        try:
            WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "h2[class='nameContainer']"))
                )

            location_name = driver.find_elements(By.CSS_SELECTOR, "h2[class='nameContainer']")
            for l in location_name:
                l_name = l.text
                # The element has other strings associated, so for simplicity's sake, just
                # make the listing name Pizza Hut.
                if "Pizza Hut" in l_name:
                    listing_name = "Pizza Hut" # we need this variable to filter later.
                    listing_names.append(listing_name)
                else:
                    # If Pizza Hut is not in the listing name, it is not a Pizza Hut
                    # listing.
                    listing_name = "N/A. NOT A PIZZA HUT LISTING!!"
                    listing_names.append(listing_name)
                print(listing_name)

        except TimeoutException:
            # If redirect occurs, use the different element name for metric.
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span[class='eh_title_container']"))
            )
            location_name = driver.find_elements(By.CSS_SELECTOR, "span[class='eh_title_container']")
            for l in location_name:
                l_name = l.text
                if "Pizza Hut" in l_name:
                    listing_name = "Pizza Hut"
                    listing_names.append(listing_name)
                else:
                    listing_name = "N/A. NOT A PIZZA HUT LISTING!"
                    listing_names.append(listing_name)
                print(listing_name)
    except TimeoutException:
        no_listing = True

    if no_listing == True:
        listing_names.append("N/A. Listing does not exist.")
        print("N/A. Listing does not exist.")

    # Get address.
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='iconDataList']"))
        )
        a_list = driver.find_elements(By.CSS_SELECTOR, "div[class='iconDataList']")
        # Check if At: ... is being used before the address.
        if len(a_list) > 2:
            # address is 2nd element.
            bing_address = a_list[1].text
            bing_addresses.append(bing_address)
        else:
            bing_address = a_list[0].text
            bing_addresses.append(bing_address)
        print(bing_address)
    except TimeoutException:
        bing_addresses.append("N/A")
        print("Bing Listing Address does not exist.")

    # Set default flag for no review sources to false.
    no_rs = False
    # Check if Tripadvisor review source exists.
    try:
        # First, check if review sources exist at all. 
        try:     
            WebDriverWait(driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='acc_mrev_p']"))
                )
        except TimeoutException:
            # No review sources exist. Update no_rs flag.
            no_rs = True
            print("No review sources.")

        review_sources = driver.find_elements(By.CSS_SELECTOR, "div[class='acc_mrev_p']")
    except TimeoutException:
        no_rs = False
        # If redirect occurs, use the different element name for metric.
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='acc_mrev_pfr']"))
            )
        review_sources = driver.find_elements(By.CSS_SELECTOR, "div[class='acc_mrev_p']")
    except TimeoutException:
        no_rs = False
        # US has different element.
        WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='acc_mrev_header']"))
            )
        review_sources = driver.find_elements(By.CSS_SELECTOR, "div[class='acc_mrev_p']") 

    
    rs_list = []
    if no_rs:
        rs_list.append("N/A")
    else:
        for rs in review_sources:
            rs_text = rs.text
            rs_list.append(rs_text)

    # Tripadvisor is always first element.
    check_ta = rs_list[0]

    # Check if Tripadvisor is in first element and if listing name is Pizza
    # Hut.
    if "Tripadvisor" in check_ta and listing_name == "Pizza Hut":
        # Get rating.
        rating_raw = driver.find_element(By.CSS_SELECTOR, "div[class='l_rev_rs']").text
        # Extract only the rating. Remove the /5.
        rating_final = rating_raw.replace("/5", "")
        ratings.append(float(rating_final))
        print(f"Rating: {rating_final}")

        # Get review count.
        review_count_raw = driver.find_element(By.XPATH, "//a[text()[contains(.,'(')]]").text
        # Remove parentheses.
        review_count_final = review_count_raw.replace("(", "").replace(")", "").replace(" review", "").replace("s", "")
        review_counts.append(int(review_count_final))
        print(f"Review Count: {review_count_final}")
    else:
        # No Tripadvisor data.
        ratings.append("N/A")
        review_counts.append("N/A")
        print("N/A. No Tripadvisor data.")
        print("N/A. No Tripadvisor data.")



# Create all necessary keys and values.
location_reviews_data["Listing Name"] = listing_names
location_reviews_data["Bing Address_1"] = bing_addresses
location_reviews_data["Rating"] = ratings
location_reviews_data["Review_count"] = review_counts

df =pd.DataFrame({'Listing Name': [x for x in location_reviews_data.get("Listing Name")],
                  'File Address_1': [address for address in xl_addresses],
                  'Bing Address_1': [x for x in location_reviews_data.get("Bing Address_1")],
                  'Rating': [x for x in location_reviews_data.get("Rating")],
                  'Review_count': [x for x in location_reviews_data.get("Review_count")],})

df.to_excel("tripadvisor_data.xlsx", index=False)

driver.quit()

