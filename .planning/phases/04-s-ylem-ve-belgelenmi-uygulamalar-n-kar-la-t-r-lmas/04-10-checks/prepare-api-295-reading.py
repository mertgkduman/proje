import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
c=Path(__file__).resolve().parent;page=c/'party-api-pages/page-25.json';p=next(x for x in json.loads(page.read_text()) if x['id']==3294);body=p['content']['rendered'];start,end=104000,len(body)
assert end==115954
digest=lambda s:hashlib.sha256(s.encode()).hexdigest()
first=json.loads((c/'party-api-286-source-reading.json').read_text());a=[next(v for v in first['parts'] if v['post_id']==3294)]+[json.loads((c/f'party-api-{i}-source-reading.json').read_text()) for i in range(287,295)]
assert all(v['body_sha256']==digest(body) and v['total_char']==end for v in a)
assert a[0]['start_char']==0 and a[-1]['end_char']==start and all(a[i]['end_char']==a[i+1]['start_char'] for i in range(len(a)-1))
out={'tranche_id':'0410-emep-api-295','read_at':datetime.now(timezone.utc).isoformat(),'method':'Özgün Türkçe HTML gövdesinin yarı açık [104000,115954) son aralığı okundu; 286–294 önceki aralıkların sürekliliği ve tam gövde hashleri kontrol edildi.','post_id':3294,'url':p['link'],'api_date':p['date'],'page':str(page),'body_sha256':digest(body),'start_char':start,'end_char':end,'total_char':len(body),'slice_sha256':digest(body[start:end]),'reading_note':'Tüzüğün son bölümünde ilçe kongresi ve yönetimi, büro ve temsilcilikler, yurtdışı temsilciliği, gençlik ve kadın örgütleri, TBMM parti grubu, grup kurulamayan durumlar ve yerel meclis grupları düzenlenir. Metin belediye başkanlarının yürütmeyle ilgili yasal görevlerine bağlayıcı grup kararı alınamayacağını belirtir. Son genel hükümler yönetimlerin boşalması, aday belirleme ve mali kayıtları işler; gövde 25 Kasım 1996 kuruluş bilgisinde biter.','limitations':['Ulaşılan birleştirilmiş program-tüzük gövdesi tamamen okundu; 37. madde içindeki kaynak kesintisi 294 makbuzunda açık kalır.','Yürürlük ve ara değişiklik tarihleri, bireysel parti ya da belediye işlemleri bu hükümlerden otomatik çıkarılmaz.','Tek belgenin okunması parti veya faz araştırmasının kapanması değildir.'],'next_unread':'API sırasındaki 3294 sonrası sonraki gövde.','closure_refs':[]}
with (c/'party-api-295-source-reading.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('API295_READING_OK',end-start,out['slice_sha256'])
