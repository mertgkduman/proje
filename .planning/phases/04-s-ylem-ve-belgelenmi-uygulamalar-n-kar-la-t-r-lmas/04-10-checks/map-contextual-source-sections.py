import datetime, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path

class Text(HTMLParser):
    def __init__(self): super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self,tag,attrs): self.skip+=tag in ('script','style','nav','footer','header')
    def handle_endtag(self,tag): self.skip-=tag in ('script','style','nav','footer','header')
    def handle_data(self,data):
        if not self.skip and data.strip(): self.parts.append(data.strip())

source=Path('data/objects/16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329/original.html.bin')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329'
p=Text();p.feed(source.read_text()); text=re.sub(r'\s+',' ',' '.join(p.parts))
anchors={
 'inventory-9eb47b0f64ca01253fbe4d25fa8597608b1e477ec03bda30546387c80d882ed0':['44-Olağan il kongreleri','Bu süre 3 yıldan fazla olamaz'],
 'inventory-9bbaa1f15a7887620c9e9e896473c4bfd39abedd08b336cbcaf1def91de0a058':['A. İŞÇİ SINIFI VE BURJUVAZİ'],
 'inventory-16866c43274871d2d805a84ee0875f2d6b3b3b8188856bfec44ad9ca8b5f8d3b':['B. TEKELLER VE EMPERYALİZM'],
 'inventory-1031555986bca399cbe14a19315780d1b3b7f7d6eae62935d2c8c63607b04ada':['C. EMPERYALİZM, DÜNYA PROLETER DEVRİMİ VE ULUSAL HAREKETLER'],
 'inventory-b3099ceef780ec09a4092c1cad4f4559f289f16e8658217e888a393d821581c5':['D. EKİM DEVRİMİ, SOSYALİST İNŞA VE KARŞI-DEVRİM'],
 'inventory-df12b681b11bc043c962bf004b89565769b365e5197e6581dd1a7f806e3de274':['E. KESKİNLEŞEN ÇELİŞKİLER, DEVRİMİN ARTAN OLANAKLARI'],
 'inventory-498f397a48db2d04162b842670d758c68d3516b844ff41c75d84781f8fcd706d':['F. TÜRKİYE DEVRİMİ'],
 'inventory-e20f7b4129f1fbd43ea56de4ac5e7a4afe20140a0a465e5e42b7d2e0e94387df':['G. A -Halk İktidarı ve Halk Demokrasisi İçin'],
 'inventory-5781cea3737368f2ea82bc7da25acbbe47bc2487e56820e874e1202e2f05cfae':['İşini kaybeden emekçiye ve yaşamını kaybeden emekçinin'],
 'inventory-7385eab2aa9fd1b5e43df771cb8c3ff9f051be6939576c3acdb26be98ec0d504':['Halk ve kişi sağlığının dokunulmaz bir'],
 'inventory-71922232be0fdd81455e59d0d77731e7203cbd33fdeaa295107009dae9be4946':['Okul öncesi ve üniversite dahil bütün eğitimin'],
 'inventory-fe7eaf57921882ebc085cf525b0152be0c8f2a0546dbbcb6fe0661f7fadcee2d':['Yeterli sayıda parasız kreş ve anaokulu.'],
 'inventory-c911f5e03c4c2707a5c7376e3837aff093aebe893104f7dba7c464a7392e44e8':['Okul öncesi ve üniversite dahil bütün eğitimin','Yeterli sayıda parasız kreş ve anaokulu.','Başta gençler olmak üzere, herkese yüksek öğrenim'],
 'inventory-68d393313810e782414b30d8aee36068a43fb908a4ab9ab695d0c687d242111d':['devletin tüm dinsel kurumlarının feshi']
}
for values in anchors.values():
    for a in values: assert text.count(a)==1,(a,text.count(a))
queue=Path('data/practices/04-emep-tranches.json');data=json.loads(queue.read_text());pending=[r for r in data['source_queue'] if r['state']=='pending'];assert {r['inventory_id'] for r in pending}==set(anchors)
now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');matches=[]
for row in pending:
    receipts=['charter-full-reading.json'] if row['source_role']=='charter' else ['program-first-reading.json','program-second-reading.json','program-third-reading.json']
    matches.append(dict(inventory_id=row['inventory_id'],anchors=[dict(text=a,normalized_offset=text.index(a)) for a in anchors[row['inventory_id']]],reading_receipts=receipts))
    row.update(state='read',processed_at=now,reading_receipts=receipts)
out=Path(__file__).parent/'read-contextual-sections-receipt.json';assert not out.exists();out.write_text(json.dumps(dict(source_version='0208-emep-program-charter-v1',method='Daha önce okunan metindeki biçimlenmiş başlık veya tanımlı bölüm, tekil bağlam çıpalarıyla eşlendi.',matches=matches,note='Kaynak metni okundu; olay araştırması ve 610 kapsam hücresi açık.',recorded_at=now),ensure_ascii=False,indent=2)+'\n');queue.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('CONTEXTUAL_SOURCE_SECTIONS_READ',len(matches))
