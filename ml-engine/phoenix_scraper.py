import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from datetime import datetime

#base_url = "https://www.phoenixnext.com/gl.html?p="

TARGET_CATEGORIES = [
    "https://www.phoenixnext.com/manga.html?p=",
    #"https://www.phoenixnext.com/light-novel.html?p="
]

all_manga_data = []              

PREMIUM_KEYWORDS = [
    "Premium Set", "Special Set", "Complete Set", 
    "Short Story Set", "Box Set", "Short Story"
]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

print("เริ่มทำการ Crawl ข้อมูล...")

def extract_romaji_title(html_text):
    if not html_text: return "ไม่พบข้อมูล"
    all_brackets = re.findall(r'\((.*?)\)', html_text)
    if not all_brackets: return "ไม่พบวงเล็บ"
    
    potential_titles = []
    for text in all_brackets:
        text = text.strip()
        if len(text) < 4: continue
        if not re.search(r'[a-zA-Z]', text): continue
        forbidden_words = r'มังงะ|ไลท์โนเวล|พิมพ์ครั้ง|เล่ม|ฉบับ'
        if re.search(forbidden_words, text, re.IGNORECASE): continue
        potential_titles.append(text)

    if potential_titles:
        raw_title = potential_titles[0] 
        clean_title = re.sub(r'(?i)\s*vol\.?\s*[0-9\-]+$', '', raw_title)
        return clean_title.strip()
    return "ไม่พบข้อมูลภาษาอังกฤษ"

def process_title(raw_text):
    media_type = "Manga"
    if re.search(r'^\(LN\)', raw_text, re.IGNORECASE):
        media_type = "Light Novel"
    elif re.search(r'^\(มังงะ\)', raw_text, re.IGNORECASE):
        media_type = "Manga"
    
    clean_name = re.sub(r'^\(มังงะ\) |^\(LN\) ', '', raw_text)
    pattern = r"|".join(map(re.escape, PREMIUM_KEYWORDS))
    clean_name = re.sub(pattern, "", clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r"\s+", " ", clean_name).strip()

    return clean_name, media_type

def match_tile_vol(clean_name):

    title_match = re.search(r'(.*?)\s+\(จบในเล่ม\)', clean_name)
    if title_match:
        th_title = title_match.group(1).strip() if title_match else clean_name
        th_vol = 1
        raw_vol = "1"

        return th_title, th_vol, raw_vol

    title_match = re.search(r'(.*?)\s+เล่ม\s*(\d+)', clean_name)

    th_title = title_match.group(1).strip() if title_match else clean_name
    
    vol_match = re.search(r'เล่ม\s*(\d+)(?:[-\s]*(\d+))?', clean_name)

    if vol_match:
        # ถ้าเจอเลขสองชุด (เช่น 1-2) ให้เอาเลขตัวหลัง (Group 2)
        # ถ้าเจอเลขชุดเดียว (เช่น 1) ให้เอาเลขตัวแรก (Group 1)
        v1 = vol_match.group(1)
        v2 = vol_match.group(2)
        th_vol = int(v2) if v2 else int(v1)
    else:
        th_vol = 1

    if vol_match.group(2):
        raw_vol = str(vol_match.group(1)) + "-" + str(vol_match.group(2))
    else:
        raw_vol = str(vol_match.group(1))

    return th_title, th_vol, raw_vol

def find_th_release_date(detail_soup):

    th_release_date = None
    label_span = detail_soup.find('span', string=lambda text: text and "วันวางจำหน่าย" in text)

    if label_span:
        # 2. กระโดดไปหาแท็ก span ตัวถัดไปที่อยู่ติดกัน
        date_span = label_span.find_next_sibling('span')
    
        if date_span:
            # ดึงข้อความออกมา จะได้ ": 18-03-2026"
            raw_date_text = date_span.get_text(strip=True)
        
            # 3. ลบเครื่องหมาย : และช่องว่างทิ้ง
            clean_date_str = raw_date_text.replace(":", "").strip()
        
            # 4. [Data Engineering Best Practice] แปลงเป็น YYYY-MM-DD
            try:
                # อ่านวันที่ในรูปแบบ วัน-เดือน-ปี
                dt_obj = datetime.strptime(clean_date_str, "%d-%m-%Y")
                # แปลงเป็น ปี-เดือน-วัน (ISO Format ที่ Postgres ชอบ)
                th_release_date = dt_obj.strftime("%Y-%m-%dT00:00:00Z")
            except ValueError:
                # ถ้าเว็บพิมพ์วันที่มาผิดฟอร์แมต ให้เก็บแบบดิบๆ ไปก่อน
                th_release_date = None

    return th_release_date

