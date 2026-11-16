"""Copy a closed report and all of its local document assets to a Pages worktree."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / 'data'
OUT = Path(__file__).resolve().parent


def digest(path):
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


class ReportLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('href', 'src', 'poster') and value:
                self.urls.append(value)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--worktree', required=True)
    parser.add_argument('--release', help='Prepare a candidate bundle before native publication completes')
    args = parser.parse_args()
    dest = Path(args.worktree).resolve()
    assert (dest / '.git').is_file(), 'Expected isolated Git worktree'
    publication = json.loads((OUT / 'publication.json').read_text()) if (OUT / 'publication.json').exists() else None
    release = args.release or publication['release_id']
    assert re.fullmatch('[0-9a-f]{32}', release)
    report = DATA / 'releases' / release / 'index.html'
    if not report.exists() and args.release:
        report = DATA / '.staging' / release / 'index.html'
    links = ReportLinks()
    links.feed(report.read_text())
    sources = {report}
    for url in links.urls:
        parsed = urlsplit(url)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        source = (report.parent / unquote(parsed.path)).resolve()
        assert source.is_relative_to(DATA) and source.is_file(), url
        relative = source.relative_to(DATA)
        assert relative.parts[0] in ('objects', 'views'), url
        sources.add(source)
        if relative.parts[0] == 'views':
            sources.update(path for path in (DATA / 'views' / relative.parts[1]).rglob('*') if path.is_file())
    hashes = {}
    for source in sorted(sources):
        relative = Path('releases') / release / 'index.html' if source == report else source.relative_to(DATA)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        sha = digest(source)
        if target.exists():
            assert digest(target) == sha, 'Published asset changed: ' + str(relative)
        else:
            shutil.copyfile(source, target)
        hashes[str(relative)] = sha
    target = 'releases/' + release + '/index.html'
    redirect = ('<!doctype html>\n<html lang="tr"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                f'<meta http-equiv="refresh" content="0; url={target}">'
                '<title>Türkiye siyasi partileri: kaynaklı rapor</title></head>'
                f'<body><a href="{target}">Kaynaklı raporu aç</a></body></html>\n')
    (dest / 'index.html').write_text(redirect)
    (dest / '.nojekyll').touch()
    evidence = {'release_id': release, 'worktree': str(dest), 'copied_files': len(hashes),
                'publication_confirmed': bool(publication and publication['release_id'] == release),
                'sha256': hashes, 'report_url': 'https://mertgkduman.github.io/proje/' + target,
                'verification_url': 'https://mertgkduman.github.io/proje/' + target + '#phase-03-verification'}
    (OUT / 'pages-bundle.json').write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: value for key, value in evidence.items() if key != 'sha256'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
