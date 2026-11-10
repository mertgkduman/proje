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
import ctypes
import ctypes.util

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
TABLES.update({
    'lead': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), heading TEXT NOT NULL, topic_id TEXT NOT NULL, url TEXT NOT NULL, normalized_url TEXT NOT NULL, relevance_reason TEXT NOT NULL, status TEXT NOT NULL',
    'edge': 'from_version_id TEXT NOT NULL REFERENCES document_version(id), to_lead_id TEXT NOT NULL REFERENCES lead(id), relation TEXT NOT NULL, relevance_reason TEXT NOT NULL, PRIMARY KEY(from_version_id,to_lead_id,relation)',
    'url_alias': 'original_url TEXT NOT NULL, final_url TEXT NOT NULL, version_id TEXT NOT NULL REFERENCES document_version(id), PRIMARY KEY(original_url,final_url,version_id)',
    'attempt': 'id TEXT PRIMARY KEY, lead_id TEXT REFERENCES lead(id), party_id TEXT NOT NULL REFERENCES party(id), heading TEXT NOT NULL, topic_id TEXT NOT NULL, type TEXT NOT NULL, query TEXT NOT NULL, attempted_at TEXT NOT NULL, result TEXT NOT NULL, reason TEXT NOT NULL, source_version_id TEXT REFERENCES document_version(id)',
    'topic_search': 'topic_id TEXT PRIMARY KEY, method_version INTEGER NOT NULL, state TEXT NOT NULL',
    'closure': 'id TEXT PRIMARY KEY, topic_id TEXT NOT NULL REFERENCES topic_search(topic_id), closed_at TEXT NOT NULL, reason TEXT NOT NULL, residual_leads TEXT NOT NULL',
    'reopen': 'closure_id TEXT NOT NULL REFERENCES closure(id), lead_id TEXT NOT NULL REFERENCES lead(id), opened_at TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(closure_id,lead_id)',
    'missing': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), heading TEXT NOT NULL, topic_id TEXT NOT NULL, status TEXT NOT NULL, attempt_id TEXT NOT NULL REFERENCES attempt(id), reason TEXT NOT NULL'
    , 'research_state': 'party_id TEXT NOT NULL REFERENCES party(id), heading TEXT NOT NULL, state TEXT NOT NULL, PRIMARY KEY(party_id,heading)'
    , 'report_option': 'name TEXT PRIMARY KEY, value TEXT NOT NULL'
})
TABLES.update({
    'manual_passage': 'passage_id TEXT PRIMARY KEY REFERENCES passage(id), checked_at TEXT NOT NULL, method TEXT NOT NULL, reason TEXT NOT NULL',
    'document_authority': 'version_id TEXT PRIMARY KEY REFERENCES document_version(id), registry_party_id TEXT NOT NULL REFERENCES party(id), authority_passage_id TEXT NOT NULL REFERENCES passage(id), verification_attempt_id TEXT NOT NULL REFERENCES attempt(id), status TEXT NOT NULL, reason TEXT NOT NULL',
    'verification': 'finding_id TEXT NOT NULL REFERENCES finding(id), passage_id TEXT NOT NULL REFERENCES passage(id), checked_at TEXT NOT NULL, result TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(finding_id,passage_id)',
    'topic': 'id TEXT NOT NULL, label TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, valid_from TEXT NOT NULL, status TEXT NOT NULL, change_reason TEXT NOT NULL, PRIMARY KEY(id,taxonomy_version)',
    'topic_basis': 'topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, passage_id TEXT NOT NULL REFERENCES passage(id), rationale TEXT NOT NULL, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES topic(id,taxonomy_version), PRIMARY KEY(topic_id,taxonomy_version,passage_id)',
    'finding_topic': 'finding_id TEXT NOT NULL REFERENCES finding(id), topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES topic(id,taxonomy_version), PRIMARY KEY(finding_id,topic_id,taxonomy_version)',
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


def pdf_page_text(path, index):
    name = ctypes.util.find_library('poppler-glib')
    if not name: raise ValueError('PDF pasaj doğrulaması için Poppler gerekli')
    pop = ctypes.CDLL(name)
    obj = ctypes.CDLL(ctypes.util.find_library('gobject-2.0'))
    glib = ctypes.CDLL(ctypes.util.find_library('glib-2.0'))
    pop.poppler_document_new_from_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p]
    pop.poppler_document_new_from_file.restype = ctypes.c_void_p
    pop.poppler_document_get_page.argtypes = [ctypes.c_void_p, ctypes.c_int]
    pop.poppler_document_get_page.restype = ctypes.c_void_p
    pop.poppler_page_get_text.argtypes = [ctypes.c_void_p]
    pop.poppler_page_get_text.restype = ctypes.c_void_p
    obj.g_object_unref.argtypes = [ctypes.c_void_p]
    glib.g_free.argtypes = [ctypes.c_void_p]
    document = pop.poppler_document_new_from_file(Path(path).resolve().as_uri().encode(), None, None)
    if not document: raise ValueError('PDF açılamadı')
    page = None
    text_ptr = None
    try:
        page = pop.poppler_document_get_page(document, index)
        if not page: raise ValueError('PDF sayfası bulunamadı')
        text_ptr = pop.poppler_page_get_text(page)
        if not text_ptr: raise ValueError('PDF sayfasında metin bulunamadı')
        return ctypes.string_at(text_ptr).decode('utf-8')
    finally:
        if text_ptr: glib.g_free(text_ptr)
        if page: obj.g_object_unref(page)
        obj.g_object_unref(document)


def pdf_page_exists(path, index):
    pop = ctypes.CDLL(ctypes.util.find_library('poppler-glib'))
    obj = ctypes.CDLL(ctypes.util.find_library('gobject-2.0'))
    pop.poppler_document_new_from_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p]
    pop.poppler_document_new_from_file.restype = ctypes.c_void_p
    pop.poppler_document_get_n_pages.argtypes = [ctypes.c_void_p]
    pop.poppler_document_get_n_pages.restype = ctypes.c_int
    obj.g_object_unref.argtypes = [ctypes.c_void_p]
    document = pop.poppler_document_new_from_file(Path(path).resolve().as_uri().encode(), None, None)
    if not document: return False
    try: return 0 <= index < pop.poppler_document_get_n_pages(document)
    finally: obj.g_object_unref(document)


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
    if kind in ('lead', 'attempt', 'closure', 'reopen', 'missing', 'document_authority', 'topic'):
        return {'lead': enqueue_lead, 'attempt': record_attempt, 'closure': close_topic, 'reopen': reopen_topic, 'missing': record_missing, 'document_authority': verify_document_authority, 'topic': record_topic}[kind](work, values)
    db = connect(Path(work) / 'records.sqlite3')
    try:
        allowed = {row['name'] for row in db.execute(f'PRAGMA table_info({kind})')}
        if not set(values) <= allowed:
            raise ValueError('Bilinmeyen kayıt alanı')
        if kind == 'document_version':
            safe_url(values['original_url']); safe_url(values['final_url'])
            if values.get('document_date') is None and (values.get('date_precision') != 'unknown' or not values.get('date_unknown_reason')):
                raise ValueError('Bilinmeyen belge tarihi için gerekçe gerekli')
            duplicate = db.execute('SELECT id FROM document_version WHERE sha256=?', (values['sha256'],)).fetchone()
            if duplicate:
                db.execute('INSERT OR IGNORE INTO url_alias VALUES (?,?,?)', (values['original_url'],values['final_url'],duplicate['id']))
                db.commit()
                return duplicate['id']
        if kind == 'edge':
            if values.get('relation') not in ('reference','contradiction','new_version') or not values.get('relevance_reason'): raise ValueError('İlgili kenar ve gerekçe gerekli')
        if kind == 'research_state' and values.get('state') not in ('not_researched','in_progress','reviewed'):
            raise ValueError('Geçersiz araştırma durumu')
        if kind == 'report_option' and values != {'name': 'chain_links', 'value': '1'}:
            raise ValueError('Geçersiz rapor seçeneği')
        if kind in ('topic_search', 'url_alias'):
            raise ValueError('Durum ve takma adlar ilgili işlem tarafından yönetilir')
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
        if kind == 'document_version':
            db.execute('INSERT OR IGNORE INTO url_alias VALUES (?,?,?)', (values['original_url'], values['final_url'], values['id']))
            for lead in db.execute("SELECT l.id,l.topic_id FROM lead l JOIN topic_search t ON t.topic_id=l.topic_id WHERE t.state='closed' AND l.normalized_url=?", (normalize_url(values['original_url']),)).fetchall():
                closure = db.execute('SELECT id FROM closure WHERE topic_id=? ORDER BY rowid DESC LIMIT 1', (lead['topic_id'],)).fetchone()
                db.execute('INSERT OR IGNORE INTO reopen VALUES (?,?,?,?)', (closure['id'],lead['id'],values['accessed_at'],'Aynı adreste yeni içerik sürümü'))
                db.execute("UPDATE topic_search SET state='in_progress' WHERE topic_id=?", (lead['topic_id'],))
                db.execute("UPDATE lead SET status='pending' WHERE id=?", (lead['id'],))
        db.commit()
    finally:
        db.close()


