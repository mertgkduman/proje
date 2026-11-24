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
def add(table, **values): entries.append({'kind': table, 'values': values})
def put(rel, raw):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): assert path.read_bytes() == raw
    else: path.write_bytes(raw)
    paths.add(str(path))

sources = [
 ('speech', '/tmp/saadet-506-indy.html', 'https://www.indyturk.com/node/755133/d%C3%BCnya/mahmut-ar%C4%B1kan-faturay%C4%B1-halka-kesip-%C3%BClke-kaynaklar%C4%B1n%C4%B1-bir-avu%C3%A7-yanda%C5%9Fa-aktarmaktan', 'html', '2025-03-12', 'news', 'Independent Türkçe', [
  ('demand', '12 Mart Arıkan KHK iade talebi', 'KHK’larla oluşturulan mağduriyetler giderilmelidir. Beraat edenler, takipsizlik alanlar görevlerine iade edilmelidir.', None)]),
 ('motion', '/tmp/saadet-102925.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T10/WebOnergeMetni/6b85c0e4-aef0-439f-81d8-b3335aa2aba9.pdf', 'pdf', '2025-07-09', 'official', 'TBMM', [
  ('subject', 'İmzalı asıl önergenin 2. sayfası', 'OHAL KHK’ları ile kamu görevinden ihraç edilen kişilerden hakkında adli bir soruşturması bulunmayan, ceza soruşturması sonucunda hakkında takipsizlik kararı verilen ya da mahkemelerde beraat eden kişilerin hala görevine iade edilmemesi', 1),
  ('signatures', 'İmzalı asıl önergenin 9. sayfası, 22 isimli imza çizelgesi', 'MESUT DOĞAN', 8),
  ('kaya', 'İmzalı asıl önergenin 9. sayfası, Bülent Kaya imza satırı', 'BÜLENT KAYA', 8)]),
 ('registry', '/tmp/saadet-102925.html', 'https://tbmm.gov.tr/Denetim/Meclis-Arastirma-Onergesi-Detay/1425e389-5fca-4a91-9149-0197f4ba0ea0', 'html', None, 'official', 'TBMM', [
  ('number', '10/2925 sicil numarası', '10 / 2925', None),
  ('status', 'Erişim anındaki önerge durumu', 'G&#xFC;ndemde', None)]),
 ('role', '/tmp/saadet-mesut-20250321.pdf', 'https://cdn.tbmm.gov.tr/KKBSPublicFile/D28/Y3/T7/WebOnergeMetni/dfba1ade-089f-48d0-ac07-3531744295a3.pdf', 'pdf', '2025-03-21', 'official', 'TBMM', [
  ('mesut', 'Mesut Doğan tarihli Saadet milletvekili başlığı', 'Mesut DOĞAN\nSaadet Partisi Ankara Milletvekili', 0)]),
]
for key, filename, url, ext, day, kind, publisher, anchors in sources:
    source = Path(filename); raw = source.read_bytes(); digest = sha256(raw).hexdigest()
    doc = '0411-khk-102925-' + key; vid = doc + '-v1'
    original = f'objects/{digest}/original.' + ('pdf' if ext == 'pdf' else 'html.bin')
    readable = f'objects/{digest}/readable.html'
    put(original, raw); put(readable, readable_bytes(raw, ext, legacy=False))
    add('document', id=doc, party_id='saadet', title='KHK ve 10/2925: ' + key, source_kind=kind)
    add('document_version', id=vid, document_id=doc, original_url=url, final_url=url, document_date=day,
        date_precision='day' if day else 'unknown', date_unknown_reason=None if day else 'TBMM sicil sayfasının ilk yayın günü belirlenmedi.',
        version_label='Erişilen özgün nüsha.', accessed_at=datetime.fromtimestamp(source.stat().st_mtime, timezone.utc).isoformat(),
        verified_at=now, mime='application/pdf' if ext == 'pdf' else 'text/html', sha256=digest, original_path=original, readable_path=readable)
    add('source_attribution', version_id=vid, publisher=publisher, author=None, kind='journalism' if kind == 'news' else 'official',
        published_at=day, date_precision='day' if day else 'unknown', social_handle=None, public_url=url,
        basis='Kaynak ve işlem tarihi ayrıldı; parti ve grup sıfatları metin ve tarihli belgeyle incelendi.')
    if ext == 'html':
        view = build_view(raw, url, root, fetch_assets=False); view['version_id'] = vid; validate_view(root, view); add('archive_view', **view)
        manifest = root / view['manifest_path']; paths.add(str(manifest)); paths.update(str(manifest.parent / n) for n in json.loads(manifest.read_bytes())['files'])
        body = html_source_text(raw)
    for suffix, section, exact, page in anchors:
        pid = doc + '-' + suffix
        text = body if page is None else pdf_page_text(root / original, page)
        manual = page is not None and not text.strip()
        if not manual: assert exact in text, (key, suffix, repr(exact))
        add('passage', id=pid, version_id=vid, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=page, printed_page=None)
        if manual: add('manual_passage', passage_id=pid, checked_at=now, method='Özgün PDF sayfası Poppler ile görsel olarak okundu.', reason='Bu sayfanın metin katmanı boş; ad, imza satırı ve bağlam görsel olarak okundu.')
(here / 'khk-102925-source-records.json').write_text(json.dumps({'party_id':'saadet', 'entries':entries}, ensure_ascii=False, indent=2) + '\n')
Path('/tmp/gsd0411-khk102925-paths').write_text('\n'.join(sorted(paths))+'\n')
print('entries',len(entries),'paths',len(paths))
