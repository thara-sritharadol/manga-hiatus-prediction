import requests
import time

API_GET_PENDING = "http://localhost:8080/api/manga/pending?status=PENDING_AL"
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
    print("Retrieving a list of manga from PENDING_AL...")
    
    try:
        res = requests.get(API_GET_PENDING)
        if res.status_code != 200:
            print("Unable to connect to the Go API.")
            return

        pending_mangas = res.json().get("data", [])
        
        if not pending_mangas:
            print("Up-to-date (No PENDING_AL manga)")
            return
        
        print(f"Found manga to search in AniList: {len(pending_mangas)} series")

        for manga in pending_mangas:
            title_jp = manga["title_jp"]
            print(f"\nSearching in AniList: {title_jp}...")

            # Payload for GraphQL
            variables = {
                'query': title_jp
            }

            anilist_res = requests.post(ANILIST_URL, json={'query': graphql_query, 'variables': variables})

            if anilist_res.status_code == 200:
                # GraphQL มักจะตอบกลับเป็น 200 เสมอ แม้จะหาไม่เจอ แต่จะให้ result_data เป็น None
                result_data = anilist_res.json().get('data', {}).get('Media')

                if result_data:
                    ani_status = result_data.get('status')
                    volumes = result_data.get('volumes')
                    
                    vols_count = volumes if volumes is not None else 0

                    if vols_count > 0:
                        """
                        if ani_status == "FINISHED":
                            manga["jikan_status"] = "FINISHED"
                        elif ani_status == "RELEASING":
                            manga["jikan_status"] = "ONGOING"
                        elif ani_status in ["CANCELLED", "HIATUS"]:
                            manga["jikan_status"] = ani_status
                        else:
                            manga["jikan_status"] = "UNKNOWN"
                        """
                        manga["jp_total_vols"] = vols_count
                        print(f"   -> Complete! Status: {ani_status} | Volumes: {vols_count}")

                    else:
                        # (vols_count == 0) โยนไม้ต่อให้ MangaUpdates
                        manga["jikan_status"] = "PENDING_MU" 
                        manga["jp_total_vols"] = 0
                        print(f"   -> Title With No Volume. Passing to MangaUpdates (PENDING_MU)")

                else:
                    manga["jikan_status"] = "PENDING_MU" 
                    manga["jp_total_vols"] = 0
                    print("   -> Not Found in AniList. Passing to MangaUpdates (PENDING_MU)")
            
            elif anilist_res.status_code == 404:
                print("   -> Not Found in AniList (404). Passing to MU")
                manga["jikan_status"] = "PENDING_MU"
                manga["jp_total_vols"] = 0

            elif anilist_res.status_code == 429:
                print("AniList Rate Limit! Sleeping for 10s...")
                time.sleep(10)
                continue
            else:
                print(f"   -> API Error: {anilist_res.status_code}. Passing to MU")
                manga["jikan_status"] = "PENDING_MU"

            # 🌟 รวบคำสั่งอัปเดต DB ไว้ที่เดียว เพื่อป้องกันการเซฟซ้ำซ้อน
            update_res = requests.post(API_UPSERT, json=manga)
            if update_res.status_code == 201:
                print(f"   Save Successfully")
            else:
                print(f"   Save Failed: {update_res.text}")

            time.sleep(2)

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    enrich_with_anilist()