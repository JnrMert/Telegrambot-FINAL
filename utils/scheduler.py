import logging
import subprocess
import sys
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import pytz
from raffles import announce_winners
from automesaj import setup_auto_message_scheduler  # Otomatik mesajları dahil et

logger = logging.getLogger(__name__)

# Site güncelleme işlemi
def run_sites_update():
    logger.info("sitesUpdate.py çalıştırılıyor...")
    subprocess.Popen([sys.executable, "sitesUpdate.py"])
    logger.info("Bot yeniden başlatılıyor...")
    time.sleep(2)
    os.execv(sys.executable, [sys.executable] + sys.argv)


# Kazananları duyurma işlemi
#def check_raffle_winners():
#    logger.info("Kazananlar kontrol ediliyor...")
 #   announce_winners(None, 1)

def setup_scheduler():
    scheduler = BackgroundScheduler(timezone=pytz.utc)

    try:
        # 24 saatte bir sitesUpdate.py dosyasını çalıştırma
        scheduler.add_job(run_sites_update, trigger=IntervalTrigger(hours=24, timezone=pytz.utc))

        # Otomatik mesajlar için zamanlayıcıyı başlatma
        setup_auto_message_scheduler()

        # Zamanlayıcıyı başlatma
        scheduler.start()
        logger.info("Scheduler başlatıldı, görevler zamanlandı.")
    except Exception as e:
        logger.error(f"Scheduler başlatılırken hata oluştu: {e}")