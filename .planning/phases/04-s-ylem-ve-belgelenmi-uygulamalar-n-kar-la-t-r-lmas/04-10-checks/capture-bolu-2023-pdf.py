import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes
capture=Path('/tmp/gsd0410-bolu-20231216.pdf');raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest()
exact='Disiplin Kurulu; Süreyya Demir, Ay-\nnur Kaman, Umut Çelikbaş';assert exact in pdf_page_text(capture,4)
url='https://koroglugazetesicom.teimg.com/koroglugazetesi-com/uploads/2023/12/gazete/16122023.pdf';root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
ident='0410-emep-2023-bolu-pdf';access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='emep',title='Köroğlu gazetesi 16 Aralık 2023, Bolu il kongresi haberi',source_kind='journalism')),
('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date='2023-12-16',version_label='16 Aralık 2023 tarihli gazete; olay günü ayrıca araştırılıyor',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='application/pdf',sha256=sha,original_path='objects/'+sha+'/original.pdf',readable_path='objects/'+sha+'/readable.html',date_precision='day',date_unknown_reason=None)),
('passage',dict(id=ident+'-discipline-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='EMEP Bolu il kongresi',pdf_page_index=4,printed_page='5')),
('source_attribution',dict(version_id=ident+'-v1',kind='journalism',publisher='Köroğlu Gazetesi',author='Yasin Celal Torun',social_handle=None,published_at='2023-12-16',date_precision='day',public_url=url,basis='Gazete sayfa başlığı tarihi ve haber sonu yazar künyesi özgün PDF sayfa 5 üzerinde okundu.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/bolu-2023-pdf-source-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',entries=[dict(kind=k,values=v) for k,v in rows],note='2020 yerel haberle bazı yönetici isimleri tekrar ediyor ancak disiplin listesi farklı; olayların ilişkisi ve kongre günü ayrı araştırılmalı.'),ensure_ascii=False,indent=2)+'\n');print(sha)