def normalize_url(url):
    p = urllib.parse.urlsplit(safe_url(url))
    query = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    query = [(k, v) for k, v in query if not k.lower().startswith('utm_') and k.lower() not in ('fbclid', 'gclid')]
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or '/', urllib.parse.urlencode(query, doseq=True), ''))


def insert_checked(work, table, values, validate):
    assert_lock(work)
    db = connect(Path(work) / 'records.sqlite3')
    try:
        if not set(values) <= {r['name'] for r in db.execute(f'PRAGMA table_info({table})')}:
            raise ValueError('Bilinmeyen kayıt alanı')
        validate(db, values)
        keys = list(values)
        db.execute(f"INSERT INTO {table} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", [values[k] for k in keys])
        db.commit()
    finally:
        db.close()


def enqueue_lead(work, values):
    values = dict(values)
    values['normalized_url'] = normalize_url(values['url'])
    values.setdefault('status', 'pending')
    assert_lock(work)
    db = connect(Path(work) / 'records.sqlite3')
    try:
        v = values
        if not set(v) <= {r['name'] for r in db.execute('PRAGMA table_info(lead)')}: raise ValueError('Bilinmeyen kayıt alanı')
        if not v.get('relevance_reason') or v['status'] != 'pending': raise ValueError('Yeni ilgili uç ve gerekçe gerekli')
        duplicate = db.execute('SELECT id FROM lead WHERE party_id=? AND topic_id=? AND normalized_url=?', (v['party_id'],v['topic_id'],v['normalized_url'])).fetchone()
        if duplicate: return duplicate['id']
        db.execute("INSERT OR IGNORE INTO topic_search VALUES (?,1,'in_progress')", (v['topic_id'],))
        closed = db.execute('SELECT state FROM topic_search WHERE topic_id=?', (v['topic_id'],)).fetchone()[0] == 'closed'
        keys = list(v)
        db.execute(f"INSERT INTO lead ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", [v[k] for k in keys])
        if closed:
            closure = db.execute('SELECT id FROM closure WHERE topic_id=? ORDER BY rowid DESC LIMIT 1', (v['topic_id'],)).fetchone()
            db.execute('INSERT INTO reopen VALUES (?,?,?,?)', (closure[0],v['id'],dt.datetime.now(dt.timezone.utc).isoformat(),'Yeni ilgili uç: '+v['relevance_reason']))
            db.execute("UPDATE topic_search SET state='in_progress' WHERE topic_id=?", (v['topic_id'],))
        db.commit()
        return v['id']
    finally: db.close()


