import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

root = Path('data/practices/sources/emep'); now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('ysk', 'pdf', '/tmp/gsd0410-election/decision.pdf', 'https://www.ysk.gov.tr/doc/karar/dosya/563457/2023-418.pdf', 'https://ysk.gov.tr/doc/karar/dosya/563457/2023-418.pdf', '2023-04-06', 'official', 'Yüksek Seçim Kurulu', None, 'YSK 2023/418 kararı'),
    ('party', 'html', '/tmp/gsd0410-election/party.html', 'https://www.emep.org/emek-partisi-yesil-sol-listelerinden-milletvekili-olan-adaylarini-tanitti', 'https://www.emep.org/emek-partisi-yesil-sol-listelerinden-milletvekili-olan-adaylarini-tanitti', '2023-04-18', 'party_publication', 'Emek Partisi', None, 'Yeşil Sol listelerindeki adayların tanıtımı ve seçim bildirgesi'),
]
entries = []
def add(record_kind, **values): entries.append(dict(kind=record_kind, values=values))
for role, typ, path, url, final, date, kind, publisher, author, title in sources:
    raw=Path(path).read_bytes(); sha=hashlib.sha256(raw).hexdigest(); obj=root/'objects'/sha; obj.mkdir(parents=True,exist_ok=True)
    original='original.pdf' if typ=='pdf' else 'original.html.bin'; ident='0410-emep-election-2023-'+role; version=ident+'-v1'
    for name, content in [(original,raw),('readable.html',readable_bytes(raw,typ,legacy=False))]:
        dest=obj/name
        if dest.exists(): assert dest.read_bytes()==content
        else: dest.write_bytes(content)
    add('document',id=ident,party_id='emep',title=title,source_kind=kind)
    add('document_version',id=version,document_id=ident,original_url=url,final_url=final,document_date=date,date_precision='day',date_unknown_reason=None,version_label=title,accessed_at=now,verified_at=now,mime='application/pdf' if typ=='pdf' else 'text/html',sha256=sha,original_path='objects/'+sha+'/'+original,readable_path='objects/'+sha+'/readable.html')
    add('source_attribution',version_id=version,kind=kind,publisher=publisher,author=author,social_handle=None,published_at=date if role=='party' else None,date_precision='day' if role=='party' else 'unknown',public_url=url,basis='Tarihli YSK kararının yayın günü doğrulanmadı; ayrı parti yayını tarihlidir. YSK www TLS bağlantısı kesildi, ysk.gov.tr eşdeğer uç yanıt verdi.')
    if typ=='html':
        view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);add('archive_view',**view)
        text=html_source_text(raw); specs=[('list','Emek Partisi (EMEP), Yeşil Sol Listelerinden seçime giren milletvekili adaylarını tanıttı.','Aday tanıtımı'),('education','Eğitim her kademede parasız, bilimsel, demokratik ve anadilinde olmalıdır.','Seçim bildirgesinde eğitim')]
    else:
        text=pdf_page_text(Path(path),0);specs=[('decision','Seçimlerine parti listeleriyle katılmama, milletvekili aday listesi sunmama kararının verildiği','Partinin kendi listesi hakkındaki YSK kararı')]
    for key,exact,section in specs:
        assert exact in text
        add('passage',id=ident+'-'+key+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=0 if typ=='pdf' else None,printed_page=None)
    print(role,sha,view['view_id'] if typ=='html' else '-')
out=Path(__file__).parent/'election-2023-sources-draft.json'
with out.open('x') as f:
    json.dump(dict(entries=entries,status='source_read_package_pending',note='YSK 6 Nisan kararı EMEP’in kendi listesiyle katılmamasını belirtir; 18 Nisan parti yayını Yeşil Sol listelerindeki adayları ve seçim bildirgesini anlatır. Siyasi mücadele ittifakının sona erdiği veya aday gösterilmediği çıkarılamaz.'),f,ensure_ascii=False,indent=2);f.write('\n')
