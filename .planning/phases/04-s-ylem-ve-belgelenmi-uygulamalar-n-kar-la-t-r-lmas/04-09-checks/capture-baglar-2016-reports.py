from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json,sys
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes
c=Path(__file__).resolve().parent; src=c/'baglar-2016-original.pdf'; raw=src.read_bytes(); digest=sha256(raw).hexdigest()
assert digest=='8364a09ace89fc806e5d65ea578e6eef8054bcaf54f3d41ddf9c7c5e298ffca1'
root=Path('data/practices/sources/dbp'); original=f'objects/{digest}/original.pdf'; readable=f'objects/{digest}/readable.html'
for name,data in [(original,raw),(readable,readable_bytes(raw,'pdf',legacy=False))]:
 path=root/name;path.parent.mkdir(parents=True,exist_ok=True)
 if path.exists():assert path.read_bytes()==data
 else:path.write_bytes(data)
url='https://www.baglar.bel.tr/Content/uploads/650ee114-c24f-482a-b241-4a4036f5aff2.pdf'; now=datetime.now(timezone.utc).isoformat(); doc='0409-baglar-2016-reports';vid=doc+'-v1'
entries=[{'kind':'document','values':dict(id=doc,party_id='dbp',title='Bağlar Belediyesi 2016 meclis kararları derlemesi',source_kind='official')},{'kind':'document_version','values':dict(id=vid,document_id=doc,original_url=url,final_url=url,document_date=None,date_precision='unknown',date_unknown_reason='Derlemenin yayım günü bilinmiyor; karar tarihleri ilgili sayfalarda.',version_label='Özgün erişilen nüsha.',accessed_at=datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),verified_at=now,mime='application/pdf',sha256=digest,original_path=original,readable_path=readable)},{'kind':'source_attribution','values':dict(version_id=vid,publisher='Bağlar Belediye Başkanlığı',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=url,basis='Özgün belediye meclis karar derlemesi ve ilgili karar tarihleri incelendi.')}]
anchors=[(20,'18-file','2016/18','2016/18 meclis kararı'),(20,'18-count','toplam 447\nadet Gıda Tüketim noktaları denetlendi.','Komisyonun denetim sayısı beyanı'),(20,'18-report','el konulup imha edildi.','Komisyonun bildirdiği ürün işlemi'),(20,'18-approval','kabulüne karar verildi.06/01/2016','Komisyon raporunun mecliste kabulü'),(22,'20-file','2016/20','2016/20 meclis kararı'),(22,'20-services','Kardelen Kadın Evi-1’de Psikolojik danışmanlık','Komisyonun bildirdiği danışmanlıklar'),(22,'20-seminars','konulu seminer ve eğitimler verilmektedir.','Komisyonun bildirdiği seminer ve eğitimler'),(22,'20-approval','verildi.07/01/2016','Komisyon raporunun mecliste kabulü')]
for page,key,exact,section in anchors:
 assert exact in pdf_page_text(str(src),page),(page,key,exact)
 entries.append({'kind':'passage','values':dict(id=doc+'-'+key,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page=None)})
out=c/'baglar-2016-reports-source-records.json'
with out.open('x') as f:json.dump({'party_id':'dbp','entries':entries},f,ensure_ascii=False,indent=2);f.write('\n')
print('DBP2016_CAPTURE_OK',digest,len(entries))