def record_attempt(work, values):
    def validate(db, v):
        if not all(v.get(k) for k in ('query','attempted_at','reason','type','result')): raise ValueError('Girişim alanları gerekli')
        if dt.datetime.fromisoformat(v['attempted_at'].replace('Z','+00:00')).tzinfo is None: raise ValueError('Girişim zaman dilimi içermeli')
        if (v['type'], v['result']) not in (('search','no_result'), ('search','results'), ('access','failure'), ('access','examined'), ('verification','inconclusive'), ('verification','confirmed'), ('review','excluded')):
            raise ValueError('Girişim türü ve sonucu uyuşmuyor')
        if v.get('lead_id'):
            lead = db.execute('SELECT * FROM lead WHERE id=?', (v['lead_id'],)).fetchone()
            if not lead or any(lead[k] != v[k] for k in ('party_id','topic_id','heading')): raise ValueError('Girişim uçla uyuşmuyor')
            if v['type'] == 'access' and normalize_url(v['query']) != lead['normalized_url']:
                raise ValueError('Erişim adresi uçla uyuşmuyor')
        if v.get('lead_id'):
            state = {'examined':'examined','failure':'blocked','excluded':'excluded'}.get(v['result'])
            if state == 'examined' and not v.get('source_version_id'): raise ValueError('İncelenmiş uç için belge gerekli')
            if state: db.execute('UPDATE lead SET status=? WHERE id=?', (state,v['lead_id']))
    insert_checked(work, 'attempt', values, validate)


