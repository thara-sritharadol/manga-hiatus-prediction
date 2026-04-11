import requests
import pandas as pd
import time

def fetch_multiple_mangas(manga_list):
    # สร้าง List ว่างๆ ไว้เก็บข้อมูลแต่ละเรื่อง
    manga_data = []

    print("🚀 เริ่มดึงข้อมูลจาก Jikan API...\n")

    for title in manga_list:
        url = f"https://api.jikan.moe/v4/manga?q={title}&limit=1"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result['data']:
                manga = result['data'][0]
                
                # ดึงข้อมูลมาสร้างเป็น Dictionary (เทียบเท่า 1 แถวในตาราง)
                row = {
                    "title_en": manga.get('title_english'),
                    "title_jp": manga.get('title_japanese'),
                    "romaji": manga.get('title'),
                    "status": manga.get('status'),
                    "volumes": manga.get('volumes'),
                    "chapters": manga.get('chapters'), # ดึง chapter มาเผื่อกรณี volumes เป็น None
                    "published_from": manga['published']['from'][:10] if manga.get('published') and manga['published'].get('from') else None
                }
                manga_data.append(row)
                print(f"✅ สำเร็จ: {title}")
            else:
                print(f"❌ ไม่พบข้อมูล: {title}")
        else:
            print(f"⚠️ API Error ({response.status_code}) สำหรับเรื่อง: {title}")
            
        # 🌟 กฎเหล็กของ DevOps/Scraper: ต้องหน่วงเวลาเสมอ เพื่อไม่ให้โดน API แบน!
        time.sleep(1) 

    # --- แปลง List ของ Dictionary ให้กลายเป็น Pandas DataFrame ---
    df = pd.DataFrame(manga_data)
    return df

# ลองลิสต์ชื่อเรื่องที่อยากดึง (ผสมเรื่องเก่า เรื่องใหม่ เรื่องที่ยังไม่จบ)
titles_to_search = [
    "Whisper Me a Love Song", 
    "Anemone wa Netsu wo Obiru", 
    "Kimi to Shiranai Natsu ni Naru", 
    "Tokidoki Bosotto Roshiago De Dereru Tonari no Alya-san",
    "Kage no Jitsuryokusha ni Naritakute!"
    "watanare"
]

# เรียกใช้งานฟังก์ชัน
df_result = fetch_multiple_mangas(titles_to_search)

print("\n📊 หน้าตาของ DataFrame ที่ได้:")
print("-" * 60)
print(df_result.to_string()) # ใช้ to_string() เพื่อให้ปริ้นท์ออกมาดูง่ายๆ ทุกคอลัมน์
print("-" * 60)

# เคล็ดลับ Data Engineer: เซฟลง CSV ไว้ใช้งานต่อ จะได้ไม่ต้องยิง API ซ้ำ
df_result.to_csv("manga_raw_data.csv", index=False, encoding='utf-8')
print("\n💾 บันทึกข้อมูลลงไฟล์ manga_raw_data.csv เรียบร้อยแล้ว!")