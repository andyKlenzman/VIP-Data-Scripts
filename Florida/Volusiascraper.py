from turtle import Turtle
import requests
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd

# initalization
f = open("fl_volusia.csv", "w")
URL = "https://www.voterfocus.com/PrecinctFinder/precinctDirectory?county=FL-VOL"

page = requests.get(URL)
writer = csv.writer(f)
soup = BeautifulSoup(page.content, "html.parser")

# print(soup)

div = soup.find("div" , {'class': 'PrecinctSummaries'})
# print(div)
addresses = div.find_all("div" , {"class": "NameAndAddress"})
titles = div.find_all("h2")
# print(titles)
# print(titles)

for title in titles:
    data = title.find("span")
    writer.writerow([data.text])


for address in addresses:
    info = address.find("a")
    info = info.text.splitlines()
    info[1] = info[1].replace("\t", "").split(", ")
    info[1][1] = info[1][1].replace("\t", "").split(" ")
    
    

    address1 = info[0]
    city = info[1][0]
    zipcode = info[1][1][1]


    name = address.find("div" , {"class": "Name"})
    # name = 
    # name = name.text
    name = name.text.replace('\t','').replace('\n', '').replace('\r', '')
    row = [name, address1, city, zipcode ]
    # print(row)
    writer.writerow(row)

    
    # print(info)
# # grab location names, addresses wy county
# spans = soup.find_all("span", class_= "accordion-item__title")
# for span in spans:
#     location = span.text.strip()
#     name_address = location.split(" | ")
#     name = name_address[0]
#     address = name_address[1]
#     address_details = address.split(",")
#     street_address = address_details[0]
#     city = address_details[1]
#     row = [name, street_address, city]
#     writer.writerow(row)

# f = open("ks_wyandotte_hours.csv", "w")
# writer = csv.writer(f)

# # grab hours and dates wy county
# hours = div.find_all('p')
# for h in hours :
#     row = h
#     writer.writerow(row)
    


# #grab name and location for sedg. county
# URL = "https://www.sedgwickcounty.org/elections/registration-and-voting/early-voting/"
# page = requests.get(URL)
# soup = BeautifulSoup(page.content, "html.parser")
# f = open("ks_sedg_locations.csv", "w")
# page = requests.get(URL)
# writer = csv.writer(f)

# trs = soup.find_all("tr")
# # delete unneeded data

# del trs[0:2]
# del trs[1]

# # quit()
# for tr in trs:
#     details = tr.find_all("p")
#     name = details[0].text
#     address = details[1].text.split(',')
#     street_address = address[0]
#     city = address[1]
#     state_zip= address[2]
#     state_zip = state_zip.split(" ")
#     zipcode = state_zip[-1]
#     row = [name, street_address, city, zipcode]
#     writer.writerow(row)

# print("Complete :)")