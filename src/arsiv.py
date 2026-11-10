"""Yerel, kaynaklı araştırma arşivi ve atomik sürüm yayıncısı."""
import argparse
import datetime as dt
import hashlib
import html
import json
import os
from pathlib import Path
import shutil
import sqlite3
import subprocess
import tempfile
import urllib.parse
import urllib.request
import uuid

from rapor import render_report

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
MAX_SOURCE = 20 * 1024 * 1024
TABLES = {
    'party': 'id TEXT PRIMARY KEY, legal_name TEXT NOT NULL, registry_key TEXT NOT NULL',
    'document': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), title TEXT NOT NULL, source_kind TEXT NOT NULL',
    'document_version': 'id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES document(id), original_url TEXT NOT NULL, final_url TEXT NOT NULL, document_date TEXT, version_label TEXT, accessed_at TEXT NOT NULL, verified_at TEXT NOT NULL, mime TEXT NOT NULL, sha256 TEXT NOT NULL, original_path TEXT NOT NULL, readable_path TEXT NOT NULL',
    'passage': 'id TEXT PRIMARY KEY, version_id TEXT NOT NULL REFERENCES document_version(id), exact TEXT NOT NULL, prefix TEXT, suffix TEXT, article TEXT, section TEXT, pdf_page_index INTEGER, printed_page TEXT',
    'finding': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), heading TEXT NOT NULL, pair_id TEXT NOT NULL, text TEXT NOT NULL, provenance TEXT NOT NULL, epistemic_type TEXT NOT NULL',
    'finding_evidence': 'finding_id TEXT NOT NULL REFERENCES finding(id), passage_id TEXT NOT NULL REFERENCES passage(id), role TEXT NOT NULL, PRIMARY KEY(finding_id, passage_id, role)',
    'comparison': 'id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, state TEXT NOT NULL',
    'comparison_evidence': 'comparison_id TEXT NOT NULL REFERENCES comparison(id), passage_id TEXT NOT NULL REFERENCES passage(id), PRIMARY KEY(comparison_id, passage_id)'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe_url(url):
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Yalnız http/https kaynak adresleri kabul edilir')
    return url


def safe_path(base, relative):
    base = Path(base).resolve()
    target = (base / relative).resolve()
    if target != base and base not in target.parents:
        raise ValueError('Kök dışındaki yol reddedildi')
    return target


def capture_source(url, kind, out=None):
    safe_url(url)
    if kind not in ('html', 'pdf'):
        raise ValueError('Desteklenmeyen kaynak türü')
    request = urllib.request.Request(url, headers={'User-Agent': 'proje-arastirma/1.0'})
    with urllib.request.urlopen(request, timeout=30) as response:
        final = safe_url(response.geturl())
        content = response.read(MAX_SOURCE + 1)
        mime = response.headers.get_content_type()
    if len(content) > MAX_SOURCE:
        raise ValueError('Kaynak boyut sınırını aşıyor')
    if not content or (kind == 'pdf' and not content.startswith(b'%PDF-')):
        raise ValueError('Kaynak boş veya beklenen türde değil')
    digest = hashlib.sha256(content).hexdigest()
    object_root = Path(out) if out else DATA / 'objects'
    folder = object_root / digest
    folder.mkdir(parents=True, exist_ok=True)
    original = folder / ('original.html.bin' if kind == 'html' else 'original.pdf')
    if original.exists() and sha(original) != digest:
        raise ValueError('Mevcut arşiv nesnesi bozuk')
    original.write_bytes(content)
    readable = folder / 'readable.html'
    decoded = content.decode('utf-8', errors='replace') if kind == 'html' else 'PDF dosyasını özgün kopyadan açın.'
    readable.write_text('<!doctype html><meta charset="utf-8"><title>Arşiv kopyası</title><pre>' + html.escape(decoded) + '</pre>', encoding='utf-8')
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    return dict(original_url=url, final_url=final, accessed_at=now, verified_at=now, mime=mime, sha256=digest, original_path=str(original.relative_to(DATA)) if original.is_relative_to(DATA) else str(original), readable_path=str(readable.relative_to(DATA)) if readable.is_relative_to(DATA) else str(readable))


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA journal_mode=DELETE')
    return db


