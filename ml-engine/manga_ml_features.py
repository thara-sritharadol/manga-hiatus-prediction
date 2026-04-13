import requests

API_GENERATE_FEATURES = "http://localhost:8080/api/manga/generate-features"

def trigger_feature_generation():
    print("[ML Feature] กำลังสั่งการ Go API ให้สร้างตาราง Machine Learning...")
    
    try:
        res = requests.post(API_GENERATE_FEATURES)
        
        if res.status_code == 200:
            print("[ML Feature] สร้างตาราง manga_ml_features สำเร็จพร้อมใช้งาน!")
        else:
            print(f"[ML Feature] Go API แจ้ง Error: {res.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[ML Feature] ไม่สามารถเชื่อมต่อกับ Go API ได้: {e}")

if __name__ == "__main__":
    trigger_feature_generation()