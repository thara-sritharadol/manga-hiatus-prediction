import requests
import json

def fetch_manga_status(search_query):
    print(f"🔍 กำลังค้นหาข้อมูล: {search_query}...")
    
    # ยิง API ไปที่ Endpoint สำหรับค้นหามังงะ โดยขอแค่ผลลัพธ์แรกสุด (limit=1)
    url = f"https://api.jikan.moe/v4/manga?q={search_query}&limit=1"
    
    response = requests.get(url)
    
    # เช็คว่ายิง API สำเร็จไหม (HTTP 200)
    if response.status_code == 200:
        result = response.json()
        
        # ตรวจสอบว่ามีข้อมูลกลับมาไหม
        if result['data']:
            manga = result['data'][0]
            
            # ดึงเฉพาะฟิลด์ที่เราจะเอาไปทำ Model
            print("-" * 30)
            print(f"📖 ชื่ออังกฤษ: {manga.get('title_english')}")
            print(f"🇯🇵 ชื่อญี่ปุ่น: {manga.get('title_japanese')}")
            print(f"โรมาจิ: {manga.get('title')}")
            print(f"📊 สถานะ: {manga.get('status')}")
            print(f"📚 จำนวนเล่มที่ออกแล้ว (JP): {manga.get('volumes')}")
            print(f"📅 เริ่มตีพิมพ์เมื่อ: {manga['published']['from'][:10] if manga.get('published') else 'N/A'}")
            print("-" * 30)
            
        else:
            print("❌ ไม่พบข้อมูลเรื่องนี้")
    else:
        print(f"⚠️ API Error: {response.status_code}")

# ลองทดสอบรันด้วยเรื่อง Whisper Me a Love Song 
# Koutsugou Semi-Friend
# Kimi to Shiranai Natsu ni Naru
# Anemone wa Netsu wo Obiru
# Tokidoki Bosotto Roshiago De Dereru Tonari no Alya-san
# Kage no Jitsuryokusha ni Naritakute!
fetch_manga_status("Shuu ni Ichido Classmate wo Kau Hanashi: Futari no Jikan, Iiwake no 5000-en")