import requests
import re
from bs4 import BeautifulSoup

URL = 'https://www.paris.cl/bicicleta-mtb-giant-talon-1-black-m-aro-29-573151.html?dwvar_573151_color=0002&cgid=dprBclMountainBike#pmax=1%2C000%2C000.00&prefn1=deportesAroBicicleta&prefn2=size&srule=price-high-to-low&pmin=500%2C000.00&prefv1=29%22&prefv2=M&start=1'
headers = {
    "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'}
page = requests.get(URL, headers=headers)

soup = BeautifulSoup(page.content, 'html.parser')

# print(soup.prettify())

titulo = soup.find_all("span", class_="visually-hidden")
precio = soup.find("div", class_="item-price offer-price price-tc default-price")

otro = re.findall("[0-9]+.+", str(precio))
otro = otro[0].replace(".", "")

#(\d+).html

print(otro)

print(titulo)
print(precio)
