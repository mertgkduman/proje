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
examined=set(range(0,553)) | set(range(906,924)) | set(range(986,1002))
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
 while end+1<1054 and (end+1 in examined)==(state=='examined') and end-i<19 and end+1 not in (20,36,40,54,57,61,69,81,97,105,113,121,129,137,145,153,161,169,177,185,193,201,209,217,225,249,257,265,273,281,289,297,305,313,321,329,337,345,353,361,369,377,385,393,401,409,417,425,433,441,449,457,465,473,481,489,497,505,513,521,529,537,545,906,924):end+=1
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
 if state=='examined' and 313<=i<321: row['review_file']='2025-224-genelgeler.md'
 if state=='examined' and 321<=i<329: row['review_file']='2025-224-siddetle-mucadele-genelgeler.md'
 if state=='examined' and 329<=i<337: row['review_file']='2025-224-istihdam-sorusturma.md'
 if state=='examined' and 337<=i<345: row['review_file']='2025-224-mahkeme-kararlari.md'
 if state=='examined' and 345<=i<353: row['review_file']='2025-224-aym-kararlari.md'
 if state=='examined' and 353<=i<361: row['review_file']='2025-224-aym-yargitay.md'
 if state=='examined' and 361<=i<369: row['review_file']='2025-224-yargi-kdk-tihek.md'
 if state=='examined' and 369<=i<377: row['review_file']='2025-224-kurumsal-tbmm.md'
 if state=='examined' and 377<=i<385: row['review_file']='2025-224-plan-butce.md'
 if state=='examined' and 385<=i<393: row['review_file']='2025-224-ddk-ashb.md'
 if state=='examined' and 393<=i<401: row['review_file']='2025-224-kalkinma-tedbirleri.md'
 if state=='examined' and 401<=i<409: row['review_file']='2025-224-eylem-siginma.md'
 if state=='examined' and 409<=i<417: row['review_file']='2025-224-hat-protokol.md'
 if state=='examined' and 417<=i<425: row['review_file']='2025-224-isbirligi-veri.md'
 if state=='examined' and 425<=i<433: row['review_file']='2025-224-bilinc-gocmen.md'
 if state=='examined' and 433<=i<441: row['review_file']='2025-224-afet-hukuk.md'
 if state=='examined' and 441<=i<449: row['review_file']='2025-224-aile-hizmet.md'
 if state=='examined' and 449<=i<457: row['review_file']='2025-224-cocuk-hizmet.md'
 if state=='examined' and 457<=i<465: row['review_file']='2025-224-engellilik-yardim.md'
 if state=='examined' and 465<=i<473: row['review_file']='2025-224-adalet-temsil.md'
 if state=='examined' and 473<=i<481: row['review_file']='2025-224-adalet-plan.md'
 if state=='examined' and 481<=i<489: row['review_file']='2025-224-adalet-uygulama.md'
 if state=='examined' and 489<=i<497: row['review_file']='2025-224-adli-surec.md'
 if state=='examined' and 497<=i<505: row['review_file']='2025-224-adli-kurum.md'
 if state=='examined' and 505<=i<513: row['review_file']='2025-224-adli-proje.md'
 if state=='examined' and 513<=i<521: row['review_file']='2025-224-cocuk-afet.md'
 if state=='examined' and 521<=i<529: row['review_file']='2025-224-koruma-esgudum.md'
 if state=='examined' and 529<=i<537: row['review_file']='2025-224-mevzuat-infaz.md'
 if state=='examined' and 537<=i<545: row['review_file']='2025-224-infaz-veri.md'
 if state=='examined' and 545<=i<553: row['review_file']='2025-224-personel-egitim.md'
 queue.append(row);i=end+1
assert [x for r in queue for x in range(r['first'],r['last']+1)]==list(range(1054))
result=dict(version=1,source_sha256=capture['sha256'],total_pages=1054,examined_pages=587,pending_pages=467,queue=queue,limitations='Kapak, içindekiler ve liste sayfaları, başkan sunuşu, altı önerge, üyeler, toplantı ve ziyaret kesitleri, kavramsal giriş, uluslararası belgeler, ulusal mevzuat, mahkeme kararları ve kurumsal yapıdan seçili sayfalar, ortak tespit ve öneriler, DEM şerhi ve takdim/kuruluş sayfaları incelendi; diğer bölümler okunmadı, sonuçların uygulanması ve hukuki etki doğrulanmadı.')
(p/'2025-224-report-reading-queue.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print('224_REPORT_QUEUE_EXACT',len(queue),'examined',587,'pending',467)