def find_price(detail_soup):
    th_price = 0.0
    old_price_div = detail_soup.find('div', class_=re.compile(r'old-price'))

    if old_price_div:
        price_span = old_price_div.find('span', class_='price')
        if price_span:
            raw_price_text = price_span.get_text(strip=True) # จะได้ข้อความเช่น "฿175.00"
            
            # ใช้ Regex ทำความสะอาด: เก็บไว้เฉพาะ "ตัวเลข" และ "จุดทศนิยม"
            # จะตัดตัวอักษร ฿ หรือลูกน้ำ (,) ออกให้หมด
            clean_price_str = re.sub(r'[^\d.]', '', raw_price_text)
            
            try:
                th_price = float(clean_price_str)
                print(f"   [Log] เจอราคาเต็ม (ดึงจากป้ายลดราคา): {th_price}")
            except ValueError:
                pass

    if th_price == 0.0:
        price_meta = detail_soup.find('meta', itemprop='price')
    
        if price_meta and price_meta.has_attr('content'):
            try:
                th_price = float(price_meta['content'])
                print(f"   [Log] เจอราคาเต็ม (ดึงจาก Meta Tag): {th_price}")
            except ValueError:
                pass

    if th_price == 0.0:
        print("   [Log] ⚠️ หาข้อมูลราคาไม่เจอเลย")

    return th_price

def process_description(detail_soup):
    en_title = "ไม่พบข้อมูลภาษาอังกฤษ"
    has_premium = 0
    premium_type = "None"

    description = detail_soup.find('div', class_='prose')

    if description:
        raw_html = str(description)
        desc_text = re.sub(r'<[^>]+>', ' ', raw_html)
        desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                
        for kw in PREMIUM_KEYWORDS:
            if kw.lower() in desc_text.lower():
                has_premium = 1
                premium_type = kw
                break # เจออันแรกที่ตรงก็หยุดเลย
                
        en_title = extract_romaji_title(desc_text)

    return en_title, has_premium, premium_type

