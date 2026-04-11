import requests
import time

API_GET_PENDING = "http://localhost:8080/api/manga/pending?status=PENDING_JIKAN"
API_UPSERT = "http://localhost:8080/api/manga"

def enrich_with_jikan():
    print("Retrieving a list of manga...")
    
    try:
        res = requests.get(API_GET_PENDING)
        if res.status_code != 200:
            print("Unable to connect to the Go API.")
            return

        pending_mangas = res.json().get("data", [])
        
        if not pending_mangas:
            print("Up-to-date")
            return
        
        print(f"Found a manga to search for on the Japanese side: {len(pending_mangas)} series")

        for manga in pending_mangas:
            title_en = manga["title_en"]
            print(f"\nSearching in Jikan: {title_en}...")

            jikan_url = f"https://api.jikan.moe/v4/manga?q={title_en}&limit=1"
            jikan_res = requests.get(jikan_url)

            if jikan_res.status_code == 200:
                jikan_data = jikan_res.json().get("data", [])

                if len(jikan_data) > 0:
                    first_result = jikan_data[0]
                    status = first_result.get("status")
                    volumes = first_result.get("volumes")
                    
                    vols_count = volumes if volumes is not None else 0

                    if status == "Finished":
                        manga["jikan_status"] = "FINISHED"
                        manga["jp_total_vols"] = vols_count
                    elif status == "Publishing":
                        manga["jikan_status"] = "ONGOING"
                        manga["jp_total_vols"] = vols_count
                    else:
                        manga["jikan_status"] = "UNKNOWN"
                        
                    print(f"   -> Jikan Found! Status: {status} | Volumes: {volumes}")
                else:
                    print("   -> Jikan Not Found")
                    manga["jikan_status"] = "NOT_FOUND"

            elif jikan_res.status_code == 429:
                print("Jikan Rate Limit!...")
                time.sleep(10)
                continue 
            else:
                manga["jikan_status"] = "API_ERROR"

            update_res = requests.post(API_UPSERT, json=manga)
            if update_res.status_code == 201:
                print(f"   Save Successfully")
            else:
                print(f"   Save Failed: {update_res.text}")

            time.sleep(1.5)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    enrich_with_jikan()