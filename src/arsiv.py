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

TABLES.update({
    'scope_party': 'party_id TEXT PRIMARY KEY REFERENCES party(id), approved_order INTEGER NOT NULL UNIQUE, inclusion_reason TEXT NOT NULL, decision_origin TEXT NOT NULL',
    'scope_observation': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), observed_at TEXT NOT NULL, source_passage_id TEXT NOT NULL REFERENCES passage(id), representation_kind TEXT NOT NULL, discrepancy_reason TEXT',
    'scope_exclusion': 'name TEXT PRIMARY KEY, reason TEXT NOT NULL, decision_origin TEXT NOT NULL, evidence_passage_id TEXT REFERENCES passage(id)',
    'identity_observation': 'entity_id TEXT NOT NULL REFERENCES party(id), entity_kind TEXT NOT NULL, registry_key TEXT NOT NULL, valid_from TEXT, valid_to TEXT, passage_id TEXT NOT NULL REFERENCES passage(id), PRIMARY KEY(entity_kind, registry_key)',
    'person': 'id TEXT PRIMARY KEY, name TEXT NOT NULL',
    'membership': 'person_id TEXT NOT NULL REFERENCES person(id), party_id TEXT NOT NULL REFERENCES party(id), valid_from TEXT, valid_to TEXT, passage_id TEXT NOT NULL REFERENCES passage(id), PRIMARY KEY(person_id, party_id, passage_id)',
    'parliamentary_group': 'id TEXT PRIMARY KEY, name TEXT NOT NULL, passage_id TEXT NOT NULL REFERENCES passage(id)',
    'group_membership': 'person_id TEXT NOT NULL REFERENCES person(id), group_id TEXT NOT NULL REFERENCES parliamentary_group(id), valid_from TEXT, valid_to TEXT, passage_id TEXT NOT NULL REFERENCES passage(id), PRIMARY KEY(person_id, group_id, passage_id)',
    'method': 'id TEXT PRIMARY KEY, version INTEGER NOT NULL UNIQUE, cutoff_at TEXT NOT NULL, cutoff_capture_version_id TEXT NOT NULL REFERENCES document_version(id), cutoff_reason TEXT NOT NULL, pilot_reason TEXT NOT NULL, period_rule TEXT NOT NULL',
    'event_date': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), passage_id TEXT NOT NULL REFERENCES passage(id), event_at TEXT, date_precision TEXT NOT NULL, date_unknown_reason TEXT, scope_status TEXT NOT NULL',
    'accounting_period': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), passage_id TEXT NOT NULL REFERENCES passage(id), period_start TEXT, period_end TEXT, date_precision TEXT NOT NULL, date_unknown_reason TEXT'
})
LEGACY_TABLES = ('party', 'document', 'document_version', 'passage', 'finding', 'finding_evidence', 'comparison', 'comparison_evidence')


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


def readable_bytes(content, kind):
    decoded = content.decode('utf-8', errors='replace') if kind == 'html' else 'PDF dosyasını özgün kopyadan açın.'
    return ('<!doctype html><meta charset="utf-8"><title>Arşiv kopyası</title><pre>' + html.escape(decoded) + '</pre>').encode('utf-8')


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
    readable = folder / 'readable.html'
    derivative = readable_bytes(content, kind)
    if readable.exists() and readable.read_bytes() != derivative:
        raise ValueError('Mevcut okunabilir arşiv bozuk')
    if not original.exists(): original.write_bytes(content)
    if not readable.exists(): readable.write_bytes(derivative)
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
    if fs not in ('xfs', 'ext2/ext3', 'ext2', 'ext3', 'ext4', 'tmpfs', 'overlayfs', 'btrfs', 'zfs', 'apfs'):
        raise ValueError('Aktif SQLite için yerel dosya sistemi gerekir')
    DATA.mkdir(parents=True, exist_ok=True)
    lock = DATA / '.write.lock'
    token = uuid.uuid4().hex
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    try:
        os.write(fd, json.dumps({'pid': os.getpid(), 'host': os.uname().nodename, 'token': token}).encode())
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
        columns = {r['name'] for r in db.execute('PRAGMA table_info(document_version)')}
        for column in ('date_precision', 'date_unknown_reason'):
            if column not in columns:
                db.execute(f'ALTER TABLE document_version ADD COLUMN {column} TEXT')
        if 'date_precision' not in columns:
            db.execute("UPDATE document_version SET date_precision=CASE WHEN document_date IS NULL THEN 'unknown' ELSE 'day' END, date_unknown_reason=CASE WHEN document_date IS NULL THEN 'Belge tarihi kaynakta belirtilmemiş veya doğrulanmamış.' ELSE NULL END")
        db.commit()
        db.close()
        (work / 'workspace.json').write_text(json.dumps({'base': base, 'token': token}), encoding='utf-8')
        return work
    except Exception:
        lock.unlink(missing_ok=True)
        raise


