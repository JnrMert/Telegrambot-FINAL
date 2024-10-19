import requests
from bs4 import BeautifulSoup
import json
import os
import random

# Web sayfasının URL'si
url = "https://kazananadam.xyz/"

# Sayfanın HTML içeriğini çekiyoruz
response = requests.get(url)
soup = BeautifulSoup(response.content, "html.parser")

# JSON dosyasının mevcut olup olmadığını kontrol edelim
if os.path.exists("urls.json"):
    with open("urls.json", "r") as json_file:
        urls_data = json.load(json_file)
else:
    urls_data = {"sites": [], "vips": []}

# Mevcut siteleri ve VIP siteleri tamamen temizleyelim
urls_data["sites"] = []
urls_data["vips"] = []

# Emojiler listesi
emojis = ["⭐", "🌟", "🔥", "🏆", "🥇", "⚜️", "°•", "𓆩🖤𓆪", "𓆰♕𓆪", "♛", "✨", "🚨", "🍁", "🎃", "🍂", "🎁", "🛒", "💸", "💰", "👑", "💥", "💣", "🚀"]

# Simetrik emoji ekleyerek başlıkları süsleyen fonksiyon
def decorate_title_with_emojis(title):
    emoji_count = random.choice([1, 2, 3])  # Rastgele 1, 2 veya 3 emoji kullan
    selected_emojis = random.sample(emojis, emoji_count)  # Rastgele emojileri seç
    decorated_title = f"{''.join(selected_emojis)} {title} {''.join(reversed(selected_emojis))}"  # Simetrik yerleşim
    return decorated_title

# sm_Container class'lı (normal siteler) elementleri bulalım
sm_containers = soup.find_all("div", class_="sm_Container")

for container in sm_containers:
    a_tag = container.find("a")
    if a_tag:
        site_name = a_tag.get("title") or "Sponsor Reklam Alanı"  # Eğer title boşsa, "Sponsor Reklam Alanı" kullan
        site_url = url + a_tag.get("href")
        
        # Başlığı süsle
        decorated_site_name = decorate_title_with_emojis(site_name)
        
        # Yeni siteyi ekleyelim
        urls_data["sites"].append({
            "name": decorated_site_name,
            "url": site_url
        })

# xs_Container class'lı (VIP siteler) elementleri bulalım
xs_containers = soup.find_all("div", class_="xs_Container")

for container in xs_containers:
    a_tag = container.find("a")
    if a_tag:
        vip_name = a_tag.get("title") or "Sponsor Reklam Alanı"  # Eğer title boşsa, "Sponsor Reklam Alanı" kullan
        vip_url = url + a_tag.get("href")
        
        # Başlığı süsle
        decorated_vip_name = decorate_title_with_emojis(vip_name)
        
        # Yeni VIP siteyi ekleyelim
        urls_data["vips"].append({
            "name": decorated_vip_name,
            "url": vip_url
        })

# Güncellenmiş veriyi geri yazalım
with open("urls.json", "w") as json_file:
    json.dump(urls_data, json_file, indent=4)

print(f"{len(sm_containers)} yeni site bilgisi eklendi.")
print(f"{len(xs_containers)} yeni VIP site bilgisi eklendi.")
