"""Archive the SPK payment decision and the reported first payments."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

checks,stage=map(Path,sys.argv[1:])
root=Path('data/practices/sources/saadet')
now=datetime.now(timezone.utc).isoformat()
entries,paths=[],set()


def add(table,**row):
    entries.append(dict(kind=table,values=row))


def save(relative,raw):
    p=root/relative
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists():
        assert p.read_bytes()==raw
    else:
        p.write_bytes(raw)
    paths.add(p)


prefix = '0411-fund-payments-'
sources = (
    ('spk-76.pdf', 'decision', 'SPK Bülteni 2026/76, 76/1903 kararı', '2026-10-27', 'SPK', 'official', None,
     'https://spk.gov.tr/data/6ae049c98f95db0c143f6579/2026-76.pdf',
     'b05bdee82148f2751bfa77659507ead881a7a72b05b97faf0c04b9753f190734', (
        ('identity','Birinci sayfa, 76/1903 karar numarası ve günü',0,'1',
         '27/10/2026 tarih ve 76/1903 sayılı Kararı Uyarınca Yapılan Duyuru:'),
        ('scope','Birinci sayfa, 1–2. bent kapsamı ve görevli bankalar',0,'1',
         'AŞ, Tera Portföy Yönetimi AŞ’nin kurucusu olduğu fonların tasfiyesi Türkiye İş Bankası AŞ tarafından yürütülür.'),
        ('priority','Birinci sayfa, 4. bent para piyasası önceliği',0,'1',
         'Ara ödemelere öncelikli olarak ünvanında “para piyasası” ibaresi yer alan yatırım fonlarından başlanır.'),
        ('ceiling','Birinci sayfa, 6. bent endeksleme ve tavan',0,'1',
         'MKK tarafından endeksleme uygulanmaksızın hesaplanan net yatırım tutarını ve 1 milyon TL’yi aşamaz.'),
        ('deduction','İkinci sayfa, 10. bent nihai tasfiyeden mahsup',1,'2',
         'Ara ödemeler, nihai tasfiye kapsamında hak kazanılacak tutardan mahsup edilir.'),
    )),
    ('spk-final.html', 'guide', 'SPK’nin 27 Ekim tasfiye ve ödemeler açıklaması', '2026-10-27', 'SPK', 'official', None,
     'https://spk.gov.tr/duyurular/basin-duyurulari/2026/basin-duyurusu_27102026',
     '0ba49fd737eab426be779863489696e1a7d815ec750cf665742fa574ef95136a', (
        ('decision','Açıklama girişi, 27 Ekim kararı',None,None,
         '27.10.2026 tarih ve 76/1903 sayılı Kararı ile tasfiye ve ödemelere ilişkin usul ve esaslar belirlenmiştir.'),
        ('banks','Soru 2, görevli iki bankanın kapsamı',None,None,
         'Tera Portföy Yönetimi AŞ’nin kurucusu olduğu fonların tasfiyesini ise Türkiye İş Bankası AŞ yürütecek.'),
    )),
    ('payment-aa.html', 'press', 'AA’nın 3 Kasım Fon Koordinasyon Kurulu açıklaması haberi', '2026-11-03',
     'Anadolu Ajansı', 'news', 'Hüseyin Cem Dağıstan',
     'https://www.aa.com.tr/tr/gundem/iletisim-baskanligindan-dokuzuncu-fon-koordinasyon-kurulu-toplantisina-iliskin-aciklama/4109842',
     '3b28cd968f8cfceb60534297f51bb4e98de2fd7d62eceaf5703a08ad73ab60a6', (
        ('authority','Haber girişinde İletişim Başkanlığı açıklamasının kaynağı',None,None,
         'İletişim Başkanlığının sosyal medya hesabından yapılan açıklamada'),
        ('transfer','Açıklama aktarımında 30 Ekim başlangıcı',None,None,
         'ilk ara ödemelerin 30 Ekim 2026 itibarıyla fon sahiplerinin hesaplarına yatırılmaya başlandığı'),
        ('amount','Açıklama aktarımında olağanüstü tasfiye tutarı',None,None, 'toplam 29,3 milyar liranın fon sahiplerinin hesaplarına yatırıldığı'),
    )),
    ('payment-tbmm.pdf', 'reply', 'Hazine ve Maliye Bakanlığının 4 Kasım imzalı yazılı soru cevabı', '2026-11-04',
     'Hazine ve Maliye Bakanlığı', 'official', 'Mehmet Şimşek',
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T7/WebOnergeMetni/345f7fa3-268a-4fba-a1bb-eb35e4582799.pdf',
     '1819d325063ca695edc72ddef55b244b64302c972c1bd85bfac1df8a86a1b756', (
        ('written','İkinci sayfa, 7/50324 ve 7/50325 cevap başlığı',1,None,
         '7/50324 ve 7/50325 Esas Sayılı Soru Önergelerine İlişkin Olarak Hazine ve Maliye Bakanlığı Cevap Metni'),
        ('meeting','Dördüncü sayfa, 3 Kasım kurul toplantısı atfı',3,None,
         '03.11.2026 tarihinde gerçekleştirilen 9. Fon Koordinasyon Kurulu Toplantısı’nda'),
        ('amount','Dördüncü sayfa, olağanüstü tasfiye tutarı',3,None,
         'toplam 29,3 milyar TL’nin fon sahiplerinin hesaplarına yatırıldığı'),
    )),
)

for filename, key, title, date, publisher, kind, author, url, digest, specs in sources:
    src = stage/filename
    raw = src.read_bytes()
    assert sha256(raw).hexdigest() == digest, filename
    pdf = filename.endswith('.pdf')
    mime = 'application/pdf' if pdf else 'text/html'
    doc = prefix+key
    vid = doc+'-v1'
    original = f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, readable_bytes(raw, 'pdf' if pdf else 'html', legacy=False))
    add('document', id=doc, party_id='saadet', title=title, source_kind=kind)
    add('document_version', id=vid, document_id=doc, original_url=url, final_url=url, document_date=date,
        date_precision='day', date_unknown_reason=None, version_label='Erişilen özgün nüsha.',
        mime=mime, accessed_at=datetime.fromtimestamp(src.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=now, sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=vid, publisher=publisher, author=author, kind=kind, social_handle=None,
        published_at=date if key!='reply' else None, date_precision='day' if key!='reply' else 'unknown',
        public_url=url, basis='Yayımlayan kurum, imza ve yayın zamanı kaynak künyesinde ayrı incelendi.')
    if not pdf:
        view = build_view(raw, url, root, fetch_assets=False)
        view['version_id'] = vid
        manifest = root/view['manifest_path']
        paths.add(manifest)
        paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        validate_view(root, view)
        add('archive_view', **view)
        body = html_source_text(raw)
    for suffix, section, page, printed, exact in specs:
        pid = doc+'-'+suffix
        if pdf:
            body = pdf_page_text(root/original, page)
        if key!='reply':
            assert exact in body, (key,suffix,exact)
        else:
            assert not body.strip()
        add('passage', id=pid, version_id=vid, exact=exact, prefix=None, suffix=None, article=None,
            section=section, pdf_page_index=page, printed_page=printed)
        if key=='reply':
            add('manual_passage', passage_id=pid, checked_at=now,
                method='Özgün tarama Poppler ile sayfa bazında görüntülendi.',
                reason='Altı sayfalık TBMM nüshası görsel olarak okundu. İlgili sayfada metin katmanı bulunmadı.')
out = checks/'fund-payments-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='saadet',entries=entries), ensure_ascii=False, indent=2)+'\n')
Path('/tmp/gsd0411-fund-payments-paths').write_text('\n'.join(sorted(map(str,paths)))+'\n')
print(len(entries), len(paths), sha256(out.read_bytes()).hexdigest())