def record(work, kind, values):
    if kind not in TABLES or not isinstance(values, dict) or not values:
        raise ValueError('Geçersiz kayıt türü veya yükü')
    assert_lock(work)
    db = connect(Path(work) / 'records.sqlite3')
    try:
        allowed = {row['name'] for row in db.execute(f'PRAGMA table_info({kind})')}
        if not set(values) <= allowed:
            raise ValueError('Bilinmeyen kayıt alanı')
        if kind == 'document_version':
            safe_url(values['original_url']); safe_url(values['final_url'])
            if values.get('document_date') is None and not values.get('date_unknown_reason'):
                raise ValueError('Bilinmeyen belge tarihi için gerekçe gerekli')
        if kind == 'identity_observation':
            party = db.execute('SELECT registry_key FROM party WHERE id=?', (values['entity_id'],)).fetchone()
            if not party or party['registry_key'] != values['registry_key']:
                raise ValueError('Kimlik anahtarı parti kaydıyla eşleşmiyor')
        if kind == 'method':
            raise ValueError('Yöntem kesimi freeze komutuyla kaydedilir')
        if kind == 'event_date':
            method = db.execute('SELECT cutoff_at FROM method ORDER BY version DESC LIMIT 1').fetchone()
            if not method:
                raise ValueError('Önce yöntem kesimi dondurulmalı')
            if values.get('party_id') != 'yeni-parti':
                raise ValueError('Parti kuruluş tarihi henüz doğrulanmadı')
            status = validate_dates(values.get('event_at'), values.get('date_precision'), '2026-07-24', method['cutoff_at'], values.get('date_unknown_reason'))
            if status == 'outside' or values.get('scope_status') != status:
                raise ValueError('Olay dönem dışında veya belirsizlik yanlış belirtilmiş')
        if kind == 'accounting_period':
            if values.get('party_id') != 'yeni-parti': raise ValueError('Parti kuruluş tarihi henüz doğrulanmadı')
            start, end = values.get('period_start'), values.get('period_end')
            if not start or not end:
                if values.get('date_precision') != 'unknown' or not values.get('date_unknown_reason'):
                    raise ValueError('Eksik hesap dönemi gerekçesi gerekli')
            else:
                if values.get('date_precision') != 'day' or dt.date.fromisoformat(start) < dt.date(2026, 7, 24) or dt.date.fromisoformat(end) < dt.date.fromisoformat(start):
                    raise ValueError('Geçersiz hesap dönemi')
        keys = list(values)
        db.execute(f"INSERT INTO {kind} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", [values[k] for k in keys])
        db.commit()
    finally:
        db.close()


def record_scope(work, kind, values):
    if kind not in ('scope_party', 'scope_observation', 'scope_exclusion'):
        raise ValueError('Geçersiz kapsam türü')
    record(work, kind, values)


def record_identity(work, kind, values):
    if kind not in ('identity_observation', 'person', 'membership', 'parliamentary_group', 'group_membership'):
        raise ValueError('Geçersiz kimlik türü')
    record(work, kind, values)


