import requests
from bs4 import BeautifulSoup
import json
import os

# Web sayfasının URL'si
url = "https://kazananadam.site/"

# Sayfanın HTML içeriğini çekiyoruz
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# JSON dosyasının mevcut olup olmadığını kontrol edelim
if os.path.exists("urls.json"):
    # Mevcut JSON dosyasını okuyalım
    with open("urls.json", "r") as json_file:
        urls_data = json.load(json_file)
else:
    # Eğer dosya yoksa, yeni bir yapı başlatıyoruz
    urls_data = {"sites": [], "vips": []}

# Mevcut siteleri ve VIP siteleri tamamen temizleyelim
urls_data["sites"] = []
urls_data["vips"] = []

# sm_Container class'lı (normal siteler) elementleri bulalım
sm_containers = soup.find_all("div", class_="sm_Container")

for container in sm_containers:
    # <a> etiketindeki href (url) ve title (site adı) değerlerini alalım
    a_tag = container.find("a")
    if a_tag:
        site_name = a_tag.get("title")
        site_url = url + a_tag.get("href")
        
        # Yeni siteyi ekleyelim
        urls_data["sites"].append({
            "name": site_name,
            "url": site_url
        })

# xs_Container class'lı (VIP siteler) elementleri bulalım
xs_containers = soup.find_all("div", class_="xs_Container")

for container in xs_containers:
    # <a> etiketindeki href (url) ve title (VIP site adı) değerlerini alalım
    a_tag = container.find("a")
    if a_tag:
        vip_name = a_tag.get("title")
        vip_url = url + a_tag.get("href")
        
        # Yeni VIP siteyi ekleyelim
        urls_data["vips"].append({
            "name": vip_name,
            "url": vip_url
        })

# Güncellenmiş veriyi geri yazalım
with open("urls.json", "w") as json_file:
    json.dump(urls_data, json_file, indent=4)

print(f"{len(sm_containers)} yeni site bilgisi eklendi.")
print(f"{len(xs_containers)} yeni VIP site bilgisi eklendi.")