def verify_document_authority(work, values):
    def validate(db, v):
        target = db.execute('SELECT d.party_id,v.final_url FROM document_version v JOIN document d ON d.id=v.document_id WHERE v.id=?', (v['version_id'],)).fetchone()
        source = db.execute('SELECT p.exact,d.party_id,d.source_kind,v.final_url FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (v['authority_passage_id'],)).fetchone()
        attempt = db.execute('SELECT * FROM attempt WHERE id=?', (v['verification_attempt_id'],)).fetchone()
        if not target or not source or not attempt or not v.get('reason') or v.get('status') != 'verified': raise ValueError('Otorite zinciri eksik')
        host = urllib.parse.urlsplit(target['final_url']).hostname or ''
        source_host = urllib.parse.urlsplit(source['final_url']).hostname or ''
        if target['party_id'] != v['registry_party_id'] or source['party_id'] != v['registry_party_id'] or source['source_kind'] != 'official' or source_host not in ('tbmm.gov.tr','www.tbmm.gov.tr','cdn.tbmm.gov.tr') or host.removeprefix('www.') not in source['exact'] or attempt['party_id'] != v['registry_party_id'] or (attempt['type'],attempt['result']) != ('verification','confirmed'):
            raise ValueError('Parti veya resmî otorite zinciri uyuşmuyor')
    insert_checked(work, 'document_authority', values, validate)


def record_topic(work, values):
    def validate(db, v):
        if v.get('status') not in ('candidate','verified') or not v.get('label') or not v.get('change_reason') or not v.get('valid_from') or not isinstance(v.get('taxonomy_version'), int) or v['taxonomy_version'] < 1:
            raise ValueError('Konu sürümü ve gerekçesi gerekli')
    insert_checked(work, 'topic', values, validate)


def validate_evidence(db, finding, passage):
    row = db.execute('SELECT d.party_id,d.source_kind,v.id AS version_id FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (passage['id'],)).fetchone()
    if not row or row['party_id'] != finding['party_id']: raise ValueError('Kanıt başka partiye ait')
    if finding['provenance'] == 'quote' and finding['text'] not in passage['exact']: raise ValueError('Alıntı pasajda bulunamadı')
    if finding['heading'] in ('Tüzük','Program') and not db.execute("SELECT 1 FROM document_authority WHERE version_id=? AND registry_party_id=? AND status='verified'", (row['version_id'],finding['party_id'])).fetchone(): raise ValueError('Belge otoritesi doğrulanmadı')
    if finding['heading'] == 'Söylem ve uygulama' and finding['epistemic_type'] == 'fact' and row['source_kind'] == 'party': raise ValueError('Parti beyanı uygulama olgusu olarak kullanılamaz')


def close_topic(work, values):
    def validate(db, v):
        if not v.get('reason') or not v.get('closed_at'): raise ValueError('Kapanma gerekçesi ve tarihi gerekli')
        state = db.execute('SELECT state FROM topic_search WHERE topic_id=?', (v['topic_id'],)).fetchone()
        if not state or state['state'] != 'in_progress': raise ValueError('Konu açık değil')
        leads = db.execute('SELECT * FROM lead WHERE topic_id=?', (v['topic_id'],)).fetchall()
        if not leads: raise ValueError('Uçsuz tarama kapanamaz')
        for lead in leads:
            if lead['status'] not in ('examined', 'blocked', 'excluded'): raise ValueError('İncelenmemiş uç var')
            attempt = db.execute('SELECT * FROM attempt WHERE lead_id=? ORDER BY attempted_at DESC LIMIT 1', (lead['id'],)).fetchone()
            expected = {'examined':'examined','blocked':'failure','excluded':'excluded'}[lead['status']]
            if not attempt or not attempt['reason'] or attempt['result'] != expected or (lead['status'] == 'examined' and not attempt['source_version_id']): raise ValueError('Uç gerçek girişimle desteklenmeli')
        db.execute("UPDATE topic_search SET state='closed' WHERE topic_id=?", (v['topic_id'],))
    insert_checked(work, 'closure', values, validate)


def reopen_topic(work, values):
    def validate(db, v):
        if not v.get('reason') or not v.get('opened_at'): raise ValueError('Yeniden açma gerekçesi gerekli')
        closure = db.execute('SELECT topic_id FROM closure WHERE id=?', (v['closure_id'],)).fetchone()
        lead = db.execute('SELECT topic_id FROM lead WHERE id=?', (v['lead_id'],)).fetchone()
        if not closure or not lead or closure[0] != lead[0]: raise ValueError('Konu uyuşmuyor')
        db.execute("UPDATE topic_search SET state='in_progress' WHERE topic_id=?", (closure[0],))
    insert_checked(work, 'reopen', values, validate)


def record_missing(work, values):
    def validate(db, v):
        a = db.execute('SELECT * FROM attempt WHERE id=?', (v['attempt_id'],)).fetchone()
        allowed = {'Bulunamadı': ('search','no_result'), 'Erişilemedi': ('access','failure'), 'Doğrulanamadı': ('verification','inconclusive')}
        if not a or any(a[k] != v[k] for k in ('party_id','heading','topic_id')) or allowed.get(v['status']) != (a['type'],a['result']) or not v.get('reason'):
            raise ValueError('Eksik durumuyla eşleşen gerekçeli girişim gerekli')
        if v['status'] == 'Erişilemedi' and not a['lead_id']:
            raise ValueError('Erişim engeli belirlenmiş bir kaynağa bağlanmalı')
    insert_checked(work, 'missing', values, validate)


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
            path = safe_path(DATA, v['original_path'])
            if path.name == 'original.pdf':
                if p['pdf_page_index'] is None or p['pdf_page_index'] < 0: raise ValueError('PDF sayfa indeksi gerekli')
                content = pdf_page_text(path, p['pdf_page_index'])
                manual = next((m for m in result.get('manual_passage', []) if m['passage_id'] == p['id']), None)
                if manual:
                    if not manual['checked_at'] or not manual['method'] or not manual['reason'] or not pdf_page_exists(path, p['pdf_page_index']): raise ValueError('PDF elle doğrulama kaydı geçersiz')
                    continue
            else: content = path.read_bytes().decode('utf-8', errors='replace')
            if p['exact'] not in content:
                raise ValueError('Pasaj özgün belgede bulunamadı')
        for f in result['finding']:
            if f['provenance'] == 'quote' and not any(f['text'] == p['exact'] for e in result['finding_evidence'] if e['finding_id'] == f['id'] for p in result['passage'] if p['id'] == e['passage_id']):
                raise ValueError('Alıntı kanıt pasajıyla eşleşmiyor')
            if 'document_authority' in existing:
                for e in (e for e in result['finding_evidence'] if e['finding_id'] == f['id']):
                    validate_evidence(db, f, next(p for p in result['passage'] if p['id'] == e['passage_id']))
        if 'topic' in existing:
            for t in result['topic']:
                if t['status'] == 'verified':
                    bases = [b for b in result['topic_basis'] if b['topic_id'] == t['id'] and b['taxonomy_version'] == t['taxonomy_version']]
                    if not bases: raise ValueError('Doğrulanmış konu dayanağı bulunamadı')
                    for b in bases:
                        row = db.execute("SELECT a.status,d.title FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id JOIN document_authority a ON a.version_id=v.id WHERE p.id=?", (b['passage_id'],)).fetchone()
                        if not b['rationale'] or not row or row['status'] != 'verified' or not any(x in row['title'].lower() for x in ('tüzük','program')): raise ValueError('Konu tüzük/program dayanağı geçersiz')
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
    ch = sub.add_parser('chain'); ch.add_argument('--workspace', required=True); ch.add_argument('--party', required=True); ch.add_argument('--topic', required=True)
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
    elif args.command == 'chain':
        assert_lock(args.workspace)
        db = connect(Path(args.workspace) / 'records.sqlite3')
        try:
            print(json.dumps([dict(x) for x in db.execute('SELECT * FROM lead WHERE party_id=? AND topic_id=? ORDER BY rowid', (args.party,args.topic))], ensure_ascii=False, indent=2))
        finally: db.close()
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
