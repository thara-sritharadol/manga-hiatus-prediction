import time
from prefect import task, flow, get_run_logger

# --- 1. Task สำหรับดึงข้อมูลฝั่งไทย ---
@task(name="Scrape Thai Publisher", retries=2)
def scrape_thai_data():
    logger = get_run_logger()
    logger.info("Starting to scrape Thai publisher websites...")
    
    # จำลองข้อมูลที่ Scrape มาได้
    return [
        {"th_title": "กระซิบรักเป็นทำนองร้องบอกเธอ", "th_vol": 8, "publisher": "Phoenix"},
        {"th_title": "ดาบพิฆาตอสูร", "th_vol": 23, "publisher": "SIC"}
    ]

# --- 2. Task สำหรับดึงข้อมูลฝั่งญี่ปุ่น (API) ---
@task(name="Fetch Japan Metadata")
def fetch_japan_metadata():
    # ในงานจริง คุณจะใช้ requests.get("https://api.jikan.moe/v4/manga/...")
    return [
        {"jp_title": "Sasayaku You ni Koi o Utau", "en_title": "Whisper Me a Love Song", "jp_status": "Publishing", "jp_total_vol": 10},
        {"jp_title": "Kimetsu no Yaiba", "en_title": "Demon Slayer", "jp_status": "Finished", "jp_total_vol": 23}
    ]

# --- 3. Task สำหรับ Matching (หัวใจสำคัญ) ---
@task(name="Data Matching & Feature Engineering")
def match_and_process(thai_list, japan_list):
    processed_results = []
    
    # ในงานจริง ตรงนี้อาจใช้ Library 'thefuzz' เพื่อทำ Fuzzy Matching ชื่อเรื่อง
    # แต่ตอนนี้เราจะจำลองการ Match แบบง่ายๆ
    for th_item in thai_list:
        # สมมติว่าเรามี Logic จับคู่ 'กระซิบรัก...' กับ 'Whisper Me a Love Song' ได้
        if "กระซิบรัก" in th_item['th_title']:
            jp_info = japan_list[0] 
            
            # คำนวณ Feature: ส่วนต่างของเล่ม (Volume Gap)
            vol_gap = jp_info['jp_total_vol'] - th_item['th_vol']
            
            processed_results.append({
                "title": th_item['th_title'],
                "vol_gap": vol_gap,
                "is_finished_jp": jp_info['jp_status'] == "Finished",
                "risk_score": vol_gap * 2.5 # สูตรสมมติสำหรับทำนายเบื้องต้น
            })
            
    return processed_results

# --- 4. Task สำหรับรัน Model ทำนาย ---
@task(name="ML Prediction")
def predict_abandonment(data):
    logger = get_run_logger()
    for item in data:
        # ในงานจริง: model.predict([[item['vol_gap'], item['is_finished_jp']]])
        status = "เสี่ยงถูกลอยแพ" if item['risk_score'] > 5 else "ปลอดภัย/ไปต่อ"
        logger.info(f"ผลทำนายเรื่อง {item['title']}: {status}")
    return "Done"

# --- Main Flow: ผู้ควบคุมลำดับงาน ---
@flow(name="Manga Abandonment Prediction Pipeline")
def manga_prediction_flow():
    # รัน Task ย่อยๆ ตามลำดับ
    thai_data = scrape_thai_data()
    japan_data = fetch_japan_metadata()
    
    # ส่งข้อมูลจาก 2 Task แรกเข้าสู่ Task การประมวลผล
    final_features = match_and_process(thai_data, japan_data)
    
    # นำข้อมูลที่พร้อมแล้วไปทำนาย
    predict_abandonment(final_features)

if __name__ == "__main__":
    manga_prediction_flow()