def current():
    path = DATA / 'current.json'
    return json.loads(path.read_text(encoding='utf-8'))['release_id'] if path.exists() else None


def open_workspace(scratch=None):
    root = Path(scratch or tempfile.gettempdir()).resolve()
    root.mkdir(parents=True, exist_ok=True)
    fs = subprocess.check_output(['stat', '-f', '-c', '%T', str(root)], text=True).strip().lower()
    if fs in ('nfs', 'nfs4', 'cifs', 'smb2', 'fuse.sshfs'):
        raise ValueError('Aktif SQLite için yerel dosya sistemi gerekir')
    DATA.mkdir(parents=True, exist_ok=True)
    lock = DATA / '.write.lock'
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, json.dumps({'pid': os.getpid(), 'host': os.uname().nodename}).encode())
    finally:
        os.close(fd)
    try:
        base = current()
        work = Path(tempfile.mkdtemp(prefix='proje-work-', dir=root))
        if base:
            audit_release(base)
            shutil.copyfile(DATA / 'releases' / base / 'records.sqlite3', work / 'records.sqlite3')
        db = connect(work / 'records.sqlite3')
        for name, definition in TABLES.items():
            db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        db.commit()
        db.close()
        (work / 'workspace.json').write_text(json.dumps({'base': base, 'lock': str(lock)}), encoding='utf-8')
        return work
    except Exception:
        lock.unlink(missing_ok=True)
        raise


def record(work, kind, values):
    if kind not in TABLES or not isinstance(values, dict) or not values:
        raise ValueError('Geçersiz kayıt türü veya yükü')
    db = connect(Path(work) / 'records.sqlite3')
    try:
        allowed = {row['name'] for row in db.execute(f'PRAGMA table_info({kind})')}
        if not set(values) <= allowed:
            raise ValueError('Bilinmeyen kayıt alanı')
        if kind == 'document_version':
            safe_url(values['original_url']); safe_url(values['final_url'])
        keys = list(values)
        db.execute(f"INSERT INTO {kind} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", [values[k] for k in keys])
        db.commit()
    finally:
        db.close()


def export_db(path, release_id):
    db = connect(path)
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Veritabanı bütünlük hatası')
        result = {'schema_version': 1, 'release_id': release_id}
        for name in TABLES:
            result[name] = [dict(row) for row in db.execute(f'SELECT * FROM {name} ORDER BY rowid')]
        if any(not any(e['finding_id'] == f['id'] for e in result['finding_evidence']) for f in result['finding']):
            raise ValueError('Kanıtsız bulgu')
        for v in result['document_version']:
            safe_url(v['original_url']); safe_url(v['final_url'])
            original = safe_path(DATA, v['original_path']); safe_path(DATA, v['readable_path'])
            if sha(original) != v['sha256']:
                raise ValueError('Arşiv özeti eşleşmiyor')
        for p in result['passage']:
            v = next(v for v in result['document_version'] if v['id'] == p['version_id'])
            if p['exact'] not in safe_path(DATA, v['original_path']).read_bytes().decode('utf-8', errors='replace'):
                raise ValueError('Pasaj özgün belgede bulunamadı')
        return result
    finally:
        db.close()


def audit_release(release='current'):
    release = current() if release == 'current' else release
    if not release or not all(c in '0123456789abcdef' for c in release):
        raise ValueError('Geçersiz sürüm')
    folder = safe_path(DATA / 'releases', release)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if manifest['release_id'] != release or set(manifest['files']) != {'records.sqlite3', 'records.json', 'index.html'}:
        raise ValueError('Geçersiz manifest')
    for name, digest in manifest['files'].items():
        if sha(safe_path(folder, name)) != digest:
            raise ValueError('Manifest özeti eşleşmiyor')
    exported = export_db(folder / 'records.sqlite3', release)
    if json.loads((folder / 'records.json').read_text(encoding='utf-8')) != exported:
        raise ValueError('JSON kapalı snapshot ile eşleşmiyor')
    if (folder / 'index.html').read_text(encoding='utf-8') != render_report(exported):
        raise ValueError('HTML kapalı snapshot ile eşleşmiyor')
    return release