def validate_dates(event, precision, founding, cutoff, unknown_reason=None):
    start = dt.date.fromisoformat(founding)
    limit = dt.datetime.fromisoformat(cutoff.replace('Z', '+00:00'))
    if limit.tzinfo is None:
        raise ValueError('Kesim zaman dilimi içermeli')
    limit = limit.astimezone(dt.timezone.utc)
    if event is None:
        if not unknown_reason or precision != 'unknown':
            raise ValueError('Bilinmeyen tarih gerekçesi gerekli')
        return 'uncertain'
    if precision == 'day':
        day = dt.date.fromisoformat(event)
        return 'outside' if day < start or day > limit.date() else ('uncertain' if day == limit.date() else 'inside')
    if precision == 'instant':
        instant = dt.datetime.fromisoformat(event.replace('Z', '+00:00'))
        if instant.tzinfo is None: raise ValueError('Olay zaman dilimi içermeli')
        instant = instant.astimezone(dt.timezone.utc)
        return 'inside' if start <= instant.date() and instant <= limit else 'outside'
    raise ValueError('Geçersiz tarih kesinliği')


def freeze_cutoff(work, tbmm_version, version=1):
    assert_lock(work)
    db = connect(Path(work) / 'records.sqlite3')
    try:
        row = db.execute('SELECT v.*, d.source_kind FROM document_version v JOIN document d ON d.id=v.document_id WHERE v.id=?', (tbmm_version,)).fetchone()
        existing = db.execute('SELECT * FROM method WHERE version=?', (version,)).fetchone()
        if existing:
            if existing['cutoff_capture_version_id'] != tbmm_version: raise ValueError('Yeni kesim için yeni yöntem sürümü gerekir')
            return existing['cutoff_at']
        observed = db.execute('SELECT 1 FROM scope_observation o JOIN passage p ON p.id=o.source_passage_id WHERE p.version_id=? LIMIT 1', (tbmm_version,)).fetchone()
        if not row or not observed or row['source_kind'] != 'official' or urllib.parse.urlsplit(row['final_url']).hostname not in ('tbmm.gov.tr', 'www.tbmm.gov.tr'):
            raise ValueError('Kesim doğrulanmış TBMM kapsam kopyası olmalı')
        latest = db.execute('SELECT MAX(version) FROM method').fetchone()[0]
        if version != (latest or 0) + 1: raise ValueError('Yöntem sürümleri ardışık olmalı')
        if version == 1:
            first = db.execute("SELECT v.id FROM document_version v JOIN passage p ON p.version_id=v.id JOIN scope_observation o ON o.source_passage_id=p.id JOIN document d ON d.id=v.document_id WHERE d.source_kind='official' ORDER BY v.accessed_at LIMIT 1").fetchone()
            if not first or first['id'] != tbmm_version: raise ValueError('İlk TBMM kapsam yakalaması gerekli')
        if sha(safe_path(DATA, row['original_path'])) != row['sha256']: raise ValueError('TBMM kopyası bozuk')
        cutoff = row['accessed_at']
        validate_dates('2026-07-24', 'day', '2026-07-24', cutoff)
        db.execute('INSERT INTO method VALUES (?,?,?,?,?,?,?)', (f'method-{version}',version,cutoff,tbmm_version,'İçeriği doğrulanan TBMM kapsam yakalamasının erişim anı; kullanıcı seçimi değildir.','Pilot Yeni Parti kullanıcının seçimidir; siyasi sıralama değildir.','Başlangıç doğrulanmış kuruluş günüdür (24.07.2026); kesim anı dahildir. Sonraki parti dosyalarında kendi kuruluş tarihi uygulanır.'))
        db.commit()
        return cutoff
    finally:
        db.close()


