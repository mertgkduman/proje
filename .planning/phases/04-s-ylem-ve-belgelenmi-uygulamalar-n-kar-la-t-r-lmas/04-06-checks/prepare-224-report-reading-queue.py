"""TBMM 224 sayılı rapor için kesintisiz sayfa sırası ve kısmi okuma kaydı."""
import datetime
import hashlib
import json
from pathlib import Path
from arsiv import pdf_page_text

p=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
capture=json.loads((p/'2025-224-report-capture.json').read_text())
raw=Path('data/practices/sources/dem')/capture['original_path']
assert hashlib.sha256(raw.read_bytes()).hexdigest()=='ed1e950a9d23850333dd94cd3fbae9acf4747da5861019c1b14b0ea5ed891bb0'
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
pages=[]
examined=set(range(0,313)) | set(range(906,924)) | set(range(986,1002))
for i in sorted(examined):
 text=pdf_page_text(raw,i)
 assert text.strip()
 pages.append(dict(pdf_page_index=i,printed_page=i-21 if i>=22 else None,text_sha256=hashlib.sha256(text.encode()).hexdigest(),characters=len(text)))
assert 'DEM PARTİ MUHALEFET ŞERHİ' in pdf_page_text(raw,986)
assert 'Adalet KAYA' in pdf_page_text(raw,1001) and 'Özgül SAKİ' in pdf_page_text(raw,1001)
queue=[]
i=0
while i<1054:
 state='examined' if i in examined else 'pending'; end=i
 while end+1<1054 and (end+1 in examined)==(state=='examined') and end-i<19 and end+1 not in (20,36,40,54,57,61,69,81,97,105,113,121,129,137,145,153,161,169,177,185,193,201,209,217,225,249,257,265,273,281,289,297,305,906,924):end+=1
 row=dict(first=i,last=end,state=state)
 if state=='examined':row.update(review_file=('2025-224-kapak-icindekiler.md' if i<20 else '2025-224-baskan-sunus.md' if i<36 else '2025-224-diger-onergeler.md' if 40<=i<54 else '2025-224-komisyon-uyeleri.md' if 57<=i<61 else '2025-224-calisma-takvimi.md' if 61<=i<69 else '2025-224-istanbul-ziyaret.md' if 69<=i<81 else '2025-224-bolge-ziyaret.md' if 81<=i<97 else '2025-224-belge-sunumu.md' if 97<=i<105 else '2025-224-kavramsal-baslangic.md' if 105<=i<113 else '2025-224-esitlik-kaynaklari.md' if 113<=i<121 else '2025-224-ayrimcilik-turleri.md' if 121<=i<129 else '2025-224-aile-egitim.md' if 129<=i<137 else '2025-224-calisma.md' if 137<=i<145 else '2025-224-istihdam-verileri.md' if 145<=i<153 else '2025-224-medya-spor-siddet.md' if 153<=i<161 else '2025-224-siddet-cercevesi.md' if 161<=i<169 else '2025-224-siddet-bicimleri.md' if 169<=i<177 else '2025-224-risk-afet.md' if 177<=i<185 else '2025-224-yayginlik.md' if 185<=i<193 else '2025-224-arastirma-isyerleri.md' if 193<=i<201 else '2025-224-medya-sunumlari.md' if 201<=i<209 else '2025-224-medya-toplum.md' if 209<=i<217 else '2025-224-tespit-oneriler.md' if 906<=i<924 else '2025-224-dem-serhi-reading.md'),text_checked_at=now,pages=[x for x in pages if i<=x['pdf_page_index']<=end])
 if state=='examined' and 217<=i<249: row['review_file']='2025-224-evlilik-guclenme.md'
 if state=='examined' and 249<=i<257: row['review_file']='2025-224-uluslararasi-belgeler.md'
 if state=='examined' and 257<=i<265: row['review_file']='2025-224-ulusal-mevzuat.md'
 if state=='examined' and 265<=i<273: row['review_file']='2025-224-usul-medeni-6284.md'
 if state=='examined' and 273<=i<281: row['review_file']='2025-224-6284-cocuk-koruma.md'
 if state=='examined' and 281<=i<289: row['review_file']='2025-224-infaz-calisma.md'
 if state=='examined' and 289<=i<297: row['review_file']='2025-224-istihdam-kurumlar.md'
 if state=='examined' and 297<=i<305: row['review_file']='2025-224-magdur-hizmetleri.md'
 if state=='examined' and 305<=i<313: row['review_file']='2025-224-koruma-yonetmelikleri.md'
 queue.append(row);i=end+1
assert [x for r in queue for x in range(r['first'],r['last']+1)]==list(range(1054))
result=dict(version=1,source_sha256=capture['sha256'],total_pages=1054,examined_pages=347,pending_pages=707,queue=queue,limitations='Kapak, içindekiler ve liste sayfaları, başkan sunuşu, altı önerge, üyeler, toplantı ve ziyaret kesitleri, kavramsal giriş, uluslararası belgeler ve ulusal mevzuattan seçili sayfalar, ortak tespit ve öneriler, DEM şerhi ve takdim/kuruluş sayfaları incelendi; diğer bölümler okunmadı, sonuçların uygulanması ve hukuki etki doğrulanmadı.')
(p/'2025-224-report-reading-queue.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('224_REPORT_QUEUE_EXACT',len(queue),'examined',347,'pending',707)