def publish_release(work, fail_at=None):
    work = Path(work)
    metadata = json.loads((work / 'workspace.json').read_text(encoding='utf-8'))
    if not Path(metadata['lock']).exists():
        raise ValueError('Yazıcı kilidi bulunamadı')
    release = uuid.uuid4().hex
    staging = DATA / '.staging' / release
    staging.mkdir(parents=True)
    try:
        if current() != metadata['base']:
            raise ValueError('Çalışma alanının taban sürümü eskidi')
        db = connect(work / 'records.sqlite3')
        db.commit(); db.close()
        if fail_at == 'close': raise RuntimeError('Enjekte edilen kapatma hatası')
        shutil.copyfile(work / 'records.sqlite3', staging / 'records.sqlite3')
        payload = export_db(staging / 'records.sqlite3', release)
        (staging / 'records.json').write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        if fail_at == 'json': raise RuntimeError('Enjekte edilen JSON hatası')
        (staging / 'index.html').write_text(render_report(payload), encoding='utf-8')
        if fail_at == 'html': raise RuntimeError('Enjekte edilen HTML hatası')
        manifest = {'release_id': release, 'files': {n: sha(staging / n) for n in ('records.sqlite3', 'records.json', 'index.html')}}
        (staging / 'manifest.json').write_text(json.dumps(manifest, sort_keys=True), encoding='utf-8')
        if fail_at == 'validate': raise RuntimeError('Enjekte edilen doğrulama hatası')
        (DATA / 'releases').mkdir(exist_ok=True)
        os.rename(staging, DATA / 'releases' / release)
        audit_release(release)
        if current() != metadata['base']:
            raise ValueError('Çalışma alanının taban sürümü eskidi')
        tmp = DATA / ('.current-' + release + '.json')
        tmp.write_text(json.dumps({'release_id': release}) + '\n', encoding='utf-8')
        os.replace(tmp, DATA / 'current.json')
        if fail_at == 'after_current':
            audit_release(release)
            raise RuntimeError('İşaretçi sonrası doğrulanmış sürüm')
        return release
    finally:
        Path(metadata['lock']).unlink(missing_ok=True)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command', required=True)
    c = sub.add_parser('capture'); c.add_argument('--url', required=True); c.add_argument('--kind', choices=['html', 'pdf'], required=True); c.add_argument('--out')
    w = sub.add_parser('workspace'); w.add_argument('--scratch')
    r = sub.add_parser('record'); r.add_argument('--workspace', required=True); r.add_argument('--kind', required=True); r.add_argument('--input', default='-')
    pub = sub.add_parser('publish'); pub.add_argument('--workspace', required=True)
    a = sub.add_parser('audit'); a.add_argument('--release', default='current')
    s = sub.add_parser('serve'); s.add_argument('--host', default='127.0.0.1'); s.add_argument('--port', type=int, default=8000)
    args = p.parse_args()
    if args.command == 'capture': print(json.dumps(capture_source(args.url, args.kind, args.out), ensure_ascii=False))
    elif args.command == 'workspace': print(open_workspace(args.scratch))
    elif args.command == 'record':
        import sys
        record(args.workspace, args.kind, json.load(sys.stdin) if args.input == '-' else json.loads(Path(args.input).read_text(encoding='utf-8')))
    elif args.command == 'publish': print(publish_release(args.workspace))
    elif args.command == 'audit': print('AUDIT_OK', audit_release(args.release))
    elif args.command == 'serve':
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
        class Handler(SimpleHTTPRequestHandler):
            def translate_path(self, path):
                relative = urllib.parse.unquote(urllib.parse.urlsplit(path).path).lstrip('/')
                try: return str(safe_path(DATA, relative))
                except ValueError: return str(DATA / '.invalid-path')
            def end_headers(self):
                self.send_header('X-Content-Type-Options', 'nosniff')
                if urllib.parse.urlsplit(self.path).path.endswith('.bin'):
                    self.send_header('Content-Disposition', 'attachment')
                super().end_headers()
            def guess_type(self, path):
                return 'application/octet-stream' if path.endswith('.bin') else super().guess_type(path)
        ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
