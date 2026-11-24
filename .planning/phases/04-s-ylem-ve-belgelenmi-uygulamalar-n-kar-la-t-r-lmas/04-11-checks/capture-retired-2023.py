from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here = Path(__file__).resolve().parent
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()

def add(table, **values):
    entries.append(dict(kind=table, values=values))

def put(relative, raw):
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == raw
    else:
        target.write_bytes(raw)
    paths.add(str(target))

sources = [
    ('speech', 'party-news-bodies/401.json', 'https://admin.saadet.org.tr/veriler/api.php?resource=haber_detay&kod=hirsiza-hirsiz-isgalciye-isgalci-katile-katil-zalime-ise-zalim-diyemediler', '2023-10-11', 'Saadet Partisi', 'party', 'party_publication', 'application/json', '2026-11-24T18:45:34.779574+00:00', [
        ('quote', 'Genel başkanın ödeme değerlendirmesi', 'Emeklilerimize, hatta sadece başka bir işte çalışmayan emeklilerimize, tek seferliğine mahsus verilecek 5 bin lira ikramiyeyi kabul etmediğimizin', None),
        ('role', 'Açıklamanın grup konuşması', 'Genel Başkanımız Temel Karamollaoğlu, TBMM Grup Toplantısı’nda yaptığı konuşmada', None)]),
    ('law7464', 'retired-2023-7464-original.html', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y6/KanunMetni/0ad8a727-9c26-42ec-9eaa-e3d6dc92595d.htm', '2023-10-25', 'TBMM', 'official', 'official', 'text/html', '2026-11-24T18:46:53.292829+00:00', [
        ('amount', 'İlk düzenlemede tek seferlik tutar', '2023 yılı Ekim ödeme döneminde\r\ngelir veya aylık ödemesi yapılanlara dosya bazında 5.000 TL tutarında bir\r\ndefaya mahsus olmak üzere ödeme yapılır.', None),
        ('excluded', 'Çalışma nedeniyle kapsam dışı bırakma', 'almakta iken 2023 yılı Ekim ayı içinde bu Kanun veya 506 sayılı Kanunun geçici\r\n20 nci maddesi kapsamında sigortalı olarak çalışanlar', None),
        ('exception', 'Ölüm aylığı ve geliri istisnası', 'Ancak, ölüm geliri\r\nve aylığı almakta olanlar hakkında bu fıkra hükümleri uygulanmaz.', None)]),
    ('law7491', 'retired-2023-7491-original.html', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y6/KanunMetni/2c5232b7-098b-4fb5-98b8-9931160b7b3e.htm', '2023-12-27', 'TBMM', 'official', 'official', 'text/html', '2026-11-24T18:46:53.303829+00:00', [
        ('repeal', 'Dördüncü fıkranın kaldırılması', '5510 sayılı Kanunun geçici 98 inci maddesinin dördüncü fıkrası yürürlükten\r\nkaldırılmıştır.', None)]),
    ('registry', 'retired-2023-registry-original.html', 'https://www.tbmm.gov.tr/Yasama/Kanun/76587700-6870-41fa-85ae-018c0159e5b9', None, 'TBMM', 'official', 'official', 'text/html', None, [
        ('gazette', 'Resmî Gazete yayımlanma tarihi', '28/12/2023', None),
        ('number', 'Resmî Gazete sayısı', '32413', None)]),
    ('debate', 'retired-2023-debate-original.html', 'https://www.tbmm.gov.tr/Haber/Detay?Id=9c75e8a5-af40-4784-928a-018ca75ecc4c', None, 'TBMM', 'official', 'official', 'text/html', None, [
        ('article', 'Teklif görüşmesindeki madde numarası', '55. maddesi kabul edildi.', None)]),
    ('sgk', 'retired-2023-sgk-activity-original.pdf', 'https://www.sgk.gov.tr/Download/DownloadFile?d=65521b2e-039e-4819-abd1-77503ab4383e&f=f4d5530f-d587-4d5d-ace9-a45698148e6e.pdf', None, 'Sosyal Güvenlik Kurumu', 'official', 'official', 'application/pdf', '2026-11-24T18:47:23.463927+00:00', [
        ('expanded', 'Çalışan emeklilerin kapsama alınması', '2023 yılı Aralık ayında söz konusu Kanun\nmaddesinde yapılan değişiklikle, emekli veya yaşlılık aylığı almakta iken çalışan sigortalıların da 5.000\nTL seyyanen ödemeden yararlanmaları sağlanmıştır.', 70),
        ('paid', 'Düzenleme sonrası ödeme özeti', 'toplamda yaklaşık 4,7 milyon kişiye 23,4 milyar TL tutarında seyyanen ödeme yapılmıştır.', 70)])
]

for key, name, url, day, publisher, kind, attribution, mime, captured, passages in sources:
    path = here / name
    raw = path.read_bytes()
    digest = sha256(raw).hexdigest()
    doc = '0411-retired-2023-' + key
    vid = doc + '-v1'
    ext = 'pdf' if mime == 'application/pdf' else 'html'
    original = f'objects/{digest}/original.' + ('pdf' if ext == 'pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    put(original, raw)
    put(readable, readable_bytes(raw, ext, legacy=False))
    accessed = captured or datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
    add('document', id=doc, party_id='saadet', title={'speech':'Karamollaoğlu’nun 2023 ödeme değerlendirmesi', 'law7464':'7464 sayılı kanun metni', 'law7491':'7491 sayılı kanun metni', 'registry':'7491 sayılı kanunun TBMM sicili', 'debate':'TBMM’de teklif maddesinin kabulü', 'sgk':'SGK 2023 faaliyet raporu'}[key], source_kind=kind)
    add('document_version', id=vid, document_id=doc, original_url=url, final_url=url, document_date=day, date_precision='day' if day else 'unknown', date_unknown_reason=None if day else 'Belgenin ilk yayımlandığı gün kaynakta kesinleştirilmedi.', version_label='Erişilen özgün kaynak.', accessed_at=accessed, verified_at=now, mime=mime, sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=vid, publisher=publisher, author=None, kind=attribution, published_at=day if key == 'speech' else None, date_precision='day' if key == 'speech' else 'unknown', social_handle=None, public_url=url, basis='Parti yayımı grup konuşmasını aktarır.' if key == 'speech' else 'Kurumun özgün kaydı incelendi.')
    if ext == 'html':
        view = build_view(raw, url, root, fetch_assets=False)
        view['version_id'] = vid
        validate_view(root, view)
        add('archive_view', **view)
        manifest = root / view['manifest_path']
        paths.add(str(manifest))
        paths.update(str(manifest.parent / n) for n in json.loads(manifest.read_bytes())['files'])
        body = html_source_text(raw)
    for suffix, section, exact, page in passages:
        assert exact in (pdf_page_text(root / original, page) if page is not None else body), (key, suffix)
        add('passage', id=doc + '-' + suffix, version_id=vid, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=page, printed_page=56 if page is not None else None)

(here / 'retired-2023-source-records.json').write_text(json.dumps(dict(party_id='saadet', entries=entries), ensure_ascii=False, indent=2) + '\n')
Path('/tmp/gsd0411-retired-2023-paths').write_text('\n'.join(sorted(paths)) + '\n')
print('entries', len(entries), 'paths', len(paths))
