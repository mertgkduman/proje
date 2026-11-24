from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

here = Path(__file__).resolve().parent
root = Path('data/practices/sources/saadet')
now = datetime.now(timezone.utc).isoformat()
entries, paths = [], set()
def add(table, **values): entries.append({'kind': table, 'values': values})
def put(rel, raw):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists(): assert p.read_bytes() == raw
    else: p.write_bytes(raw)
    paths.add(str(p))
sources = [
 ('statement','leaders-2023-03-03-abc-original.html','https://abcgazetesi.com.tr/karamollaoglundan-aciklama-bizler-milletimize-verdigimiz-sozun-arkasindayiz-467541','2023-03-03','ABC Gazetesi','journalism','journalism','text/html','2026-11-24T20:29:17.002611+00:00','3 Mart tarihinde yayımlanmış ve güncellenmiş haber.'),
 ('meeting','leaders-2023-03-06-independent-original.html','https://www.indyturk.com/node/615011/siyaset/millet-i%CC%87ttifak%C4%B1n%C4%B1n-cumhurba%C5%9Fkan%C4%B1-aday%C4%B1-kemal-k%C4%B1l%C4%B1%C3%A7daro%C4%9Flu','2023-03-06','Independent Türkçe','journalism','journalism','text/html','2026-11-24T20:29:18.695617+00:00','6 Mart haberi. Son güncelleme aynı gün saat 21.24.'),
 ('party','party-news-bodies/386.json','https://admin.saadet.org.tr/veriler/api.php?resource=haber_detay&kod=millet-ittifakinin-cumhurbaskani-adayi-kemal-kilicdarogludur','2023-03-12','Saadet Partisi','party','party_publication','application/json','2026-11-24T20:26:55.025130+00:00','API damgasının yerel günü 12 Mart. Toplantı tarihi bağımsız kaynakla doğrulanır.'),
]
anchors = {
 'statement':[('plan','Saadet liderinin toplantı planı','6 Mart Pazartesi günü Saadet Partimizin ev sahipliğinde bir araya geleceğiz.')],
 'meeting':[('event','Toplantı ve ortak aday',"Millet İttifakı'nın\u00a0Saadet Partisi Genel Merkezi'ndeki 13'üncü toplantısı Kemal Kılıçdaroğlu'nun adaylığıyla sonuçlandı."),('announcement','Adayı açıklayan kişi',"Kısa bir konuşma yapan Karamollaoğlu, CHP Genel Başkanı Kemal Kılıçdaroğlu'nun\u00a0Millet İttifakı'nı oluşturan 6 partinin cumhurbaşkanı adayı olduğunu açıkladı.")],
 'party':[('host','Saadet ev sahipliği','Saadet Partisi ev sahipliğinde gerçekleştirilen Millet İttifakı Liderler Toplantısı sona erdi.'),('candidate','Karamollaoğlunun ortak aday duyurusu','Sayın Kemal Kılıçdaroğlu bizim cumhurbaşkanı adayımızdır.')],
}
for key, name, url, day, publisher, kind, attribution, mime, accessed, label in sources:
    raw = (here / name).read_bytes()
    h = sha256(raw).hexdigest()
    doc = '0411-leaders-2023-03-' + key
    vid = doc + '-v1'
    original, readable = f'objects/{h}/original.html.bin', f'objects/{h}/readable.html'
    put(original, raw)
    put(readable, readable_bytes(raw, 'html', legacy=False))
    add('document', id=doc, party_id='saadet', title='6 Mart 2023 liderler toplantısı ' + key, source_kind=kind)
    add('document_version', id=vid, document_id=doc, original_url=url, final_url=url, document_date=day, date_precision='day', date_unknown_reason=None, version_label=label, accessed_at=accessed, verified_at=now, mime=mime, sha256=h, original_path=original, readable_path=readable)
    add('source_attribution', version_id=vid, publisher=publisher, author=None, kind=attribution, published_at=day, date_precision='day', social_handle=None, public_url=url, basis=label)
    view = build_view(raw, url, root, fetch_assets=False)
    view['version_id'] = vid
    validate_view(root, view)
    add('archive_view', **view)
    manifest = root / view['manifest_path']
    paths.add(str(manifest))
    paths.update(str(manifest.parent / n) for n in json.loads(manifest.read_bytes())['files'])
    body = html_source_text(raw)
    for suffix, section, exact in anchors[key]:
        assert exact in body, (key, suffix)
        add('passage', id=doc+'-'+suffix, version_id=vid, exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=None, printed_page=None)
(here/'leaders-2023-03-source-records.json').write_text(json.dumps({'party_id':'saadet','entries':entries}, ensure_ascii=False, indent=2)+'\n')
Path('/tmp/gsd0411-leaders-2023-paths').write_text('\n'.join(sorted(paths))+'\n')
print('entries', len(entries), 'paths', len(paths))
