import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes
capture=Path('/tmp/gsd0410-ipa-akdeniz.pdf');raw=capture.read_bytes();sha=hashlib.sha256(raw).hexdigest()
exact='22 Kasım 2020’de\ngerçekleşen Emek Partisi’nin 9. Genel\nKongresinde Genel Başkan seçildi.';assert exact in pdf_page_text(capture,25)
url='https://ipa.istanbul/uploads/guvencesizlik-yeni-esitsizlikler-ve-cozum-yollari-konferansi-ozet-kitabi-95811-c45b3b4c.pdf';root=Path('data/practices/sources/emep');obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
ident='0410-ipa-2020-congress-date';access=datetime.fromtimestamp(capture.stat().st_mtime,timezone.utc).isoformat(timespec='seconds')
rows=[('document',dict(id=ident,party_id='emep',title='İPA konferans özet kitabı — Ercüment Akdeniz biyografisi',source_kind='independent_report')),
('document_version',dict(id=ident+'-v1',document_id=ident,original_url=url,final_url=url,document_date=None,version_label='İPA konferans özet kitabı; yayın günü doğrulanmadı',accessed_at=access,verified_at=datetime.now(timezone.utc).isoformat(timespec='seconds'),mime='application/pdf',sha256=sha,original_path='objects/'+sha+'/original.pdf',readable_path='objects/'+sha+'/readable.html',date_precision='unknown',date_unknown_reason='Raporun kesin yayın günü doğrulanmadı; olay tarihi belge tarihi değildir.')),
('passage',dict(id=ident+'-p',version_id=ident+'-v1',exact=exact,prefix=None,suffix=None,article=None,section='Ercüment Akdeniz biyografisi',pdf_page_index=25,printed_page='46')),
('source_attribution',dict(version_id=ident+'-v1',kind='other',publisher='İstanbul Planlama Ajansı',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='İPA yayımladığı konferans özet kitabında biyografi ve seçimin gününü aktarıyor; kitabın kesin yayım günü doğrulanmadı.'))]
out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-10-checks/ipa-event-date-source-draft.json');out.write_text(json.dumps(dict(status='draft_unvalidated',entries=[dict(kind=k,values=v) for k,v in rows],note='İPA biyografisindeki tarih bağımsız kurum bağlamıdır; olay tarihi yayın günü varsayılmadan belirlenir.'),ensure_ascii=False,indent=2)+'\n');print(sha)
