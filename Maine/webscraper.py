import requests
from bs4 import BeautifulSoup
import csv
import re
import pandas as pd

f = open('web_scraper_maine.csv', 'w')



#how to write row to csv

URL = "https://www.maine.gov/sos/cec/elec/munic.html"
page = requests.get(URL)
print(page)

writer = csv.writer(f)






soup = BeautifulSoup(page.content, "html.parser")
results = soup.find(id="awt-content-area2")
soup = soup.find_all("dl", class_="address1")

# details =  soup.find_all(attrs={'class': None})

for s in soup:
    
    # more = sou.find_all("p")
    # print("hey", more)
    
    s= s.find('p')

    
    
    



    
   


    # COMPLETE
    city = re.findall('(.*)', s.text)[6]
    city = str(re.findall('^(.+?),', city))
    city = city.split("'")[1]

    zipcode = str(re.findall('\d{5}', s.text))
    zipcode = zipcode.split("'")[1]
    address1 = str(re.findall('(\d.*)(?=(\r))', s.text)[0][0])

    phone= str(re.findall('Phone.{16}', s.text))
    phone =  str(phone.replace('Phone: ',''))
    phone = phone.split("'")[1]
    state = "ME"

    



    print(zipcode, phone)
    row = [address1, city, state, zipcode, phone]


    
    writer.writerow(row)



    # print( s)
    # print('REGEX',zipcode)

    


