"""Archive the signed 10/4826 motion and its separate agenda vote."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

checks,stage=map(Path,sys.argv[1:])
root=Path('data/practices/sources/yeni-yol')
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


day = '2026-10-21'
prefix = '0408-fund-4826-'
sources = (
    ('atmaca.html', 'detail', 'TBMM 10/4826 esas kaydı', None,
     'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/aaa8954d-bfa7-40d9-a4c9-01a15e7ab21a',
     '53e87631cd7c96e6d7f3918be7153ab1c22af074801c8e9b2305d855b1846c6e', (
        ('id', '10/4826 esas numarası', None, '<td>10 / 4826</td>'),
        ('filed', 'TBMM Başkanlığına geliş 21 Ekim 2026', None, '<td>21/10/2026</td>'),
        ('status', 'Erişilen esas dosyası durumu', None, '<td>G&#xFC;ndemde</td>'),
        ('owner', 'Araştırma önergesi sahibi ve diğer imzacılar', None, 'Bursa Milletvekili Mehmet Atmaca ve 19 Milletvekili'),
        ('party', 'TBMM imza tablosunda ilk imzanın grup kaydı', None,
         'Mehmet ATMACA</a></td>\n                                        <td>Yeni Yol Partisi</td>'),
    )),
    ('4826.pdf', 'signed', '10/4826 imzalı Meclis araştırması önergesi', day,
     'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y5/T10/WebOnergeMetni/00b7284f-394f-4166-bfdb-e6c7dd60fceb.pdf',
     '2d3dcbf7e9cd7dcca8ec1401bcb4c2c16443260a46e2c3c8b74d022935c53ada', (
        ('id', 'İmzalı kapak, 10/4826 esas numarası', 0, '10/4826'),
        ('purpose', 'Gerekçe, kamu kurumları arasında koordinasyon incelemesi', 1,
         'kurumlar arasındaki koordinasyonun yeterli olup olmadığının incelenmesini'),
        ('signature', 'İmza cetveli, Mehmet Atmaca satırı', 2, 'MEHMET ATMACA'),
    )),
    ('day9-ham.html', 'floor', '21 Ekim 2026 TBMM 9. Birleşim ham tutanağı', day,
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/9/Ham/c1743ea7-6d52-4961-8176-63c54738bc4e.html',
     '9aa80adf41ffb4c2a32d492009e507dca02631eb737c7755936e869bcbd2fdfa', (
        ('agenda', 'Yeni Yol’un aynı gün ön görüşme önerisi', None,
         'görüşmelerinin 21/10/2026 Çarşamba günkü birleşimde yapılması önerilmiştir.'),
        ('role', 'Mehmet Atmaca’nın Yeni Yol grup sıfatı', None, 'YENİ YOL GRUBU ADINA MEHMET ATMACA (Bursa)'),
        ('aim', 'Atmaca’nın Meclis komisyonu talebi', None, 'bu işin Millet Meclisinde kurulacak bir komisyona devri'),
        ('first', 'Birinci elektronik oylamada yeter sayı bulunmadığının ikinci oturum başında teyidi', None,
         'YENİ YOL Partisi grup önerisinin oylamasında karar yeter sayısı bulunamamıştı.'),
        ('second', 'İkinci elektronik oylamada yeter sayı bulunmadığının üçüncü oturum başında teyidi', None,
         "YENİ YOL Partisi grup önerisinin 2'nci oylamasında da karar yeter sayısı bulunamamıştı."),
    )),
    ('day9-ozet.html', 'summary', '21 Ekim 2026 TBMM 9. Birleşim işlem özeti', day,
     'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/9/Ozet/b0168fb9-37c5-40e5-a853-e52533af38b9.html',
     '9c3645192c5bfabba71416db7db7a1e5e13209c2ed18840adf56e3244443badd', (
        ('motion', 'İşlem özetinde Yeni Yol ve Atmaca önergesi', None,
         '21/10/2026 tarihinde Bursa Milletvekili Mehmet Atmaca ve 19 milletvekili'),
        ('result', 'Özette aynı gün görüşme önerilerinin sonucu', None, 'önerileri yapılan görüşmelerden sonra kabul edilmedi.'),
    )),
)
shared = Path('data/practices/sources/yeni-parti')
prior = json.loads(Path('data/practices/04-yeni-parti.json').read_bytes())['entries']

for filename, key, title, date, url, digest, specs in sources:
    src = stage/filename
    raw = src.read_bytes()
    assert sha256(raw).hexdigest() == digest, filename
    pdf = filename.endswith('.pdf')
    doc = prefix+key
    vid = doc+'-v1'
    original = f'objects/{digest}/'+('original.pdf' if pdf else 'original.html.bin')
    readable = f'objects/{digest}/readable.html'
    save(original, raw)
    save(readable, (shared/readable).read_bytes() if key == 'summary' else readable_bytes(raw, 'pdf' if pdf else 'html', legacy=False))
    add('document', id=doc, party_id='yeni-yol', title=title, source_kind='official')
    add('document_version', id=vid, document_id=doc, original_url=url, final_url=url, document_date=date,
        date_precision='day' if date else 'unknown',
        date_unknown_reason=None if date else 'TBMM dosyasının ilk yayımlandığı gün açık değil. Geliş tarihi ayrı pasajda.',
        version_label='Erişilen özgün TBMM kaydı.', mime='application/pdf' if pdf else 'text/html',
        accessed_at=datetime.fromtimestamp(src.stat().st_mtime, timezone.utc).isoformat(), verified_at=now,
        sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=vid, publisher='TBMM', author=None, kind='official',
        published_at=None, date_precision='unknown', social_handle=None, public_url=url,
        basis='TBMM birleşim ve evrak kimlikleri asıl belgede okundu.')
    if pdf:
        assert tuple(pdf_page_text(root/original, i).strip() for i in range(3)) == ('10/4826', '', '')
    else:
        if key == 'summary':
            view = next(e['values'].copy() for e in prior if e['kind']=='archive_view'
                        and e['values']['version_id']=='0404-ilk-yayin-takip-fon-1021-ozet-v1')
            manifest = Path(view['manifest_path'])
            save(manifest, (shared/manifest).read_bytes())
            for name in json.loads((shared/manifest).read_bytes())['files']:
                rel = manifest.parent/name
                save(rel, (shared/rel).read_bytes())
        else:
            view = build_view(raw, url, root, fetch_assets=False)
            manifest = root/view['manifest_path']
            paths.add(manifest)
            paths.update(manifest.parent/name for name in json.loads(manifest.read_bytes())['files'])
        view['version_id'] = vid
        validate_view(root, view)
        add('archive_view', **view)
        body = html_source_text(raw)
    if key == 'floor':
        anchor = body.index("YENİ YOL Partisi grup önerisinin 2'nci oylamasında")
        begin = body.index('Öneri kabul edilmemiştir.', anchor)
        final = body.index('Karar yeter sayısı vardır.', begin)+len('Karar yeter sayısı vardır.')
        specs += (('decision', 'Üçüncü oturum, karar yeter sayısı ve önerinin reddi', None, body[begin:final]),)
    for suffix, section, page, exact in specs:
        if not pdf:
            assert exact in body, (key, suffix)
        pid = doc+'-'+suffix
        add('passage', id=pid, version_id=vid, exact=exact, prefix=None, suffix=None, article=None,
            section=section, pdf_page_index=page, printed_page=None)
        if page in (1, 2):
            add('manual_passage', passage_id=pid, checked_at=now,
                method='Özgün PDF sayfası Poppler görüntüsünden okundu.',
                reason='İlgili sayfada metin katmanı yok. Gerekçe ve imza tablosu görsel olarak okundu.')
out = checks/'fund-4826-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='yeni-yol', entries=entries), ensure_ascii=False, indent=2)+'\n')
Path('/tmp/gsd0408-fund-4826-source-paths').write_text('\n'.join(sorted(map(str, paths)))+'\n')
print(len(entries), len(paths), sha256(out.read_bytes()).hexdigest())
