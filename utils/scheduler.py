import subprocess
import sys
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from commands.db_management import reset_warnings  # reset_warnings fonksiyonunu içe aktar


# Site güncelleme işlemi (sadece program başında çalışacak)
def run_sites_update():
    subprocess.Popen([sys.executable, "sitesUpdate.py"])


# Botu yeniden başlatma işlemi
def restart_bot():
    print("Bot yeniden başlatılıyor...")
    time.sleep(2)
    os.execv(sys.executable, [sys.executable] + sys.argv)  # Botu yeniden başlat


def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.utc)

    try:
        # 24 saatte bir reset_warnings çalıştırma
        scheduler.add_job(reset_warnings, trigger=IntervalTrigger(hours=24, timezone=pytz.utc))

        # Zamanlayıcıyı başlat
        scheduler.start()
    except Exception as e:
        pass


if __name__ == '__main__':
    # İlk olarak sitesUpdate.py'yi çalıştırma
    run_sites_update()

    # Zamanlayıcıyı kur
    setup_scheduler()

    # 24 saat sonra botu yeniden başlatmak için zamanlayıcı veya manuel tetikleme eklenebilir
    print("Bot çalışıyor...")

    # Botunuzu burada çalıştırabilirsiniz, örneğin:
    # updater.start_polling()
    # updater.idle()

    # 24 saatte bir botu manuel olarak yeniden başlatmak için zamanlayıcı kullanabilirsiniz
    time.sleep(24 * 3600)
    restart_bot()
