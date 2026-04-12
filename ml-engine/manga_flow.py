from prefect import task, flow
import time

from phoenix_scraper import start_scraping # สมมติว่าคุณรวบโค้ดใน phoenix_scraper.py ไว้ในฟังก์ชันนี้
from title_imputer import run_title_imputation
from jikan_enricher import enrich_with_jikan
from anilist_enricher import enrich_with_anilist
from mu_enricher import enrich_with_mangaupdates

# 🌟 1. เปลี่ยนสคริปต์เดิมให้เป็น "Task"
# เราสามารถกำหนดจำนวนครั้งที่ให้ลองใหม่ได้ถ้าเกิด Error (retries)
@task(retries=2, retry_delay_seconds=60)
def run_phoenix_scraper():
    print("--- Starting Phoenix Scraper ---")
    start_scraping() 

@task(retries=2, retry_delay_seconds=60)
def run_imputer_title():
    print("--- Starting Imputation Title ---")
    run_title_imputation() 

@task(retries=3, retry_delay_seconds=30)
def run_jikan_enricher():
    print("--- Starting Jikan Enricher ---")
    enrich_with_jikan()

@task(retries=3, retry_delay_seconds=30)
def run_anilist_enricher():
    print("--- Starting AniList Enricher ---")
    enrich_with_anilist()

@task(retries=3, retry_delay_seconds=30)
def run_mu_enricher():
    print("--- Starting MU Enricher (Final Step) ---")
    enrich_with_mangaupdates()

# 🌟 2. สร้าง "Flow" เพื่อกำหนดลำดับการทำงาน (Waterfall)
@flow(name="Manga Data Prediction")
def manga_full_pipeline():
    # เรียงลำดับตาม Logic ที่เราวางไว้
    # 1. กวาดข้อมูลจากไทยก่อน
    run_phoenix_scraper()

    run_imputer_title()
    
    # 2. เริ่มขั้นตอนการ Enrich ข้อมูลจากญี่ปุ่น
    # Prefect จะรอให้ Phoenix เสร็จก่อนค่อยเริ่ม Jikan ตามลำดับที่เราเขียน
    run_jikan_enricher()
    run_anilist_enricher()
    run_mu_enricher()

if __name__ == "__main__":
    # รัน Pipeline ทั้งหมด
    manga_full_pipeline()