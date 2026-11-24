import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=68000,80000
assert len(body)==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
out={'tranche_id':'0410-emep-api-292','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [68000,80000) karakter aralığı okundu.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Programın son kısmında eşit ücret, taşeronluğun kaldırılması, tarım işçisi güvencesi, çevre ve ormanların korunması, nükleer santrallerin yasaklanması, toplumsal cinsiyet eşitliği ve sığınma merkezleri, göçmenlerin hakları ve yurtdışında yaşayan emekçiler hakkında talepler yer alır. Ardından tüzük başlar: parti adı ve merkezi, amaç ile örgütlenme ilkelerinin ilk dört maddesi okunur; aralık devam eden örgütlenme ilkeleri içinde kesilir.','limitations':['Program talepleri veya tüzük hükümleri uygulanmış sonuç olarak sunulmaz; belge kabul tarihi ayrıca doğrulanmadı.','80000 sonrası okunmadı.'],'next_unread':{'post_id':3294,'start_char':end,'total_char':len(body)},'closure_refs':[]}
with (c/'party-api-292-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API292_READING_OK',end-start,out['slice_sha256'])