def start_scraping():
    def extract_romaji_title(html_text):
        if not html_text: return "ไม่พบข้อมูล"
        all_brackets = re.findall(r'\((.*?)\)', html_text)
        if not all_brackets: return "ไม่พบวงเล็บ"
        
        potential_titles = []
        for text in all_brackets:
            text = text.strip()
            if len(text) < 4: continue
            if not re.search(r'[a-zA-Z]', text): continue
            forbidden_words = r'มังงะ|ไลท์โนเวล|พิมพ์ครั้ง|เล่ม|ฉบับ'
            if re.search(forbidden_words, text, re.IGNORECASE): continue
            potential_titles.append(text)

        if potential_titles:
            raw_title = potential_titles[0] 
            clean_title = re.sub(r'(?i)\s*vol\.?\s*[0-9\-]+$', '', raw_title)
            return clean_title.strip()
        return "ไม่พบข้อมูลภาษาอังกฤษ"
    def process_title(raw_text):
        media_type = "Manga"
        if re.search(r'^\(LN\)', raw_text, re.IGNORECASE):
            media_type = "Light Novel"
        elif re.search(r'^\(มังงะ\)', raw_text, re.IGNORECASE):
            media_type = "Manga"
        
        clean_name = re.sub(r'^\(มังงะ\) |^\(LN\) ', '', raw_text)
        pattern = r"|".join(map(re.escape, PREMIUM_KEYWORDS))
        clean_name = re.sub(pattern, "", clean_name, flags=re.IGNORECASE)
        clean_name = re.sub(r"\s+", " ", clean_name).strip()

        return clean_name, media_type
    def match_tile_vol(clean_name):
        title_match = re.search(r'(.*?)\s+\(จบในเล่ม\)', clean_name)
        if title_match:
            th_title = title_match.group(1).strip() if title_match else clean_name
            th_vol = 1
            raw_vol = "1"

            return th_title, th_vol, raw_vol

        title_match = re.search(r'(.*?)\s+เล่ม\s*(\d+)', clean_name)

        th_title = title_match.group(1).strip() if title_match else clean_name
        
        vol_match = re.search(r'เล่ม\s*(\d+)(?:[-\s]*(\d+))?', clean_name)

        if vol_match:
            # ถ้าเจอเลขสองชุด (เช่น 1-2) ให้เอาเลขตัวหลัง (Group 2)
            # ถ้าเจอเลขชุดเดียว (เช่น 1) ให้เอาเลขตัวแรก (Group 1)
            v1 = vol_match.group(1)
            v2 = vol_match.group(2)
            th_vol = int(v2) if v2 else int(v1)
        else:
            th_vol = 1

        if vol_match.group(2):
            raw_vol = str(vol_match.group(1)) + "-" + str(vol_match.group(2))
        else:
            raw_vol = str(vol_match.group(1))

        return th_title, th_vol, raw_vol
    def find_th_release_date(detail_soup):
        th_release_date = None
        label_span = detail_soup.find('span', string=lambda text: text and "วันวางจำหน่าย" in text)

        if label_span:
            # 2. กระโดดไปหาแท็ก span ตัวถัดไปที่อยู่ติดกัน
            date_span = label_span.find_next_sibling('span')
        
            if date_span:
                # ดึงข้อความออกมา จะได้ ": 18-03-2026"
                raw_date_text = date_span.get_text(strip=True)
            
                # 3. ลบเครื่องหมาย : และช่องว่างทิ้ง
                clean_date_str = raw_date_text.replace(":", "").strip()
            
                # 4. [Data Engineering Best Practice] แปลงเป็น YYYY-MM-DD
                try:
                    # อ่านวันที่ในรูปแบบ วัน-เดือน-ปี
                    dt_obj = datetime.strptime(clean_date_str, "%d-%m-%Y")
                    # แปลงเป็น ปี-เดือน-วัน (ISO Format ที่ Postgres ชอบ)
                    th_release_date = dt_obj.strftime("%Y-%m-%dT00:00:00Z")
                except ValueError:
                    # ถ้าเว็บพิมพ์วันที่มาผิดฟอร์แมต ให้เก็บแบบดิบๆ ไปก่อน
                    th_release_date = None

        return th_release_date
    def find_price(detail_soup):
        th_price = 0.0
        old_price_div = detail_soup.find('div', class_=re.compile(r'old-price'))

        if old_price_div:
            price_span = old_price_div.find('span', class_='price')
            if price_span:
                raw_price_text = price_span.get_text(strip=True) # จะได้ข้อความเช่น "฿175.00"
                
                # ใช้ Regex ทำความสะอาด: เก็บไว้เฉพาะ "ตัวเลข" และ "จุดทศนิยม"
                # จะตัดตัวอักษร ฿ หรือลูกน้ำ (,) ออกให้หมด
                clean_price_str = re.sub(r'[^\d.]', '', raw_price_text)
                
                try:
                    th_price = float(clean_price_str)
                    print(f"   [Log] เจอราคาเต็ม (ดึงจากป้ายลดราคา): {th_price}")
                except ValueError:
                    pass

        if th_price == 0.0:
            price_meta = detail_soup.find('meta', itemprop='price')
        
            if price_meta and price_meta.has_attr('content'):
                try:
                    th_price = float(price_meta['content'])
                    print(f"   [Log] เจอราคาเต็ม (ดึงจาก Meta Tag): {th_price}")
                except ValueError:
                    pass

        if th_price == 0.0:
            print("   [Log] ⚠️ หาข้อมูลราคาไม่เจอเลย")

        return th_price
    def process_description(detail_soup):
        en_title = "ไม่พบข้อมูลภาษาอังกฤษ"
        has_premium = 0
        premium_type = "None"

        description = detail_soup.find('div', class_='prose')

        if description:
            raw_html = str(description)
            desc_text = re.sub(r'<[^>]+>', ' ', raw_html)
            desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                    
            for kw in PREMIUM_KEYWORDS:
                if kw.lower() in desc_text.lower():
                    has_premium = 1
                    premium_type = kw
                    break # เจออันแรกที่ตรงก็หยุดเลย
                    
            en_title = extract_romaji_title(desc_text)

        return en_title, has_premium, premium_type
    for base_url in TARGET_CATEGORIES:
        print(f"กำลังกวาดข้อมูลหมวดหมู่: {base_url}")

        page = 1

        first_page_first_item_url = None

        while True:
            print(f"กำลังกวาดข้อมูล หน้าที่ {page}...")
            url = f"{base_url}{page}"
            response = requests.get(url, headers=headers)

            if response.status_code != 200:
                print(f"Error {response.status_code} หยุดการค้นหาหมวดหมู่นี้")
                break

            soup = BeautifulSoup(response.text, 'lxml')
            title_tags = soup.find_all('a', class_='product-item-link line-clamp-2')

            if len(title_tags) == 0: 
                print(f"ไม่พบสินค้าในหน้าที่ {page} ถือว่ากวาดจบหมวดหมู่นี้แล้ว!")
                break
            
            current_first_item_url = title_tags[0]['href']

            if page == 1:
                first_page_first_item_url = current_first_item_url
            elif current_first_item_url == first_page_first_item_url:
                print(f"ตรวจพบการวนลูปกลับหน้า 1! ถือว่ากวาดจบหมวดหมู่นี้ที่หน้า {page - 1}")
                break


            if page > 150: 
                print("กวาดเกิน 150 หน้าแล้ว ผิดปกติแน่นอน ขอตัดจบหมวดหมู่นี้")
                break

            for a_tag in title_tags:
                try:
                    raw_title = a_tag.text.strip()
                    detail_url = a_tag['href']
                    clean_name, type_media = process_title(raw_title)
                    th_title, th_vol, raw_vol= match_tile_vol(clean_name)


                    print(f"กำลังเจาะเข้าหน้า: {th_title} เล่ม {th_vol}...")
                    detail_res = requests.get(detail_url, headers=headers)
                    detail_soup = BeautifulSoup(detail_res.text, 'lxml')

                    release_date_th = find_th_release_date(detail_soup)
                    print(f"   [Log] Release Date: {release_date_th}")
                    
                    th_price = find_price(detail_soup)

                    en_title, has_premium, premium_type = process_description(detail_soup)

                    all_manga_data.append({
                        "title_th": th_title,
                        "vol_th": th_vol,
                        "vol_raw": raw_vol,
                        "title_en": en_title,
                        "has_premium": has_premium,
                        "premium_type": premium_type,
                        "media_type" : type_media,
                        "price": th_price,
                        "url": detail_url, 
                        "th_release_date": release_date_th
                    })

                    manga_record = {
                        "url": detail_url,
                        "title_th": th_title,
                        "title_en": en_title,
                        "vol_th": th_vol,
                        "vol_raw": raw_vol,
                        "has_premium": has_premium,
                        "premium_type": premium_type,
                        "media_type" : type_media,
                        "price": th_price,
                        "th_release_date": release_date_th,
                    }

                    api_endpoint = "http://localhost:8080/api/manga"

                    try:
                        # 3. ยิง Request แบบ POST และส่งข้อมูลเป็น JSON
                        res = requests.post(api_endpoint, json=manga_record)
                        
                        # 4. เช็คผลลัพธ์ (Go ของเราตั้งค่าไว้ว่าถ้าสำเร็จจะส่ง 201 Created กลับมา)
                        if res.status_code == 201:
                            print(f"บันทึก/อัปเดตลง DB สำเร็จ: {th_title} เล่ม {th_vol}")
                        else:
                            # กรณี Go แจ้ง Error กลับมา (เช่น JSON ผิดฟอร์แมต หรือ DB มีปัญหา)
                            print(f"API ตอบกลับ Error (Status {res.status_code}):")
                            print(f"รายละเอียด: {res.text}")
                            print(f"ข้อมูลที่พยายามส่งไป: {manga_record}")
                            
                    except requests.exceptions.RequestException as e:
                        # กรณีที่ Python หา Go Server ไม่เจอ (ลืมเปิด Server หรือพอร์ตผิด)
                        print(f"ไม่สามารถเชื่อมต่อกับ Go API ได้: {e}")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    print(f"Error: {e}")
                    continue
                
            page += 1

            """
            if page == 5:
                break
            """

    print("\nกวาดข้อมูลเสร็จสมบูรณ์!")

if __name__ == "__main__":
    start_scraping()
