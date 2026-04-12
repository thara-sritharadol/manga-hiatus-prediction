import requests

API_IMPUTE = "http://localhost:8080/api/manga/impute-titles"

def run_title_imputation():
    print("[Data Cleanser] สั่งการ Go API เพื่อซ่อมแซมชื่อภาษาอังกฤษ...")
    
    try:
        res = requests.post(API_IMPUTE)
        
        if res.status_code == 200:
            data = res.json()
            updated_rows = data.get("updated_rows", 0)
            print(f"[Data Cleanser] ซ่อมแซมสำเร็จ! เติมชื่อไปทั้งหมด {updated_rows} รายการ")
        else:
            print(f"[Data Cleanser] Go API แจ้ง Error: {res.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"[Data Cleanser] ไม่สามารถเชื่อมต่อกับ Go API ได้: {e}")

if __name__ == "__main__":
    run_title_imputation()