from lxml import html
import requests
from time import sleep
import pandas as pd
import numpy as np


XPATH_URLS = '//a[contains(@href,"szczegoly.php?id2")]/@href'
all_locations_list = []

def make_get_request(url_):
    
    url = url_

    payload={}
    headers = {
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://www.ebib.pl/biblioteki/baza/www_typ_bibliotek.php',
    'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7,und;q=0.6,hu;q=0.5',
    'Cookie': 'PHPSESSID=aecf34ff930817143f4dcf579e1e18e2; _ga=GA1.2.1103295210.1621250148; _gid=GA1.2.609132299.1621250148'
    }


    response = requests.request("GET", url, headers=headers, data=payload)
    return response

page = make_get_request("http://www.ebib.pl/biblioteki/baza/www_typ_bibliotek.php?q=14")
tree = html.fromstring(page.content)

urls = tree.xpath(XPATH_URLS)
print("Found urls: ", len(urls))

iteration = 0

for url in urls:
    url = "http://www.ebib.pl/biblioteki/baza/" + url
    details_page = make_get_request(url)
    details_tree = html.fromstring(details_page.content)

    sleep(0.1)
    
    try:
        [title] = details_tree.xpath('//h2/text()')
    except Exception as e:
        print(e)

    try:
        [location] = details_tree.xpath('//p[contains(text(),"Położenie: ")]/text()')
    except Exception as e:
        print(e)
    
    try:
        [email] = details_tree.xpath('//p[contains(text(),"Poczta elektroniczna")]/text()')
    except Exception as e:
        print(e)

    location = location.replace("Położenie:", "")
    email = email.replace("Poczta elektroniczna:", "")

    if "@" not in email:
        email = ""
    
    all_locations_list.append([title, location, email, url])
    print(iteration,"/",len(urls)," ",title)
    iteration += 1

all_locations_nparray = np.array(all_locations_list)
df = pd.DataFrame(all_locations_nparray, columns = ['Nazwy bibliotek','Położenie','Poczta elektroniczna', 'Link'])
print(df)

df.to_excel('biblioteki_publiczne.xlsx')
