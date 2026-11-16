"""Verify the deployed report and the exact documents used by its review examples."""
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PUBLIC = 'https://mertgkduman.github.io/proje/'


def fetch(path, expected=None):
    request = Request(PUBLIC + path, headers={'User-Agent': 'proje-publication-check/1.0'})
    digest = hashlib.sha256()
    count = 0
    with urlopen(request, timeout=120) as response:
        assert response.status == 200
        while chunk := response.read(1024 * 1024):
            digest.update(chunk)
            count += len(chunk)
    actual = digest.hexdigest()
    if expected:
        assert actual == expected, 'Served bytes differ: ' + path
    return {'path': path, 'status': 200, 'bytes': count, 'sha256': actual}


def main():
    bundle = json.loads((OUT / 'pages-bundle.json').read_text())
    release = bundle['release_id']
    folder = ROOT / 'data/releases' / release
    records = json.loads((folder / 'records.json').read_text())
    acceptance = next(r for r in records['review'] if r['id'] == 'phase-03-user-acceptance-20261116')
    review = json.loads(acceptance['reason'])
    fields = {f['id']: f for f in records['comparison_field']}
    passages = {p['id']: p for p in records['passage']}
    versions = {v['id']: v for v in records['document_version']}
    views = {v['version_id']: v['index_path'] for v in records['archive_view']}
    paths = {'releases/' + release + '/index.html'}
    for test in review['tests']:
        for example in test['examples']:
            field = fields.get(example.get('field_id'))
            if not field:
                continue
            fids = {field['summary_finding_id'], field['quote_finding_id']}
            for evidence in records['finding_evidence']:
                if evidence['finding_id'] not in fids:
                    continue
                version = versions[passages[evidence['passage_id']]['version_id']]
                paths.add(version['original_path'])
                if version['id'] in views:
                    paths.add(views[version['id']])
                else:
                    paths.add(version['readable_path'])
    for suffix in ('.css', '.woff2', '.png'):
        asset = next((path for path in bundle['sha256'] if path.endswith(suffix)), None)
        if asset:
            paths.add(asset)
    with urlopen(PUBLIC + '?release=' + release, timeout=30) as response:
        root = response.read().decode('utf-8')
    assert release in root, 'Public root still points to an older report'
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda path: fetch(path, bundle['sha256'][path]), sorted(paths)))
    result = {'release_id': release, 'root_points_to_release': True,
              'report_url': bundle['report_url'], 'verification_url': bundle['verification_url'],
              'checked_files': len(results), 'files': results}
    (OUT / 'live-checks.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'files'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