def export_db(path, release_id):
    db = connect(path)
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Veritabanı bütünlük hatası')
        existing = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        names = [n for n in TABLES if n in existing] if 'scope_party' in existing else LEGACY_TABLES
        cols = {r['name'] for r in db.execute('PRAGMA table_info(document_version)')}
        result = {'schema_version': 3 if 'date_precision' in cols else (2 if 'scope_party' in existing else 1), 'release_id': release_id}
        for name in names:
            result[name] = [dict(row) for row in db.execute(f'SELECT * FROM {name} ORDER BY rowid')]
        if result['schema_version'] == 3:
            versions = {v['id']: v for v in result['document_version']}
            for method in result['method']:
                v = versions[method['cutoff_capture_version_id']]
                if method['cutoff_at'] != v['accessed_at'] or urllib.parse.urlsplit(v['final_url']).hostname not in ('tbmm.gov.tr', 'www.tbmm.gov.tr'):
                    raise ValueError('Kesim kaynak yakalaması ile eşleşmiyor')
            if result['event_date'] and not result['method']: raise ValueError('Olay için yöntem kesimi gerekli')
            for event in result['event_date']:
                method = max(result['method'], key=lambda m: m['version'])
                if event['party_id'] != 'yeni-parti': raise ValueError('Kuruluş tarihi doğrulanmadı')
                actual = validate_dates(event['event_at'], event['date_precision'], '2026-07-24', method['cutoff_at'], event['date_unknown_reason'])
                if actual == 'outside' or actual != event['scope_status']: raise ValueError('Olay kapsamı geçersiz')
        if any(not any(e['finding_id'] == f['id'] for e in result['finding_evidence']) for f in result['finding']):
            raise ValueError('Kanıtsız bulgu')
        for v in result['document_version']:
            safe_url(v['original_url']); safe_url(v['final_url'])
            original = safe_path(DATA, v['original_path']); readable = safe_path(DATA, v['readable_path'])
            if sha(original) != v['sha256']:
                raise ValueError('Arşiv özeti eşleşmiyor')
            kind = 'pdf' if original.name == 'original.pdf' else 'html'
            if readable.read_bytes() != readable_bytes(original.read_bytes(), kind):
                raise ValueError('Okunabilir arşiv özgün belgeden farklı')
        for p in result['passage']:
            v = next(v for v in result['document_version'] if v['id'] == p['version_id'])
            if p['exact'] not in safe_path(DATA, v['original_path']).read_bytes().decode('utf-8', errors='replace'):
                raise ValueError('Pasaj özgün belgede bulunamadı')
        for f in result['finding']:
            if f['provenance'] == 'quote' and not any(f['text'] == p['exact'] for e in result['finding_evidence'] if e['finding_id'] == f['id'] for p in result['passage'] if p['id'] == e['passage_id']):
                raise ValueError('Alıntı kanıt pasajıyla eşleşmiyor')
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


def assert_lock(work):
    metadata = json.loads((Path(work) / 'workspace.json').read_text(encoding='utf-8'))
    lock = DATA / '.write.lock'
    if not lock.is_file() or json.loads(lock.read_text(encoding='utf-8')).get('token') != metadata.get('token') or not metadata.get('token'):
        raise ValueError('Çalışma alanının yazıcı kilidi bulunamadı')
    return metadata


def publish_release(work, fail_at=None):
    work = Path(work)
    metadata = assert_lock(work)
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
        if (DATA / '.write.lock').exists():
            try:
                assert_lock(work)
            except (ValueError, OSError, json.JSONDecodeError):
                pass
            else:
                (DATA / '.write.lock').unlink()


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='command', required=True)
    c = sub.add_parser('capture'); c.add_argument('--url', required=True); c.add_argument('--kind', choices=['html', 'pdf'], required=True); c.add_argument('--out')
    w = sub.add_parser('workspace'); w.add_argument('--scratch')
    r = sub.add_parser('record'); r.add_argument('--workspace', required=True); r.add_argument('--kind', required=True); r.add_argument('--input', default='-')
    pub = sub.add_parser('publish'); pub.add_argument('--workspace', required=True)
    f = sub.add_parser('freeze'); f.add_argument('--workspace', required=True); f.add_argument('--tbmm-version', required=True); f.add_argument('--method-version', type=int, default=1)
    a = sub.add_parser('audit'); a.add_argument('--release', default='current')
    s = sub.add_parser('serve'); s.add_argument('--host', default='127.0.0.1'); s.add_argument('--port', type=int, default=8000)
    args = p.parse_args()
    if args.command == 'capture': print(json.dumps(capture_source(args.url, args.kind, args.out), ensure_ascii=False))
    elif args.command == 'workspace': print(open_workspace(args.scratch))
    elif args.command == 'record':
        import sys
        record(args.workspace, args.kind, json.load(sys.stdin) if args.input == '-' else json.loads(Path(args.input).read_text(encoding='utf-8')))
    elif args.command == 'publish': print(publish_release(args.workspace))
    elif args.command == 'freeze': print(freeze_cutoff(args.workspace, args.tbmm_version, args.method_version))
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
