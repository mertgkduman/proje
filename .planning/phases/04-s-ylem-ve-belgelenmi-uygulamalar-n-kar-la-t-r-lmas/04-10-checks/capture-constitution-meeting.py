import hashlib, json, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, 'src')
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

D = Path(__file__).parent
root = Path('data/practices/sources/emep')
now = datetime.now(timezone.utc).isoformat(timespec='seconds')
sources = [
    ('tbmm', 'constitution-meeting-20240605-tbmm.html', 'https://www.tbmm.gov.tr/Haber/Detay?Id=9daf2d55-dd3c-46a6-b8b9-018fe8a08b30', '2024-06-05', 'Türkiye Büyük Millet Meclisi', 'official', "Meclis Başkanlığı makamında yaklaşık 40 dakika süren kabule, Aslan'ın yanı sıra EMEP İstanbul Milletvekili İskender Bayhan ile Gaziantep Milletvekili Sevda Karaca Demir de katıldı."),
    ('emep', 'constitution-meeting-20240605-emep.html', 'https://www.emep.org/meclis-baskani-numan-kurtulmus-anayasa-degisikligi-gundemiyle-emep-heyetiyle-gorustu-demokratik-anayasa-kurucu-meclisle-olur', '2024-06-06', 'Emek Partisi', 'party_publication', 'Görüşmeye EMEP Genel Başkanı Seyit Aslan, İstanbul Milletvekili İskender Bayhan ve Antep Milletvekili Sevda Karaca katıldı.'),
]
entries=[]
for role,filename,url,date,publisher,kind,exact in sources:
    raw=(D/filename).read_bytes(); digest=hashlib.sha256(raw).hexdigest(); obj=root/'objects'/digest; obj.mkdir(parents=True,exist_ok=True)
    for name,content in [('original.html.bin',raw),('readable.html',readable_bytes(raw,'html',legacy=False))]:
        path=obj/name
        if path.exists(): assert path.read_bytes()==content
        else: path.write_bytes(content)
    doc='0410-emep-constitution-meeting-'+role; version=doc+'-v1'
    entries.append(dict(kind='document',values=dict(id=doc,party_id='emep',title='EMEP heyetinin TBMM Başkanı ile anayasa görüşmesi: '+publisher,source_kind='official' if role=='tbmm' else 'party')))
    entries.append(dict(kind='document_version',values=dict(id=version,document_id=doc,original_url=url,final_url=url,document_date=date,date_precision='day',date_unknown_reason=None,version_label='Özgün yayın',accessed_at=now,verified_at=now,mime='text/html',sha256=digest,original_path='objects/'+digest+'/original.html.bin',readable_path='objects/'+digest+'/readable.html')))
    view=build_view(raw,url,root,fetch_assets=False,http_charset='utf-8');view['version_id']=version;validate_view(root,view);entries.append(dict(kind='archive_view',values=view))
    assert exact in html_source_text(raw)
    entries.append(dict(kind='passage',values=dict(id=doc+'-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Görüşmeye katılım',pdf_page_index=None,printed_page=None)))
    entries.append(dict(kind='source_attribution',values=dict(version_id=version,kind=kind,publisher=publisher,author=None,social_handle=None,published_at=date,date_precision='day',public_url=url,basis='Kurumun özgün yayını; görüşme günü ve ertesi gün parti yayını ayrı.')))
    print(role,digest,view['view_id'])
with (D/'constitution-meeting-20240605-source-draft.json').open('x') as f:
    json.dump(dict(status='source_read_package_pending',entries=entries,note='5 Haziran 2024 kabul ve görüşme, kurucu meclis hakkındaki görüş ve herhangi bir anayasa değişikliği sonucu ayrı tutulur.'),f,ensure_ascii=False,indent=2);f.write('\n')
