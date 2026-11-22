"""Run archive commands against one isolated Yeni Parti draft."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / 'data'
PACKAGE = HERE / 'policy-tracer-draft.json'
REVIEW = HERE / 'policy-review-draft.json'
INVENTORY = DATA / 'practices/04-inventory.json'
SOURCE = DATA / 'practices/sources/tip'
EXPECTED_RELEASE = 'f67ca0a35e634035bf3aa83a46571f50'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def receipt(path, text):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())


def canonical_identity():
    pointer = DATA / 'current.json'
    release = json.loads(pointer.read_text())['release_id']
    require(release == EXPECTED_RELEASE and not (DATA / '.write.lock').exists(), 'canonical base or lock changed')
    folder = DATA / 'releases' / release
    manifest = folder / 'manifest.json'
    expected = json.loads(manifest.read_text())['files']
    require({n: sha(folder / n) for n in expected} == expected, 'canonical release bytes disagree')
    return {'release': release, 'pointer': sha(pointer), 'manifest': sha(manifest), 'files': expected}


def ignore(directory, names):
    ignored = {'__pycache__'}
    if Path(directory) == DATA:
        ignored.update({'.staging', '.write.lock'})
    return ignored.intersection(names)


def check(receipt_name, name, args, cwd, marker):
    path = HERE / f'{receipt_name}-{name}.log'
    with path.open('x', encoding='utf-8') as log:
        code = subprocess.call([sys.executable, 'src/arsiv.py', *args], cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        log.flush()
        os.fsync(log.fileno())
    receipt(HERE / f'{receipt_name}-{name}.exit', f'{code}\n')
    require(code == 0, f'{name}: exit {code}')
    require(any(line.startswith(marker) for line in path.read_text().splitlines()), f'{name}: missing {marker}')


def main(package_path, review_path, scope='tip-policy', event_id='0405-tip-282121-event',
         relation_id='0405-tip-282121-relation', absent_dispute=''):
    job = os.environ['SLURM_JOB_ID']
    receipt_name = f'{scope}-{job}'
    baseline = canonical_identity()
    ps, rs, inv = (sha(path) for path in (package_path, review_path, INVENTORY))
    package = json.loads(package_path.read_text())
    require(package['base_release'] == baseline['release'] and package['party_id'] == 'tip', 'wrong package base/owner')
    with tempfile.TemporaryDirectory(prefix=f'gsd-0404-{scope}-') as tmp:
        stage = Path(tmp)
        shutil.copytree(ROOT / 'src', stage / 'src', ignore=ignore)
        shutil.copytree(DATA, stage / 'data', ignore=ignore)
        code = subprocess.check_output(['git', 'ls-files', 'src'], text=True, cwd=ROOT).splitlines()
        require(all(sha(ROOT / p) == sha(stage / p) for p in code), 'staged code differs')
        require(sha(stage / 'data/current.json') == baseline['pointer'], 'staged pointer differs')
        paths = set()
        for entry in package['entries']:
            row = entry['values']
            if entry['kind'] == 'document_version':
                paths.update(row[k] for k in ('original_path', 'readable_path') if row.get(k))
            elif entry['kind'] == 'archive_view':
                m = Path(row['manifest_path'])
                paths.add(str(m))
                path = SOURCE / m
                if not path.is_file():
                    path = DATA / m
                paths.update(str(m.parent / key) for key in json.loads(path.read_text())['files'])
        for name in sorted(paths):
            p = Path(name)
            require(not p.is_absolute() and '..' not in p.parts, f'invalid asset path {name}')
            dest = stage / 'data' / p
            source = SOURCE / p
            if not source.is_file():
                source = DATA / p
            require(source.is_file(), f'missing asset {name}')
            if dest.exists():
                require(sha(dest) == sha(source), f'different source bytes at {name}')
            else:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, dest)
        print(f'Staged {len(paths)} original, readable and view paths; package {ps}; review {rs}', flush=True)
        staged_inventory = stage / 'data/practices/04-inventory.json'
        require(sha(staged_inventory) == inv, 'staged inventory differs')
        check(receipt_name, 'input', ['practice-check','--input',str(package_path),'--inventory',str(staged_inventory)],
              stage, 'PRACTICE_INPUT_OK')
        check(receipt_name, 'source', ['practice-source-check','--input',str(package_path),'--review',str(review_path)],
              ROOT, 'PRACTICE_SOURCE_REVIEW_OK')
        out = stage / 'view'
        check(receipt_name, 'preview', ['practice-preview','--input',str(package_path),'--inventory',str(INVENTORY),
                               '--out',str(out),'--source-root',str(SOURCE)], ROOT, 'PRACTICE_PREVIEW_OK')
        releases = list((out / 'releases').iterdir())
        require(len(releases) == 1, 'expected one preview release')
        rel = releases[0]
        manifest = json.loads((rel / 'manifest.json').read_text())
        require({name: sha(rel / name) for name in manifest['files']} == manifest['files'], 'preview files differ')
        snapshot = json.loads((rel / 'records.json').read_text())
        require(any(r['id']==event_id for r in snapshot['practice_event']), f'event missing: {event_id}')
        require(any(r['id']==relation_id for r in snapshot['practice_relation']), f'relation missing: {relation_id}')
        if absent_dispute:
            require(all(r['id'] != absent_dispute for r in snapshot['practice_dispute']), f'unsupported dispute persisted: {absent_dispute}')
        report = (rel / 'index.html').read_text()
        for prefix in ('party', 'comparison'):
            require(f'id="{prefix}-practice-{relation_id}"' in report, f'{prefix} relation missing')
        require(canonical_identity()==baseline, 'canonical archive changed')
        require((sha(package_path),sha(review_path),sha(INVENTORY))==(ps,rs,inv), 'draft or inventory changed')
        artifact = DATA / '.staging' / f'gsd-0405-{receipt_name}'
        shutil.copytree(out, artifact)
        result = {'job':job,'scope':scope,'event':event_id,'relation':relation_id,'absent_dispute':absent_dispute,'package_sha256':ps,'review_sha256':rs,
                  'inventory_sha256':inv,'canonical':baseline,'preview':str(artifact/'releases'/rel.name),
                  'preview_manifest_sha256':sha(rel/'manifest.json'),'staged_source_paths':len(paths)}
        receipt(HERE / f'{receipt_name}.json', json.dumps(result,ensure_ascii=False,indent=2)+'\n')


if __name__ == '__main__':
    arguments = sys.argv[1:]
    if arguments:
        main(Path(arguments[0]).resolve(), Path(arguments[1]).resolve(), *arguments[2:])
    else:
        main(PACKAGE, REVIEW)
