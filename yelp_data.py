import requests
from not_the_api_token import not_the_api_token

import pandas as pd
import string

# Read in the excel file.
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

# We need to find if addresses start with a pound sign.
for string in xl_addresses:
    if string[0] == '#':
        # retrieve the current index number of this element.
        str_index = xl_addresses.index(string)
        # update the element to remove only the leading pound sign.
        updated_string = string.replace('#', '', 1)
        # remove the old element and insert in its place the updated element.
        xl_addresses.insert(str_index, updated_string)
        xl_addresses.remove(string)
    # check for & and replace with 'and'.
    if '&' in string:
        str_index = xl_addresses.index(string)
        updated_string = string.replace('&', 'and', 1)
        xl_addresses.insert(str_index, updated_string)
        xl_addresses.remove(string)

# Create a dict to hold location reviews data.
location_reviews_data = {}

# Create lists to collect business name, address, rating, review_count, coords.
names = []
file_addresses = []
yelp_addresses = []
ratings = []
review_counts = []
lat_lngs = []

for xl_address in xl_addresses:
    url = f"https://api.yelp.com/v3/businesses/search?location={xl_address}&term=pizza%20hut&radius=1000&sort_by=best_match&limit=1"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {not_the_api_token}"
    }

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        print(f"Status: {r.status_code} (Success!)")
    else:
        print(f"API Call Failed! Status Code: {r.status_code}.")
        exit()

    biz_dict = r.json()

    biz_data = biz_dict['businesses'][0]
    print(biz_data)

    name = biz_dict['businesses'][0]['name']
    address = biz_dict['businesses'][0]['location']['display_address']
    rating = biz_dict['businesses'][0]['rating']
    review_count = biz_dict['businesses'][0]['review_count']
    lat = biz_dict['businesses'][0]['coordinates']['latitude']
    lng = biz_dict['businesses'][0]['coordinates']['longitude']
    lat_lng = f"{lat},{lng}"

    print(name)
    print(address)
    print(rating)
    print(review_count)
    print(lat_lng)

    names.append(name)
    file_addresses.append(xl_address)
    yelp_addresses.append(address)
    ratings.append(rating)
    review_counts.append(review_count)
    lat_lngs.append(lat_lng)

# Create all necessary keys and values.
location_reviews_data["Location_name"] = names
location_reviews_data["File_addresses"] = xl_addresses
location_reviews_data["Yelp_address"] = yelp_addresses
location_reviews_data["Rating"] = ratings
location_reviews_data["Review_count"] = review_counts
location_reviews_data["Coordinates"] = lat_lngs

df =pd.DataFrame({'Location Name': [x for x in location_reviews_data.get("Location_name")],
                  'File Address': [x for x in location_reviews_data.get("File_addresses")],
                  'Yelp Address': [x for x in location_reviews_data.get("Yelp_address")],
                  'Rating': [x for x in location_reviews_data.get("Rating")],
                  'Review Count': [x for x in location_reviews_data.get("Review_count")],
                  'Coordinates': [x for x in location_reviews_data.get("Coordinates")],
                  })

df.to_excel("yelp_output.xlsx", index=False)
