import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=92000,104000
assert len(body)==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
out={'tranche_id':'0410-emep-api-294','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [92000,104000) karakter aralığı okundu.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Tüzüğün 28–50. maddelerinde parti organları, genel kongre ve delege koşulları, genel başkan ve GYK, MYK ve disiplin kurulları, il ve ilçe örgütleri düzenlenir. Genel başkanın partiyi temsil yetkisi, olağan kongrenin üç yılda bir toplanması ve olağanüstü kongre için delege istemi gibi hükümler metne aittir. 37. maddenin görünen cümlesi program ve kararların uygulanmaması ifadesinde kesilip sonraki paragrafa atlar; eksik hüküm tamamlanmadı. Aralık 50. maddenin içinde kesilir.','limitations':['Gövdenin 37. madde kısmı görünen biçimiyle eksiktir; kayıp sözcük veya yaptırım uydurulmadı.','Belgenin belirli bir tarihteki yürürlüğü ve 104000 sonrası ayrı araştırma ister.'],'next_unread':{'post_id':3294,'start_char':end,'total_char':len(body)},'closure_refs':[]}
with (c/'party-api-294-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API294_READING_OK',end-start,out['slice_sha256'])
