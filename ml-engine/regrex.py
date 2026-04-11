import json
import re

# จำลองข้อมูล JSON ที่คุณ Scrape มาได้
raw_json = {"url":"https://www.phoenixnext.com/mgm00289-01.html","product_id":"MGM00289-01","name":"(มังงะ) เพื่อนสะดวกคิส มิตรสะดวกเลิฟ เล่ม 1","image_url":"https://www.phoenixnext.com/media/catalog/product/m/g/mgm00289-01.jpg","price":185,"list_price":185,"price_currency_code":"THB","availability":"InStock","description":"&lt;p&gt;&lt;span style=\"font-size: 20px;\"&gt;รายละเอียดมังงะ “เพื่อนสะดวกคิส มิตรสะดวกเลิฟ เล่ม 1” (Koutsugou Semi-Friend Vol.1)&lt;/p&gt;&lt;p&gt;...เรื่องย่อ...&lt;br /&gt;.&lt;br /&gt;ซูนะ สาว ม.ปลายขี้อายต้องมาอยู่ร่วมหอกับ รุกะ สาวห้าวที่ขาดคู่ขา (sefure) ไม่ได้ ซูนะไม่อยากให้รุกะพาผู้หญิงคนอื่นเข้ามาจู๋จี๋ในห้อง แต่ก็ไม่อยากห้ามรุกะ เลยเสนอตัวขอเป็นคู่ขาของรุกะเองซะอย่างนั้น!?&lt;/p&gt;","review_count":1,"rating_value":5,"tags1":["add-to-cart"],"category":["/Manga","/All Series/เพื่อนสะดวกคิส มิตรสะดวกเลิฟ","/Manga/Comedy","/Manga/Romantic","/Manga/School","/Manga/Slice of life","/Manga/Yuri","/Yuri","/Yuri/เพื่อนสะดวกคิส มิตรสะดวกเลิฟ","/New Release"],"category_id":["2","37","1448","64","42","40","972","479","61","1449","171"],"parent_category_id":["1","2","112","37","61"],"custom_fields":{"stock_status":"Ready","barcode":"9786166244991"}}

