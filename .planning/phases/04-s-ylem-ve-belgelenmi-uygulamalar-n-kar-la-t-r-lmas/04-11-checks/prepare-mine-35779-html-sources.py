"""Build the same 7/35779 case with TBMM's compact official HTML sources."""

from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path

from arsiv import html_source_text, readable_bytes
from arsiv_gorunum import build_view, validate_view

archive = Path('/work/mg551/gsd0411-2020-miners')
compact = archive / 'compact'
compact.mkdir(exist_ok=True)
source_root = Path('data/practices/sources/saadet').resolve()
base = archive / 'candidate-draft.json'
review = archive / 'candidate-review-draft.json'
base_data = base.read_bytes()
review_data = review.read_bytes()
assert sha256(base_data).hexdigest() == '2bca7d9a895c282df74d9a09c36e817be5ce6394cba738cd3b7e528c65ab2783'
assert sha256(review_data).hexdigest() == 'a305484f46ec4bd7cae6eae1201e3bc509ba71c06c90e1d30192d81116a85e36'
package = json.loads(base_data)
prior_release = json.loads(Path('data/current.json').read_bytes())
assert prior_release['release_id'] == package['base_release']
entries = package['entries']
now = datetime.now(timezone.utc).isoformat()


def store(path, raw):
    target = source_root / path
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes() == raw, target
    else:
        target.write_bytes(raw)


def update_version(source, url, file, digest, sections, *, http_charset=None):
    prefix = '0411-mine-inquiry-'
    version_id = f'{prefix}{source}-v1'
    fetched = archive / file
    raw = fetched.read_bytes()
    assert sha256(raw).hexdigest() == digest
    accessed_at = datetime.fromtimestamp(fetched.stat().st_mtime, timezone.utc).isoformat()
    content = html_source_text(raw)
    version = next(item['values'] for item in entries if item['kind'] == 'document_version'
                   and item['values']['id'] == version_id)
    previous = version['final_url']
    original = f'objects/{digest}/original.html.bin'
    readable = f'objects/{digest}/readable.html'
    store(original, raw)
    if http_charset:
        assert http_charset == 'utf-8'
        raw.decode('utf-8', errors='strict')
        header = (archive / 'filing-direct-headers.txt').read_bytes().lower().splitlines()
        assert b'content-type: text/html; charset=utf-8' in header
        assert (archive / 'filing-direct-header-proof.html').read_bytes() == raw
    store(readable, readable_bytes(raw, 'html', legacy=bool(http_charset)))
    view = build_view(raw, url, source_root, fetch_assets=False, http_charset=http_charset)
    validate_view(source_root, view)
    entries.append({'kind':'archive_view','values':dict(view,version_id=version_id)})
    version.update(original_url=url, final_url=url, accessed_at=accessed_at,
                   verified_at=now, mime='text/html', sha256=digest,
                   original_path=original, readable_path=readable)
    attribution = next(item['values'] for item in entries if item['kind'] == 'source_attribution'
                       and item['values']['version_id'] == version_id)
    attribution.update(public_url=url, basis='TBMM’nin tarihli çevrimiçi tutanak kaydı, basılı nüshayla karşılaştırıldı.')
    for name, exact in sections.items():
        assert exact in content, name
        passage = next(item['values'] for item in entries if item['kind'] == 'passage'
                       and item['values']['id'] == f'{prefix}{source}-{name}')
        passage.update(exact=exact,pdf_page_index=None,printed_page=None)
    for row in package['practice_records']['practice_attempt_v2']:
        if row['source_version_id'] == version_id:
            assert row['url'] == previous and row['query'] == previous
            row.update(url=url,query=url)
    for row in package['practice_records']['practice_lead']:
        if row['url'] == previous and version_id in row['id']:
            row['url'] = url
    return {'id':version_id,'url':url,'previous_pdf_url':previous,'sha256':digest,
            'original_path':original,'readable_path':readable,'view':view,
            'http_charset':http_charset,'retrieved_at':accessed_at}


versions = [
    update_version(
        'identity', 'https://tbmm.gov.tr/milletvekili/UyeGenelKurulKonusmalariDetay?eid=91216',
        'identity-compact-curl.html','696a7b1426f153a64b024ae30a4ea2652223b4933ead22dcf389b035375cac10',
        {'member':'ABDULKADİR KARADUMAN (Konya) -',
         'party':"Saadet Partisi olarak gençlerin başka ülke vatandaşı olma hayali kurmayacakları bir Türkiye'yi kurmak"},
    ),
    update_version(
        'filing', 'https://tbmm.gov.tr/Gundem/GelenKagitDetay/3c4bf528-7953-40a7-1f04-08db286b2e79',
        'filing-direct-curl.html','809cf5a370b3478f7eed5cd6b71c56ad83af8aeb4e7661048fc2593c156de94d',
        {'filing':"Konya Milletvekili Abdulkadir Karaduman'ın, Soma ve Ermenek'te bazı maden işçilerinin kıdem tazminatını alamadıklarına dair iddialara ilişkin Enerji ve Tabii Kaynaklar Bakanı'ndan yazılı soru önergesi (7/35779) (Başkanlığa geliş tarihi: 20.10.2020)"},
        http_charset='utf-8',
    ),
]
answer = next(item['values'] for item in entries if item['kind'] == 'document_version'
              and item['values']['id'] == '0411-mine-inquiry-answer-v1')
original = source_root / answer['original_path']
if not original.exists():
    source = Path(__file__).parent / 'karaduman-2020-miners' / 'tbmm-karaduman-written-question.pdf'
    assert sha256(source.read_bytes()).hexdigest() == answer['sha256']
    original.parent.mkdir(parents=True, exist_ok=True)
    os.link(source, original)
assert sha256(original.read_bytes()).hexdigest() == answer['sha256']
store(answer['readable_path'], readable_bytes(original.read_bytes(), 'pdf', legacy=False))
compact_package = compact / 'candidate-draft.json'
compact_package.write_text(json.dumps(package,ensure_ascii=False,indent=2)+'\n')
(compact / 'candidate-review-draft.json').write_bytes(review_data)
proof = {'package_sha256':sha256(compact_package.read_bytes()).hexdigest(),
         'review_sha256':sha256(review_data).hexdigest(),'substitutions':versions}
(compact / 'source-proof.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
print(proof['package_sha256'],proof['review_sha256'])
