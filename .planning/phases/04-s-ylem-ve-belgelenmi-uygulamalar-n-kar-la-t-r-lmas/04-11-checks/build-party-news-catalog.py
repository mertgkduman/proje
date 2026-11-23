"""Freeze the public Saadet news listing and its remaining body reads."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys
from urllib.parse import urlencode

checks, stage = map(Path, sys.argv[1:])
root = checks/'party-news-pages'
root.mkdir(exist_ok=True)
cutoff = datetime.fromisoformat('2026-11-10T14:38:46.154751+00:00')
api = 'https://admin.saadet.org.tr/veriler/api.php'
pages, posts = [], {}


def save(path, raw):
    if path.exists():
        assert path.read_bytes() == raw, path
    else:
        path.write_bytes(raw)


def iso(value):
    return datetime.fromtimestamp(int(value), timezone.utc) if value else None


def api_url(resource, **params):
    return api+'?'+urlencode(dict(resource=resource, **params))


for page in range(1, 74):
    file = stage/f'news-page{page}.json'
    raw = file.read_bytes()
    assert b'HTTP/2 200' in (stage/f'news-page{page}.headers').read_bytes()
    response = json.loads(raw)
    assert (response['sonuc'], response['sayfa'], response['toplam'], response['toplam_sayfa'])==(1,page,655,73)
    listing = response['hero']+response['veri']
    path = root/f'page-{page:02}.json'
    save(path, raw)
    pages.append(dict(page=page, sha256=sha256(raw).hexdigest(), size=len(raw),
        file=str(path.relative_to(checks)), post_ids=[str(row['id']) for row in listing],
        accessed_at=datetime.fromtimestamp(file.stat().st_mtime, timezone.utc).isoformat(),
        url=api_url('haberler',mode='page',page=page,hero_size=3,grid_size=9,lang=1,include_slug=1)))
    for row in listing:
        post_id = str(row['id'])
        published = iso(row['tarih'])
        updated = iso(row.get('guncellemetarih'))
        assert post_id not in posts and published
        status = 'pending'
        if published>cutoff:
            status='published_after_cutoff'
        elif updated and updated>cutoff:
            status='historical_version_pending'
        posts[post_id] = dict(id=post_id, page=page, title=row['baslik'], slug=row['kod'],
            publisher='Saadet Partisi', public_url='https://saadet.org.tr/'+row['kod'],
            body_url=api_url('haber_detay',kod=row['kod']), published_at=published.isoformat(),
            listing_updated_at=updated.isoformat() if updated else None, body_status=status)

repeat = (stage/'news-page1-repeat.json').read_bytes()
assert sha256(repeat).hexdigest()==pages[0]['sha256']
assert len(posts)==655
assert sum(row['body_status']=='pending' for row in posts.values())==649
ordered = sorted(posts.values(),key=lambda row: (row['published_at'],int(row['id'])),reverse=True)
out = dict(party_id='saadet', cutoff_at=cutoff.isoformat(), listing_pages=pages, posts=ordered,
    first_page_repeat_sha256=sha256(repeat).hexdigest(),
    boundary='73 erişilen liste yanıtı, 655 benzersiz kayıt. Tarih kesiminden önceki gövdelerin okuması açık. Liste 2001–2020 dönemini kapsamıyor.')
save(checks/'party-news-catalog.json',(json.dumps(out,ensure_ascii=False,indent=2)+'\n').encode())
