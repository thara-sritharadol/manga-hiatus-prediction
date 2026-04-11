import requests
import time
import re

API_GET_PENDING = "http://localhost:8080/api/manga/pending?status=PENDING_MU"
API_UPSERT = "http://localhost:8080/api/manga"

def enrich_with_mangaupdates():
    print("Retrieving a list of manga...")
    
    try:
        res = requests.get(API_GET_PENDING)
        if res.status_code != 200:
            print("Unable to connect to the Go API.")
            return

        pending_mangas = res.json().get("data", [])
        
        if not pending_mangas:
            print("Up-to-Date")
            return
        
        print(f"Found a manga to search for on the Japanese side: {len(pending_mangas)} series")

        for manga in pending_mangas:
            title_en = manga["title_en"]
            print(f"\nSearching in MU: {title_en}...")

            search_url = "https://api.mangaupdates.com/v1/series/search"
            search_payload = {"search": title_en}
            
            mu_res = requests.post(search_url, json=search_payload)

            if mu_res.status_code == 200:
                results = mu_res.json().get("results", [])

                if len(results) > 0:
                    series_id = results[0].get("record", {}).get("series_id")
                    
                    detail_url = f"https://api.mangaupdates.com/v1/series/{series_id}"
                    detail_res = requests.get(detail_url)
                    
                    if detail_res.status_code == 200:
                        detail_data = detail_res.json()
                        
                        # MU usually use "5 Volumes (Complete)" or "Ongoing"
                        mu_status_text = detail_data.get("status", "")
                        
                        vol_match = re.search(r'(\d+)\s+Volumes?', mu_status_text, re.IGNORECASE)
                        vols_count = int(vol_match.group(1)) if vol_match else 0
                        
                        if "Complete" in mu_status_text:
                            manga["jikan_status"] = "FINISHED"
                            manga["jp_total_vols"] = vols_count
                        elif "Ongoing" in mu_status_text:
                            manga["jikan_status"] = "ONGOING"
                            manga["jp_total_vols"] = vols_count
                        elif "Hiatus" in mu_status_text:
                            manga["jikan_status"] = "HIATUS"
                            manga["jp_total_vols"] = vols_count
                        else:

                            if vols_count == 0:
                                manga["jikan_status"] = "PENDING_JIKAN"
                            else:
                                manga["jikan_status"] = "UNKNOWN"
                                manga["jp_total_vols"] = vols_count

                        if vols_count > 0:
                            print(f"   -> MU Found! Volumes: {vols_count} | Raw Data: {mu_status_text}")
                        else:
                            print(f"   -> MU Found with No Volumes (PENDING_JIKAN)")
                            
                else:
                    print("   -> MU Not Found (PENDING_JIKAN)")
                    manga["jikan_status"] = "PENDING_JIKAN"

            elif mu_res.status_code == 429:
                print("MU Rate Limit!...")
                time.sleep(5)
                continue 

            update_res = requests.post(API_UPSERT, json=manga)
            if update_res.status_code == 201:
                print(f"   Save Successfully")
            else:
                print(f"   Save Failed")

            time.sleep(2) #

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    enrich_with_mangaupdates()