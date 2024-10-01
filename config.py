import os
import json

# BASE_DIR'i tanımla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Telegram Bot Token
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7665315933:AAErETBqygrPP4vxCPM1hM28WOMiKdDz0yE')

# PostgreSQL Database URL
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://telegrammodbot_user:b0yP1EP75Od6OyrF3vNQOxmzEcFnlV8I@dpg-crt7ui08fa8c73ct33pg-a.frankfurt-postgres.render.com/telegrammodbot')

# Gif URL for ban message
BAN_GIF_URL = os.getenv('BAN_GIF_URL', 'https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExYTlxZGt5bGJpdWdhNHY5dDkyNDRmdGhqd2RyMnJ6bnZldDViMzJhcSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/fe4dDMD2cAU5RfEaCU/giphy.gif')

ALLOWED_GROUPS = [-1002196403922]  # Botun aktif olmasını istediğin grup ID'leri
# Load URLs and Images from JSON file
urls_path = os.path.join(BASE_DIR, 'urls.json')
with open(urls_path, 'r') as f:
    url_data = json.load(f)
    
PHOTOS = url_data['photos']
SITES = url_data['sites']
VIP = url_data['vips']
BONUSES = url_data['bonuses']
IMAGES = url_data['images']
CAPTIONS = url_data['captions']
RAFFLE_CHAT_ID = [-1002196403922]
# Flood kontrol ayarları
settings = {
    'antiflood_max_msgs': 5,           # Maksimum izin verilen mesaj sayısı
    'antiflood_seconds': 10,           # Flood kontrol için zaman aralığı (saniye)
    'timeout_duration': 60             # Flood yapan kullanıcıya verilecek timeout (saniye)
}
# Load Spam Keywords
spam_keywords_path = os.path.join(BASE_DIR, 'spam_keywords.json')
with open(spam_keywords_path, 'r') as f:
    spam_keywords_data = json.load(f)

SPAM_KEYWORDS = spam_keywords_data['keywords']
print(SPAM_KEYWORDS)
# Load Blacklist
blacklist_path = os.path.join(BASE_DIR, 'blacklist.json')
with open(blacklist_path, 'r') as f:
    blacklist_data = json.load(f)

BLACKLIST = blacklist_data.get('blacklist', [])

# Load Admin List
adminlist_path = os.path.join(BASE_DIR, 'adminlist.json')
with open(adminlist_path, 'r') as f:
    adminlist_data = json.load(f)
    

# Load Auto Messages
automesaj_path = os.path.join(BASE_DIR, 'automesaj.json')
with open(automesaj_path, 'r') as f:
    automesaj_data = json.load(f)
AUTOMESSAGES = automesaj_data['automessages']

ADMIN_DATA = adminlist_data['admins']  # Admin verilerini saklayın
ADMINS = [int(admin['user_id']) for admin in ADMIN_DATA]  # Adminlerin ID'lerini alın
ADMIN_CHAT_ID = ",".join([str(admin['user_id']) for admin in ADMIN_DATA])  # Adminlerin ID'lerini virgülle ayırarak alın
print(ADMINS)  # ADMINS listesinin doğru yüklendiğini kontrol edin
# Load Mod List
modlist_path = os.path.join(BASE_DIR, 'modlist.json')
with open(modlist_path, 'r') as f:
    modlist_data = json.load(f)

MODS = modlist_data['mods']