#{"url":"https://www.phoenixnext.com/ln0795-01.html","product_id":"LN0795-01","name":"(LN) การปฏิวัติเวทมนตร์ขององค์หญิงเกิดใหม่กับยัยคุณหนูยอดอัจฉริยะ เล่ม 8","image_url":"https://www.phoenixnext.com/media/catalog/product/l/n/ln0795-01.jpg","price":300,"list_price":300,"price_currency_code":"THB","availability":"InStock","description":"&lt;p&gt;&lt;span style=\"font-size: 20px;\"&gt;รายละเอียดไลท์โนเวล “การปฏิวัติเวทมนตร์ขององค์หญิงเกิดใหม่กับยัยคุณหนูยอดอัจฉริยะ เล่ม 8” (Tensei Oujo to Tensai Reijou no Mahou Kakumei Vol.8 )&lt;/p&gt;&lt;p&gt;…เรื่องย่อ…&lt;br /&gt;.&lt;br /&gt;ระหว่างที่อานิสทำหน้าที่เป็นผู้รับผิดชอบการก่อสร้างนครศาสตร์เวท &lt;br /&gt;เรนนีก็ส่งจดหมายมาจากพระราชวัง ใจความคือยูฟีกำลังพักฟื้น &lt;br /&gt;และเรื่องนั้นเกี่ยวพันถึงแผนการของขุนนางภาคตะวันตก—&lt;/p&gt;&lt;p&gt;“ฉันอดคิดไม่ได้เลยว่าเพราะอะไรถึงต้องปกป้องประเทศที่ทำร้ายท่านด้วย” &lt;br /&gt;“ขยี้ภาคตะวันตกทิ้งเลยดีมั้ย”&lt;/p&gt;&lt;p&gt;เกิดขุมกำลังใหม่ต่อต้านการปฏิวัติของทั้งสองคนซึ่งๆหน้า &lt;br /&gt;ขณะยูฟีแสวงหาเหตุผลในการขึ้นเป็นราชินี &lt;br /&gt;อานิสซึ่งผลักภาระราชินีให้เธอจะให้คำตอบเช่นไรในการก้าวสู่อนาคต!?&lt;br /&gt;นี่คือการเผชิญหน้าระหว่างคนทั้งสองซึ่งคำนึงถึงอนาคตกับขุนนางที่ยึดติดกับอดีต&lt;br /&gt;การต่อสู้อันเดิมพันด้วยศักดิ์ศรีกำลังจะเปิดฉากขึ้นในนิยายแฟนตาซียูริในวัง!&lt;/p&gt;","review_count":0,"rating_value":0,"tags1":["add-to-cart"],"category":["/Light Novel","/All Series/การปฏิวัติเวทมนตร์ขององค์หญิงเกิดใหม่กับยัยคุณหนูยอดอัจฉริยะ","/Light Novel/Fantasy","/Light Novel/Yuri","/Yuri","/Yuri/การปฏิวัติเวทมนตร์ขององค์หญิงเกิดใหม่กับยัยคุณหนูยอดอัจฉริยะ","/New Release"],"category_id":["2","29","818","30","476","61","878","171"],"parent_category_id":["1","2","112","29","61"],"custom_fields":{"stock_status":"Ready","barcode":"9786166244397"}}
#{"url":"https://www.phoenixnext.com/mgm00289-01.html","product_id":"MGM00289-01","name":"(มังงะ) เพื่อนสะดวกคิส มิตรสะดวกเลิฟ เล่ม 1","image_url":"https://www.phoenixnext.com/media/catalog/product/m/g/mgm00289-01.jpg","price":185,"list_price":185,"price_currency_code":"THB","availability":"InStock","description":"&lt;p&gt;&lt;span style=\"font-size: 20px;\"&gt;รายละเอียดมังงะ “เพื่อนสะดวกคิส มิตรสะดวกเลิฟ เล่ม 1” (Koutsugou Semi-Friend Vol.1)&lt;/p&gt;&lt;p&gt;...เรื่องย่อ...&lt;br /&gt;.&lt;br /&gt;ซูนะ สาว ม.ปลายขี้อายต้องมาอยู่ร่วมหอกับ รุกะ สาวห้าวที่ขาดคู่ขา (sefure) ไม่ได้ ซูนะไม่อยากให้รุกะพาผู้หญิงคนอื่นเข้ามาจู๋จี๋ในห้อง แต่ก็ไม่อยากห้ามรุกะ เลยเสนอตัวขอเป็นคู่ขาของรุกะเองซะอย่างนั้น!?&lt;/p&gt;","review_count":1,"rating_value":5,"tags1":["add-to-cart"],"category":["/Manga","/All Series/เพื่อนสะดวกคิส มิตรสะดวกเลิฟ","/Manga/Comedy","/Manga/Romantic","/Manga/School","/Manga/Slice of life","/Manga/Yuri","/Yuri","/Yuri/เพื่อนสะดวกคิส มิตรสะดวกเลิฟ","/New Release"],"category_id":["2","37","1448","64","42","40","972","479","61","1449","171"],"parent_category_id":["1","2","112","37","61"],"custom_fields":{"stock_status":"Ready","barcode":"9786166244991"}}
print("🔍 เริ่มกระบวนการทำความสะอาดข้อมูล (Data Cleansing)...")

# 1. ทำความสะอาดชื่อไทย และหาเลขเล่ม
# ใช้ Regex ลบคำว่า "(มังงะ)" หรือ "(ไลท์โนเวล)" ออก
clean_th_name = re.sub(r'^\(มังงะ\) |^\(LN\) ', '', raw_json['name'])

# แยกชื่อเรื่องกับเลขเล่มออกจากกัน
vol_match = re.search(r'(.*?)\s+เล่ม\s*(\d+)', clean_th_name)
if vol_match:
    th_title = vol_match.group(1).strip()
    vol_num = int(vol_match.group(2))
else:
    th_title = clean_th_name
    vol_num = 1 # ถ้าไม่มีเขียนเล่มที่ มักจะเป็นเล่มเดียวจบหรือเล่ม 1

# 2. แงะชื่อภาษาอังกฤษ/โรมาจิ ออกจาก Description
# หาข้อความที่อยู่ในวงเล็บ ( ... ) ที่มีคำว่า Vol.
en_match = re.search(r'\((.+?)\s*[Vv]ol\.?\s*\d+\s*\)', raw_json['description'])
if en_match:
    en_title = en_match.group(1).strip()
else:
    en_title = "ไม่พบข้อมูลภาษาอังกฤษ"

# 3. สรุปผลลัพธ์
print("-" * 30)
print(f"🇹🇭 ชื่อไทย: {th_title}")
print(f"🇬🇧 ชื่อโรมาจิ: {en_title}")
print(f"📚 เล่มที่: {vol_num}")
print(f"🛒 สถานะสินค้า: {raw_json['availability']}")
print("-" * 30)