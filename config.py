import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7665315933:AAErETBqygrPP4vxCPM1hM28WOMiKdDz0yE')

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://telegrammodbot_user:b0yP1EP75Od6OyrF3vNQOxmzEcFnlV8I@dpg-crt7ui08fa8c73ct33pg-a.frankfurt-postgres.render.com/telegrammodbot')

BAN_GIF_URL = os.getenv('BAN_GIF_URL', 'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTlxZGt5bGJpdWdhNHY5dDkyNDRmdGhqd2RyMnJ6bnZldDViMzJhcSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fe4dDMD2cAU5RfEaCU/giphy.gif')

ALLOWED_GROUPS = [-1002196403922, -1002458297138, -1001150697718]  
urls_path = os.path.join(BASE_DIR, 'urls.json')
with open(urls_path, 'r') as f:
    url_data = json.load(f)
    
PHOTOS = url_data['photos']
SITES = url_data['sites']
VIP = url_data['vips']
BONUSES = url_data['bonuses']
IMAGES = url_data['images']
CAPTIONS = url_data['captions']



# Flood kontrol ayarları
settings = {
    'antiflood_max_msgs': 5,           
    'antiflood_seconds': 10,           
    'timeout_duration': 60             
}


def load_sponsor_data():
    with open('sponsors.json', 'r', encoding='utf-8') as f:
        return json.load(f)
spam_keywords_path = os.path.join(BASE_DIR, 'spam_keywords.json')



with open(spam_keywords_path, 'r') as f:
    spam_keywords_data = json.load(f)
SPAM_KEYWORDS = spam_keywords_data['keywords']


blacklist_path = os.path.join(BASE_DIR, 'blacklist.json')
with open(blacklist_path, 'r') as f:
    blacklist_data = json.load(f)

BLACKLIST = blacklist_data.get('blacklist', [])

adminlist_path = os.path.join(BASE_DIR, 'adminlist.json')
with open(adminlist_path, 'r') as f:
    adminlist_data = json.load(f)
    

ADMIN_DATA = adminlist_data['admins']  # Admin verilerini saklayın
ADMINS = [int(admin['user_id']) for admin in ADMIN_DATA]  # Adminlerin ID'lerini alın
ADMIN_CHAT_ID = ",".join([str(admin['user_id']) for admin in ADMIN_DATA])  # Adminlerin ID'lerini virgülle ayırarak alın
