from turtle import Turtle
import requests
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd

f = open("MN_Cities.csv", "w")


# how to write row to csv

URL = "https://www.sos.state.mn.us/elections-voting/other-ways-to-vote/cities-and-towns-with-in-person-absentee-voting/"
page = requests.get(URL)
print(page)

writer = csv.writer(f)
soup = BeautifulSoup(page.content, "html.parser")

ul = soup.find_all("ul", class_="list-unstyled")
# print(ul)
# li = ul.find_all('li')
# # print(li)

for u in ul:
    print("")
    print("")
    print("")
    # print(u)
    li = u.find_all("li")
    for l in li:
        # website
        a = l.find("a")
        website = a["href"]
        a.extract()
        l = l.text.strip()

        items = l.split(",")
        zipcode = items[3].split(" ")[-1]
        row = [website, items[1], items[2], zipcode]

        print(row)
        writer.writerow(row)


quit()


soup = BeautifulSoup(page.content, "html.parser")
# results = soup.find(id="awt-content-area2")
soup = soup.find_all("dl", class_="list-unstyled")

# details =  soup.find_all(attrs={'class': None})

for s in soup:

    # more = sou.find_all("p")
    # print("hey", more)

    s = s.find("p")
    # COMPLETE
    city = re.findall("(.*)", s.text)[6]
    city = str(re.findall("^(.+?),", city))
    city = city.split("'")[1]

    zipcode = str(re.findall("\d{5}", s.text))
    zipcode = zipcode.split("'")[1]
    address1 = str(re.findall("(\d.*)(?=(\r))", s.text)[0][0])

    phone = str(re.findall("Phone.{16}", s.text))
    phone = str(phone.replace("Phone: ", ""))
    phone = phone.split("'")[1]
    state = "ME"

    print(zipcode, phone)
    row = [address1, city, state, zipcode, phone]

    writer.writerow(row)

    # print( s)
    # print('REGEX',zipcode)
