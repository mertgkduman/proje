import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import pdf_page_text, readable_bytes
raw_path=Path('/tmp/gsd0410-ysk-4219-2019.pdf')
raw=raw_path.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
assert sha=='0f5d25e653bee1b32586c9f1e44c9d0cc639af230f57ed17578d238d2da5c249'
root=Path('data/practices/sources/emep'); obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
for name, content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 dest=obj/name
 if dest.exists(): assert dest.read_bytes()==content
 else: dest.write_bytes(content)
url='https://cdnuploads.aa.com.tr/uploads/userFiles/d7949134-ce71-4b68-82e5-458179071638/YSK-Istanbul-gerekceli-karar.pdf'
now=datetime.now(timezone.utc).isoformat(timespec='seconds');ident='0410-emep-ysk2019-4219-precedent';v=ident+'-v1'
p1='Emek Partisi Genel Başkan Yardımcısı Selma GÜRKAN';p2='27/04/2009 tarih\nve 1616 sayılı YSK kararı'
assert p1 in pdf_page_text(raw_path,241)
assert p2 in pdf_page_text(raw_path,242)
entries=[
 dict(kind='document',values=dict(id=ident,party_id='emep',title='YSK 2019/4219 karşı oyunda 2009 Yaylakonak itirazı',source_kind='official')),
 dict(kind='document_version',values=dict(id=v,document_id=ident,original_url=url,final_url=url,document_date='2019-05-06',date_precision='day',date_unknown_reason=None,version_label='YSK İstanbul gerekçeli kararı, karşı oy içinde 2009/1616 atfı',accessed_at=now,verified_at=now,mime='application/pdf',sha256=sha,original_path='objects/'+sha+'/original.pdf',readable_path='objects/'+sha+'/readable.html')),
 dict(kind='source_attribution',values=dict(version_id=v,kind='official',publisher='Yüksek Seçim Kurulu',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='Anadolu Ajansı sunucusunda YSK 2019/4219 gerekçeli kararının PDF nüshası; karar günü ve karşı oy metni ayrıdır.')),
 dict(kind='passage',values=dict(id=ident+'-applicant-p',version_id=v,exact=p1,prefix=None,suffix=None,article=None,section='Karşı oy içinde 2009 başvuru sahibi',pdf_page_index=241,printed_page=None)),
 dict(kind='passage',values=dict(id=ident+'-result-p',version_id=v,exact=p2,prefix=None,suffix=None,article=None,section='Karşı oy içinde 2009/1616 ret kararı atfı',pdf_page_index=242,printed_page=None)),
]
out=Path(__file__).parent/'ysk2009-precedent-source-draft.json'
with out.open('x') as f:
 json.dump(dict(entries=entries,status='source_read_partial',note='2019/4219 karşı oy gerekçesinde Selma Gürkan’ın Yaylakonak itirazı ve 27 Nisan 2009 YSK 1616 ret kararına atıf; 2009 karar aslı ve itiraz başvuru tarihi ayrıca araştırılıyor.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('YSK_PRECEDENT_SOURCE',sha)
