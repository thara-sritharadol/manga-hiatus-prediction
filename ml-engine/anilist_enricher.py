import requests
import time

API_GET_PENDING = "http://localhost:8080/api/manga/pending"
API_UPSERT = "http://localhost:8080/api/manga"

# URL for AniList GraphQL
ANILIST_URL = 'https://graphql.anilist.co'

graphql_query = '''
query ($query: String) {
  Media (search: $query, type: MANGA, format: MANGA) {
    id
    title {
      romaji
      english
    }
    status
    volumes
    chapters
    startDate {
      year
    }
  }
}
'''

def enrich_with_anilist():
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
            print(f"\nกำลังค้นหาใน AniList: {title_en}...")

            # Payload for GraphQL
            variables = {
                'query': title_en
            }

            anilist_res = requests.post(ANILIST_URL, json={'query': graphql_query, 'variables': variables})

            if anilist_res.status_code == 200:
                result_data = anilist_res.json().get('data', {}).get('Media')

                if result_data:
                    ani_status = result_data.get('status')
                    volumes = result_data.get('volumes')
                    
                    vols_count = volumes if volumes is not None else 0

                    if vols_count > 0:
                        if ani_status == "FINISHED":
                            manga["jikan_status"] = "FINISHED"
                        elif ani_status == "RELEASING":
                            manga["jikan_status"] = "ONGOING"
                        elif ani_status in ["CANCELLED", "HIATUS"]:
                            manga["jikan_status"] = ani_status
                        else:
                            manga["jikan_status"] = "UNKNOWN"
                            
                        manga["jp_total_vols"] = vols_count
                        print(f"   -> Complete! Status: {ani_status} | Volumes: {vols_count}")

                    else:
                        # (vols_count == 0)
                        manga["jikan_status"] = "PENDING_MU" 
                        manga["jp_total_vols"] = 0
                        print(f"   -> Title With No Volumn (PENDING_MU)")

                else:
                    manga["jikan_status"] = "PENDING_MU" 
                    manga["jp_total_vols"] = 0
                    print("   -> Not Found (PENDING_MU)")

            elif anilist_res.status_code == 429:
                print("AniList Rate Limit...")
                time.sleep(10)
                continue

            elif anilist_res.status_code == 404:
                print("Not Found")
                manga["jikan_status"] = "PENDING_MU" 
                manga["jp_total_vols"] = 0
                print("   -> Not Found (PENDING_MU)")

                update_res = requests.post(API_UPSERT, json=manga)
                if update_res.status_code == 201:
                    print(f"   Save Successfully")
                else:
                    print(f"   Save Successfully: {update_res.text}")

            else:
                print(f"   -> API Error: {anilist_res.status_code}")
                continue
            
            print(f"   [Debug] Data: {manga}")
            update_res = requests.post(API_UPSERT, json=manga)
            if update_res.status_code == 201:
                print(f"   Save Successfully")
            else:
                print(f"   Save Failed: {update_res.text}")

            time.sleep(2.5)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    enrich_with_anilist()