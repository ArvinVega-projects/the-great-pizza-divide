from bs4 import BeautifulSoup

import requests
import fnmatch
import pandas as pd
import string

# This is used for the US website, the Canadian website is structured
# differently..
url = 'https://locations.pizzahut.com/ny/new-york'
page = requests.get(url)

# Extract html data using BeautifulSoup.
soup = BeautifulSoup(page.text, features='html.parser')

# Create a list to add addresses.
address_list = []
# Addresses can be found in div class='address-line'.
addresses = soup.find_all('div', class_ = 'address-line')


for address in addresses:
    # Remove leading and trailing white space from address text.
    clean_add = address.text.strip()
    address_list.append(clean_add)


# Some elements are empty strings, let's remove them from the list.
# Use list comprehension to keep elements that result in True for strip().
remove_empty = [x for x in address_list if x.strip()]
address_list = remove_empty


# Separate city name, post code so that we just get the address line 1.
# We'll add these to a variable so we can append them to the file separately.
cities_postcodes = fnmatch.filter(address_list, 'New York, NY*')

# Now we remove city names, post codes from the main address_list.
for address in address_list:
    for city_postcode in cities_postcodes:
        if city_postcode in address:
            address_list.remove(address)

# this removes address line two since this is usually a center name and doesn't
# start with a number.
for string in address_list:
     if not string[0].isdigit():
        address_list.remove(string)


# If the length of addresses and cities_postcodes do not match, there was an
# error in filtering data. Exit the program if this happens.
if len(address_list) != len(cities_postcodes):
    print("STOP! Spot check data as the data does not align!")
    exit()


# Set column names for our dataframe.
d_column_names = ["Address Line 1", "City and Post Code"]
df = pd.DataFrame(columns=d_column_names)

# Add onto our data frame of the location data we just extracted.
for address, city_postcode in zip(address_list, cities_postcodes):
    df.loc[len(df)] = [address, city_postcode]

# Read in the excel file and assign it to a different dataframe.
xl_data = pd.read_excel('us_addresses.xlsx')
xl_df = pd.DataFrame(xl_data)

# Concatenate the current data extraction with the excel data.
df_merged = pd.concat([df, xl_df], ignore_index=True)
# Save the updated data to the excel file.
df_merged.to_excel("us_addresses.xlsx")
