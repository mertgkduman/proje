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
import re
from decimal import Decimal, InvalidOperation
from functools import lru_cache

from rapor import RENDERER_VERSION, render_report
from rapor_legacy import render_report as render_legacy_report
from rapor_v2 import render_report as render_v2_report
from rapor_v3 import render_report as render_v3_report
from rapor_v4 import render_report as render_v4_report
from rapor_v5 import render_report as render_v5_report
from rapor_v6 import render_report as render_v6_report
from rapor_v7 import render_report as render_v7_report
from rapor_v8 import render_report as render_v8_report
from rapor_v9 import render_report as render_v9_report
from rapor_v10 import render_report as render_v10_report
from rapor_v11 import render_report as render_v11_report
from rapor_v12 import render_report as render_v12_report
from rapor_v13 import render_report as render_v13_report
from rapor_v14 import render_report as render_v14_report
from rapor_v15 import render_report as render_v15_report
from rapor_v16 import render_report as render_v16_report
from rapor_v17 import render_report as render_v17_report
from rapor_v18 import render_report as render_v18_report
from rapor_v19 import render_report as render_v19_report
from rapor_v20 import render_report as render_v20_report
from rapor_v21 import render_report as render_v21_report
from rapor_v22 import render_report as render_v22_report
from kaynaklar import (POLICY_TABLES, active_policy, check_attribution, validate_policy,
                      check_evidence_attribution, validate_policy_descent)
from arsiv_gorunum import VIEW_TABLES, validate_view, decode_html, CSP as ARCHIVE_CSP
from dosyalar import (DOSSIER_TABLES, foundation_for_party, migrate_workspace,
                      validate_dossier, validate_delivery_prefix, DELIVERY_ORDER)

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
    'topic_basis': 'topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, passage_id TEXT NOT NULL REFERENCES passage(id), rationale TEXT NOT NULL, source_role TEXT, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES topic(id,taxonomy_version), PRIMARY KEY(topic_id,taxonomy_version,passage_id)',
    'finding_topic': 'finding_id TEXT NOT NULL REFERENCES finding(id), topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES topic(id,taxonomy_version), PRIMARY KEY(finding_id,topic_id,taxonomy_version)',
    'topic_query': 'topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, actor_kind TEXT NOT NULL, query TEXT NOT NULL, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES topic(id,taxonomy_version), PRIMARY KEY(topic_id,taxonomy_version,actor_kind)',
})
TABLES.update({
    'actor': 'id TEXT PRIMARY KEY, kind TEXT NOT NULL, party_id TEXT NOT NULL REFERENCES party(id), person_id TEXT REFERENCES person(id), authorization_passage_id TEXT REFERENCES passage(id)',
    'action': 'finding_id TEXT PRIMARY KEY REFERENCES finding(id), actor_id TEXT NOT NULL REFERENCES actor(id), event_date TEXT NOT NULL, date_precision TEXT NOT NULL, occurrence_passage_id TEXT NOT NULL REFERENCES passage(id), context TEXT NOT NULL',
    'match': 'id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, statement_finding_id TEXT NOT NULL REFERENCES finding(id), action_finding_id TEXT NOT NULL REFERENCES action(finding_id), relation TEXT NOT NULL, rationale TEXT NOT NULL, eligibility TEXT NOT NULL, exclusion_reason TEXT, reviewed_at TEXT NOT NULL'
})
TABLES.update({
    'match_candidate': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), topic_id TEXT NOT NULL, lead_id TEXT REFERENCES lead(id), passage_id TEXT REFERENCES passage(id), status TEXT NOT NULL, match_id TEXT REFERENCES match(id), missing_id TEXT REFERENCES missing(id), rationale TEXT NOT NULL, reviewed_at TEXT NOT NULL',
    'missing_resolution': 'missing_id TEXT PRIMARY KEY REFERENCES missing(id), resolved_at TEXT NOT NULL, passage_id TEXT NOT NULL REFERENCES passage(id), reason TEXT NOT NULL'
})
TABLES['financial'] = 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), version_id TEXT NOT NULL REFERENCES document_version(id), category TEXT NOT NULL, amount TEXT, currency TEXT NOT NULL, period_start TEXT NOT NULL, period_end TEXT NOT NULL, organization_scope TEXT NOT NULL, published_at TEXT NOT NULL, passage_id TEXT REFERENCES passage(id), missing_id TEXT REFERENCES missing(id), number_format TEXT'
TABLES['review'] = 'id TEXT PRIMARY KEY, kind TEXT NOT NULL, subject_id TEXT NOT NULL, reviewer_kind TEXT NOT NULL, reviewed_at TEXT NOT NULL, result TEXT NOT NULL, reason TEXT NOT NULL'
TABLES.update(DOSSIER_TABLES)
TABLES.update(POLICY_TABLES)
TABLES.update(VIEW_TABLES)
COMPARISON_TABLES = {
    'comparison_contract': 'version INTEGER PRIMARY KEY, taxonomy_version INTEGER NOT NULL, stage TEXT NOT NULL',
    'comparison_topic': 'topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, domain TEXT NOT NULL, parent_topic_id TEXT, order_index INTEGER NOT NULL, definition TEXT NOT NULL, applicable_levels TEXT NOT NULL, basis_kind TEXT NOT NULL, PRIMARY KEY(topic_id,taxonomy_version)',
    'comparison_row': 'id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, party_id TEXT NOT NULL REFERENCES party(id), level TEXT NOT NULL, organ TEXT NOT NULL, version_id TEXT REFERENCES document_version(id), alternative_group TEXT, source_role TEXT NOT NULL, state TEXT NOT NULL, scope_id TEXT, missing_id TEXT REFERENCES missing(id), selection_reason TEXT NOT NULL, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES comparison_topic(topic_id,taxonomy_version)',
    'comparison_field': 'id TEXT PRIMARY KEY, row_id TEXT NOT NULL REFERENCES comparison_row(id), field TEXT NOT NULL, summary_finding_id TEXT REFERENCES finding(id), quote_finding_id TEXT REFERENCES finding(id), condition_key TEXT',
    'comparison_review_scope': 'id TEXT PRIMARY KEY, party_id TEXT NOT NULL REFERENCES party(id), version_id TEXT NOT NULL REFERENCES document_version(id), sections TEXT NOT NULL, query_terms TEXT NOT NULL, reviewed_at TEXT NOT NULL, result TEXT NOT NULL, reason TEXT NOT NULL',
    'comparison_change': 'id TEXT PRIMARY KEY, row_id TEXT NOT NULL REFERENCES comparison_row(id), before_passage_id TEXT NOT NULL REFERENCES passage(id), after_passage_id TEXT NOT NULL REFERENCES passage(id), summary TEXT NOT NULL, order_basis TEXT NOT NULL',
    'comparison_synthesis': 'id TEXT PRIMARY KEY, topic_id TEXT NOT NULL, taxonomy_version INTEGER NOT NULL, text TEXT NOT NULL, FOREIGN KEY(topic_id,taxonomy_version) REFERENCES comparison_topic(topic_id,taxonomy_version)',
    'comparison_synthesis_evidence': 'synthesis_id TEXT NOT NULL REFERENCES comparison_synthesis(id), passage_id TEXT NOT NULL REFERENCES passage(id), PRIMARY KEY(synthesis_id,passage_id)',
    'comparison_semantic_review': 'subject_kind TEXT NOT NULL, subject_id TEXT NOT NULL, reviewer_kind TEXT NOT NULL, reviewed_at TEXT NOT NULL, result TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(subject_kind,subject_id,reviewer_kind)',
}
COMPARISON_INVENTORY_TABLE = 'id TEXT PRIMARY KEY, taxonomy_version INTEGER NOT NULL, party_id TEXT NOT NULL REFERENCES party(id), version_id TEXT REFERENCES document_version(id), source_role TEXT NOT NULL, section TEXT NOT NULL, page_range TEXT, full_text_available INTEGER NOT NULL, scanned_at TEXT NOT NULL, topic_ids TEXT NOT NULL, unmatched_headings TEXT NOT NULL, search_boundary TEXT NOT NULL, missing_id TEXT REFERENCES missing(id)'
COMPLETION_TABLE = 'version INTEGER NOT NULL, taxonomy_version INTEGER NOT NULL, evidence TEXT NOT NULL, PRIMARY KEY(version,taxonomy_version)'
# Identity of the already adopted v1 marker, not a semantic approval.  New
# closure decisions use v2; untrusted inputs cannot invent a weaker v1 proof.
LEGACY_COMPLETION_MARKERS = {(1, 4): '9413a4616f01dedebe47ca63dac068503e58cee09cee3e3e6a3e8512217827e8'}
# Optional v2 tables are append-only.  The v1 marker above is deliberately
# unchanged: existing closed snapshots retain their original interpretation.
COMPLETION_V2_TABLES = {
    'comparison_completion_basis': 'id TEXT PRIMARY KEY, version INTEGER NOT NULL, taxonomy_version INTEGER NOT NULL, parent_basis_id TEXT REFERENCES comparison_completion_basis(id), created_at TEXT NOT NULL, source_catalog TEXT NOT NULL, universe TEXT NOT NULL, inventory TEXT NOT NULL, risk_universe TEXT NOT NULL, source_assertions TEXT NOT NULL',
    'comparison_coverage_disposition': 'basis_id TEXT NOT NULL REFERENCES comparison_completion_basis(id), cell_id TEXT NOT NULL, logical_key TEXT NOT NULL, disposition TEXT NOT NULL, source_judgment TEXT NOT NULL, mapping_refs TEXT NOT NULL, basis_ids TEXT NOT NULL, field_dispositions TEXT NOT NULL, PRIMARY KEY(basis_id,cell_id)',
    'comparison_completion_revision': 'id TEXT PRIMARY KEY, version INTEGER NOT NULL, epoch INTEGER NOT NULL UNIQUE, parent_revision_id TEXT REFERENCES comparison_completion_revision(id), taxonomy_version INTEGER NOT NULL, basis_id TEXT NOT NULL REFERENCES comparison_completion_basis(id), stage TEXT NOT NULL, created_at TEXT NOT NULL, legacy_anchor TEXT, selection TEXT NOT NULL, review TEXT NOT NULL, reason TEXT NOT NULL',
    'comparison_completion_supersession': 'revision_id TEXT NOT NULL REFERENCES comparison_completion_revision(id), old_cell_id TEXT NOT NULL, new_cell_id TEXT NOT NULL, old_row_id TEXT NOT NULL, new_row_id TEXT NOT NULL, source_basis_refs TEXT NOT NULL, reason TEXT NOT NULL, PRIMARY KEY(revision_id,old_cell_id,new_cell_id)',
}
COMPLETION_MANIFEST_KEYS = ('comparison_completion_revision_id', 'comparison_completion_epoch',
                            'comparison_completion_basis_id', 'comparison_completion_stage',
                            'comparison_completion_basis_sha256', 'comparison_completion_selection_sha256',
                            'comparison_completion_review_sha256')


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def completion_basis_digest(basis):
    normalized = {k: v for k, v in basis.items() if not k.startswith('_')}
    normalized['cells'] = sorted(basis['cells'], key=lambda cell: cell['id'])
    return hashlib.sha256(canonical_json(normalized).encode()).hexdigest()


def completion_basis_records(basis, risk_universe, basis_id, created_at, parent_basis_id=None, *, reading_registry=None, correction_registry=None):
    """Encode authored source judgments for storage inside a closed snapshot."""
    catalog = {k: basis[k] for k in ('artifact_version', 'completion_contract_target', 'artifact_kind', 'reviewer_kind', 'origin_policy', 'new_source_reading_claim', 'human_acceptance', 'source_documents', 'unresolved')}
    catalog['reading_registry'] = reading_registry if reading_registry is not None else basis.get('_reading_registry')
    catalog['correction_registry'] = correction_registry if correction_registry is not None else basis.get('_correction_registry', [])
    head = dict(id=basis_id, version=2, taxonomy_version=basis['taxonomy_version'],
                parent_basis_id=parent_basis_id, created_at=created_at,
                source_catalog=canonical_json(catalog),
                universe=canonical_json({k: basis[k] for k in ('topics', 'topic_bases', 'universe')}),
                inventory=canonical_json(basis['inventory_sections']),
                risk_universe=canonical_json(risk_universe),
                source_assertions=canonical_json({'source_assertions': basis['source_assertions'],
                                                  'synthesis_obligations': basis['synthesis_obligations']}))
    dispositions = [dict(basis_id=basis_id, cell_id=c['id'], logical_key=canonical_json(c['logical_key']),
                         disposition=c['disposition'],
                         source_judgment=canonical_json({'reference': c['source_judgment'], 'record': c['source_judgment_record'],
                                                         'inventory_section_indexes': c.get('inventory_section_indexes', []),
                                                         'fulfilment_locator_only': c.get('fulfilment_locator_only')}),
                         mapping_refs=canonical_json({'references': c['mapping_refs'], 'records': c['mapping_records']}),
                         basis_ids=canonical_json(c['basis_ids']), field_dispositions=canonical_json(c['field_dispositions']))
                    for c in basis['cells']]
    return head, dispositions


def decode_completion_basis(head, dispositions):
    """Restore source content without consulting mutable research files."""
    try:
        catalog = json.loads(head['source_catalog'])
        reading_registry = catalog.pop('reading_registry', None)
        correction_registry = catalog.pop('correction_registry', None)
        result = dict(catalog, **json.loads(head['universe']),
                      taxonomy_version=head['taxonomy_version'], inventory_sections=json.loads(head['inventory']),
                      **json.loads(head['source_assertions']))
        result['_reading_registry'] = reading_registry
        result['_correction_registry'] = correction_registry
        risk = json.loads(head['risk_universe'])
        result['cells'] = []
        for item in dispositions:
            source, mapping = json.loads(item['source_judgment']), json.loads(item['mapping_refs'])
            result['cells'].append(dict(id=item['cell_id'], logical_key=json.loads(item['logical_key']),
                                        disposition=item['disposition'], source_judgment=source['reference'],
                                        source_judgment_record=source['record'], mapping_refs=mapping['references'],
                                        mapping_records=mapping['records'], basis_ids=json.loads(item['basis_ids']),
                                        field_dispositions=json.loads(item['field_dispositions']),
                                        inventory_section_indexes=source['inventory_section_indexes'],
                                        fulfilment_locator_only=source['fulfilment_locator_only']))
        return result, risk
    except (ValueError, TypeError, KeyError) as exc:
        raise ValueError('Kaynak kapanışı sözlüğü çözümlenemedi') from exc
LINEAGE_TABLES = {
    'comparison_lineage_contract': 'version INTEGER PRIMARY KEY, first_taxonomy_version INTEGER NOT NULL',
    'comparison_row_lineage': 'old_row_id TEXT NOT NULL REFERENCES comparison_row(id), new_row_id TEXT NOT NULL REFERENCES comparison_row(id), transition TEXT NOT NULL, PRIMARY KEY(old_row_id,new_row_id)',
    'comparison_row_meaning': 'row_id TEXT PRIMARY KEY REFERENCES comparison_row(id), definition TEXT NOT NULL, conditions TEXT NOT NULL, refs TEXT NOT NULL',
}
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


def readable_bytes(content, kind, legacy=True):
    decoded = (content.decode('utf-8', errors='replace') if legacy else decode_html(content)) if kind == 'html' else 'PDF dosyasını özgün kopyadan açın.'
    return ('<!doctype html><meta charset="utf-8"><title>Arşiv kopyası</title><pre>' + html.escape(decoded) + '</pre>').encode('utf-8')


def html_source_text(content):
    try: return decode_html(content)
    except ValueError: return content.decode('utf-8',errors='replace') # Existing historical captures only.


def check_identity(db, values):
    party = db.execute('SELECT * FROM party WHERE id=?', (values['entity_id'],)).fetchone()
    source = db.execute('SELECT d.party_id,d.source_kind,v.final_url,v.original_path FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (values['passage_id'],)).fetchone()
    if not party or party['registry_key'] != values['registry_key'] or values['entity_kind'] != 'party' or not source or source['party_id'] != party['id'] or source['source_kind'] != 'registry':
        raise ValueError('Kimlik ve sicil kaynağı partiyle uyuşmuyor')
    url = urllib.parse.urlsplit(source['final_url'])
    match = re.fullmatch(r'/sipar/(\d+)', url.path)
    if url.scheme != 'https' or url.hostname not in ('yargitaycb.gov.tr','www.yargitaycb.gov.tr') or not match:
        raise ValueError('Kimlik için resmi sicil sayfası gerekli')
    registry_key = 'yargitay-' + match.group(1)
    if party['registry_key'] != registry_key: raise ValueError('Sicil anahtarı kaynak adresiyle uyuşmuyor')
    content = html_source_text(safe_path(DATA, source['original_path']).read_bytes())
    if party['legal_name'].casefold() not in content.casefold(): raise ValueError('Parti adı sicil kaynağında yok')
    dates = []
    for key in ('valid_from','valid_to'):
        if values.get(key):
            date = dt.date.fromisoformat(values[key]); dates.append(date)
            if date.strftime('%d.%m.%Y') not in content and date.isoformat() not in content: raise ValueError('Kimlik tarihi sicil kaynağında yok')
    if values.get('valid_from') and values.get('valid_to') and dates[1] < dates[0]: raise ValueError('Kimlik dönemi geçersiz')


def pdf_libraries():
    return _load_pdf_libraries(ctypes.util.find_library)


@lru_cache(maxsize=4)
def _load_pdf_libraries(find_library):
    libraries = []
    for name in ('poppler-glib', 'gobject-2.0', 'glib-2.0'):
        try:
            path = find_library(name)
            if not path: raise OSError('bulunamadı')
            libraries.append(ctypes.CDLL(path))
        except OSError as exc:
            raise ValueError('PDF doğrulaması için Poppler-glib, GObject ve GLib paylaşımlı kütüphaneleri ve bağımlılıkları (Cairo dahil) gerekli; eksik: ' + name) from exc
    pop, obj, glib = libraries
    pop.poppler_document_new_from_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_void_p]
    pop.poppler_document_new_from_file.restype = ctypes.c_void_p
    pop.poppler_document_get_page.argtypes = [ctypes.c_void_p, ctypes.c_int]
    pop.poppler_document_get_page.restype = ctypes.c_void_p
    pop.poppler_document_get_n_pages.argtypes = [ctypes.c_void_p]
    pop.poppler_document_get_n_pages.restype = ctypes.c_int
    pop.poppler_page_get_text.argtypes = [ctypes.c_void_p]
    pop.poppler_page_get_text.restype = ctypes.c_void_p
    obj.g_object_unref.argtypes = [ctypes.c_void_p]
    glib.g_free.argtypes = [ctypes.c_void_p]
    return libraries


def pdf_page_text(path, index):
    pdf_libraries()
    try:
        path = Path(path).resolve()
        digest = sha(path)
    except OSError as exc:
        raise ValueError('PDF açılamadı') from exc
    return _pdf_page_text(path, digest, index)


@lru_cache(maxsize=256)
def _pdf_page_text(path, digest, index):
    pop, obj, glib = pdf_libraries()
    document = pop.poppler_document_new_from_file(path.as_uri().encode(), None, None)
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
    pop, obj, _ = pdf_libraries()
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
        charset = response.headers.get_content_charset()
    if len(content) > MAX_SOURCE:
        raise ValueError('Kaynak boyut sınırını aşıyor')
    if not content or (kind == 'pdf' and not content.startswith(b'%PDF-')):
        raise ValueError('Kaynak boş veya beklenen türde değil')
    if kind == 'html' and charset:
        try:
            standalone=decode_html(content)
            declared=decode_html(content,charset)
        except ValueError as exc:
            raise ValueError('HTTP charset tek başına kalıcı kaydedilemez; HTML meta/BOM kodlaması gerekli') from exc
        if standalone != declared:
            raise ValueError('HTTP charset tek başına kalıcı kaydedilemez; HTML meta/BOM kodlaması gerekli')
    elif kind == 'html':
        decode_html(content)
    digest = hashlib.sha256(content).hexdigest()
    object_root = Path(out) if out else DATA / 'objects'
    folder = object_root / digest
    folder.mkdir(parents=True, exist_ok=True)
    original = folder / ('original.html.bin' if kind == 'html' else 'original.pdf')
    if original.exists() and sha(original) != digest:
        raise ValueError('Mevcut arşiv nesnesi bozuk')
    readable = folder / 'readable.html'
    derivative = readable_bytes(content, kind, legacy=False)
    if readable.exists() and readable.read_bytes() not in (derivative,readable_bytes(content,kind)):
        raise ValueError('Mevcut okunabilir arşiv bozuk')
    if not original.exists(): original.write_bytes(content)
    if not readable.exists(): readable.write_bytes(derivative)
    now = dt.datetime.now(dt.timezone.utc).isoformat()
    result = dict(original_url=url, final_url=final, accessed_at=now, verified_at=now, mime=mime, sha256=digest, original_path=str(original.relative_to(DATA)) if original.is_relative_to(DATA) else str(original), readable_path=str(readable.relative_to(DATA)) if readable.is_relative_to(DATA) else str(readable))
    if charset: result['http_charset'] = charset
    return result


def connect(path):
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA journal_mode=DELETE')
    return db


def connect_readonly(path):
    db = sqlite3.connect(Path(path).resolve().as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    db.execute('PRAGMA foreign_keys=ON')
    return db


def current():
    path = DATA / 'current.json'
    return json.loads(path.read_text(encoding='utf-8'))['release_id'] if path.exists() else None


def migrate_comparisons(db, backup_path, fail_at=None):
    """Add comparison tables atomically without changing existing rows."""
    backup = sqlite3.connect(backup_path)
    try:
        db.backup(backup)
    finally:
        backup.close()
    try:
        db.execute('BEGIN IMMEDIATE')
        columns = {r['name'] for r in db.execute('PRAGMA table_info(topic_basis)')}
        if columns and 'source_role' not in columns:
            db.execute('ALTER TABLE topic_basis ADD COLUMN source_role TEXT')
        db.execute(f'CREATE TABLE IF NOT EXISTS comparison_source_inventory ({COMPARISON_INVENTORY_TABLE})')
        db.execute(f'CREATE TABLE IF NOT EXISTS comparison_completion ({COMPLETION_TABLE})')
        for name, definition in COMPLETION_V2_TABLES.items():
            db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        for name, definition in COMPARISON_TABLES.items():
            db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        if fail_at == 'migration':
            raise RuntimeError('Enjekte edilen comparison migration hatası')
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Karşılaştırma migration bütünlük hatası')
        db.commit()
    except Exception:
        db.rollback()
        raise


def comparison_inventory_records(inventory, taxonomy_version):
    if not isinstance(inventory, dict) or inventory.get('status') != 'complete' or inventory.get('taxonomy_version') != taxonomy_version or not isinstance(inventory.get('sections'), list) or not inventory['sections']:
        raise ValueError('Tam karşılaştırma için tamamlanmış kaynak envanteri gerekli')
    required = {'party_id','version_id','source_role','section','page_range','full_text_available','scanned_at','topic_ids','unmatched_headings','search_boundary','missing_id'}
    records = []
    for section in inventory['sections']:
        if not isinstance(section, dict) or set(section) != required or type(section['full_text_available']) is not bool or not isinstance(section['topic_ids'], list) or not isinstance(section['unmatched_headings'], list) or section['unmatched_headings']:
            raise ValueError('Envanter bölümünde eksik veya eşleşmemiş başlık var')
        canonical = json.dumps(section, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        identity = f'{taxonomy_version}:{canonical}'
        values = dict(section, taxonomy_version=taxonomy_version, id='inventory-' + hashlib.sha256(identity.encode('utf-8')).hexdigest())
        records.append(dict(kind='comparison_source_inventory', values=values))
    return records


def load_comparison(work, payload, inventory=None, *, reconciled=False):
    if not isinstance(payload, dict) or type(payload.get('contract_version')) is not int or payload['contract_version'] not in (1, 2, 3) or payload.get('stage') not in ('tracer','partial','complete') or type(payload.get('taxonomy_version')) is not int or payload['taxonomy_version'] < 1 or not isinstance(payload.get('records'), list):
        raise ValueError('Karşılaştırma paketi geçersiz')
    if inventory is not None:
        if payload['stage'] != 'complete': raise ValueError('Kaynak envanteri yalnız tam karşılaştırmaya eklenebilir')
        payload = dict(payload, records=payload['records'] + comparison_inventory_records(inventory, payload['taxonomy_version']))
    work = Path(work)
    assert_lock(work)
    protected = {'party','scope_party','scope_observation','method','party_identity_revision','source_policy'}
    allowed = (set(COMPARISON_TABLES) - {'comparison_contract'}) | (set(TABLES) - protected) | {'comparison_source_inventory', 'comparison_completion'} | set(LINEAGE_TABLES) | set(COMPLETION_V2_TABLES)
    with tempfile.TemporaryDirectory(dir=work) as temp:
        temp = Path(temp)
        shutil.copyfile(work / 'records.sqlite3', temp / 'records.sqlite3')
        shutil.copyfile(work / 'workspace.json', temp / 'workspace.json')
        db = connect(temp / 'records.sqlite3')
        try:
            migrate_comparisons(db, work / 'pre-comparison-migration.sqlite3')
            prior_revision = db.execute('SELECT * FROM comparison_completion_revision ORDER BY epoch DESC LIMIT 1').fetchone()
            incoming_revisions = [e['values'] for e in payload['records'] if isinstance(e, dict) and e.get('kind') == 'comparison_completion_revision' and isinstance(e.get('values'), dict)]
            next_epoch = prior_revision['epoch'] + 1 if prior_revision else 1
            parent = prior_revision['id'] if prior_revision else None
            chain = sorted((r for r in incoming_revisions if type(r.get('epoch')) is int and r['epoch'] >= next_epoch), key=lambda r: r['epoch'])
            forward_revision = bool(chain)
            for revision in chain:
                if revision['epoch'] != next_epoch or revision.get('parent_revision_id') != parent:
                    forward_revision = False
                    break
                next_epoch, parent = next_epoch + 1, revision.get('id')
            forward_revision = bool(forward_revision and chain[-1].get('stage') == payload['stage'] and
                                    chain[-1].get('taxonomy_version') == payload['taxonomy_version'])
            with db:
                if payload['contract_version'] == 3:
                    for name, definition in LINEAGE_TABLES.items():
                        db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
                contract = db.execute('SELECT * FROM comparison_contract').fetchone()
                historical_package = False
                if contract:
                    if contract['version'] not in (1, 2, 3): raise ValueError('Bilinmeyen karşılaştırma sözleşmesi')
                    if payload['taxonomy_version'] >= 3 and payload['taxonomy_version'] > contract['taxonomy_version'] and not reconciled:
                        raise ValueError('Yeni sözlük açık karşılaştırma eşlemesi gerektirir')
                    stages = {'tracer':0,'partial':1,'complete':2}
                    historical_package = payload['taxonomy_version'] < contract['taxonomy_version'] or (stages[payload['stage']] < stages[contract['stage']] and not forward_revision)
                    if not historical_package:
                        if payload['contract_version'] < contract['version'] or (payload['contract_version'] >= 2 and payload['taxonomy_version'] < 3):
                            raise ValueError('Karşılaştırma sözleşmesi geriletilemez veya eski sözlüğe uygulanamaz')
                        db.execute('UPDATE comparison_contract SET version=?,taxonomy_version=?,stage=? WHERE version=?', (payload['contract_version'],payload['taxonomy_version'],payload['stage'],contract['version']))
                else:
                    if payload['contract_version'] != 1: raise ValueError('Sentez sözleşmesi önceki sürüm gerektirir')
                    db.execute('INSERT INTO comparison_contract VALUES (?,?,?)', (1,payload['taxonomy_version'],payload['stage']))
                for entry in payload['records']:
                    if not isinstance(entry, dict) or set(entry) != {'kind','values'} or entry['kind'] not in allowed or not isinstance(entry['values'],dict) or not entry['values']:
                        raise ValueError('Karşılaştırma paket kaydı geçersiz')
                    kind, values = entry['kind'], entry['values']
                    if kind in LINEAGE_TABLES and payload['contract_version'] != 3:
                        raise ValueError('Satır soyu sürüm 3 sözleşmesi gerektirir')
                    if kind == 'comparison_source_inventory':
                        values = dict(values)
                        for key in ('topic_ids', 'unmatched_headings'):
                            if isinstance(values.get(key), list):
                                values[key] = json.dumps(values[key], ensure_ascii=False)
                    info = db.execute(f'PRAGMA table_info({kind})').fetchall()
                    columns = {r['name'] for r in info}
                    if not set(values) <= columns: raise ValueError('Bilinmeyen kayıt alanı')
                    pks = [r['name'] for r in sorted(info,key=lambda r:r['pk']) if r['pk']]
                    if not pks or not all(k in values for k in pks): raise ValueError('Kayıt anahtarı eksik')
                    existing = db.execute(f"SELECT * FROM {kind} WHERE " + ' AND '.join(k+'=?' for k in pks), [values[k] for k in pks]).fetchone()
                    if existing:
                        conflicts = [k for k in columns if existing[k] != values.get(k)]
                        if conflicts and kind == 'comparison_row' and not historical_package and existing['state'] == 'not_researched' and values.get('state') in ('evidence','no_explicit_statement','document_missing') and all(existing[k] == values.get(k) for k in ('id','topic_id','taxonomy_version','party_id','level','organ')):
                            keys = [k for k in values if k not in pks]
                            db.execute(f"UPDATE {kind} SET " + ','.join(k+'=?' for k in keys) + ' WHERE ' + ' AND '.join(k+'=?' for k in pks), [values[k] for k in keys] + [values[k] for k in pks])
                            conflicts = []
                        if conflicts: raise ValueError('Aynı kimlikle çelişen kayıt')
                        continue
                    if historical_package: raise ValueError('Eski paket mevcut sürüme yeni kayıt ekleyemez')
                    if kind in COMPARISON_TABLES or kind in LINEAGE_TABLES or kind in COMPLETION_V2_TABLES or kind in ('comparison_source_inventory', 'comparison_completion'):
                        keys = list(values)
                        db.execute(f"INSERT INTO {kind} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", [values[k] for k in keys])
                    else:
                        # Existing record kinds retain their ordinary checks. The
                        # whole scratch database is installed only after export.
                        db.commit()
                        record(temp, kind, values)
            if not prior_revision and incoming_revisions:
                first = db.execute('SELECT * FROM comparison_completion_revision ORDER BY epoch LIMIT 1').fetchone()
                head = db.execute('SELECT * FROM comparison_completion_basis WHERE id=?', (first['basis_id'],)).fetchone()
                cells = [dict(row) for row in db.execute('SELECT * FROM comparison_coverage_disposition WHERE basis_id=?', (first['basis_id'],))]
                source, risk = decode_completion_basis(dict(head), cells)
                verify_initial_completion_basis(source, risk)
                metadata = json.loads((temp / 'workspace.json').read_text(encoding='utf-8'))
                has_legacy_marker = db.execute('SELECT 1 FROM comparison_completion LIMIT 1').fetchone()
                if has_legacy_marker:
                    try:
                        anchor = json.loads(first['legacy_anchor'])
                    except (TypeError, ValueError) as exc:
                        raise ValueError('Önceki kaynak kapanışı çapası eksik') from exc
                    if anchor.get('release_id') != metadata.get('base'):
                        raise ValueError('Önceki kaynak kapanışı gerçek tabanla uyuşmuyor')
                elif first['legacy_anchor'] is not None:
                    raise ValueError('Var olmayan önceki kaynak kapanışı çapası reddedildi')
            if incoming_revisions:
                origin = prior_revision or db.execute('SELECT * FROM comparison_completion_revision ORDER BY epoch LIMIT 1').fetchone()
                previous_basis_id = origin['basis_id']
                previous_head = dict(db.execute('SELECT * FROM comparison_completion_basis WHERE id=?', (previous_basis_id,)).fetchone())
                previous_cells = [dict(row) for row in db.execute('SELECT * FROM comparison_coverage_disposition WHERE basis_id=?', (previous_basis_id,))]
                previous_basis, _ = decode_completion_basis(previous_head, previous_cells)
                for successor in db.execute('SELECT * FROM comparison_completion_revision WHERE epoch>? ORDER BY epoch', (origin['epoch'],)):
                    if successor['basis_id'] == previous_basis_id:
                        continue
                    next_head = dict(db.execute('SELECT * FROM comparison_completion_basis WHERE id=?', (successor['basis_id'],)).fetchone())
                    next_cells = [dict(row) for row in db.execute('SELECT * FROM comparison_coverage_disposition WHERE basis_id=?', (successor['basis_id'],))]
                    next_basis, _ = decode_completion_basis(next_head, next_cells)
                    verify_successor_completion_basis(previous_basis, next_basis)
                    previous_basis_id, previous_basis = successor['basis_id'], next_basis
            if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Karşılaştırma bütünlük hatası')
            if incoming_revisions:
                # Reject invalid candidate closure before performing expensive
                # source-byte and publication checks; the final export still
                # performs all of those checks before installing the workspace.
                available = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
                names = (set(TABLES) | set(COMPARISON_TABLES) | set(COMPLETION_V2_TABLES) |
                         set(LINEAGE_TABLES) | {'comparison_source_inventory', 'comparison_completion'}) & available
                candidate = {name: [dict(row) for row in db.execute(f'SELECT * FROM {name} ORDER BY rowid')] for name in names}
                validate_completion(candidate)
        finally:
            db.close()
        export_db(temp / 'records.sqlite3', 'workspace', strict_identity=True)
        os.replace(temp / 'records.sqlite3', work / 'records.sqlite3')


def comparison_reconcile(work, taxonomy, inventory, backfill):
    """Apply explicitly reviewed row lineage and backfill in one workspace swap."""
    work = Path(work)
    assert_lock(work)
    if not all(isinstance(x, dict) for x in (taxonomy, inventory, backfill)):
        raise ValueError('Karşılaştırma eşleme paketleri geçersiz')
    version = taxonomy.get('taxonomy_version')
    if type(version) is not int or backfill.get('taxonomy_version') != version:
        raise ValueError('Eşleme ve geri tarama sözlüğü uyuşmuyor')
    taxonomy_records = taxonomy.get('records')
    backfill_records = backfill.get('records')
    mappings = taxonomy.get('row_mappings')
    superseded = taxonomy.get('superseded_rows', [])
    if not all(isinstance(x, list) for x in (taxonomy_records, backfill_records, mappings, superseded)):
        raise ValueError('Açık eşleme ve kayıt listeleri gerekli')
    db = connect_readonly(work / 'records.sqlite3')
    try:
        contract = db.execute('SELECT * FROM comparison_contract').fetchone()
        if not contract or version != contract['taxonomy_version'] + 1:
            raise ValueError('Yeni sözlük önceki sürümden bir sonraki sürüm olmalı')
        old_version = contract['taxonomy_version']
        parties = {r['party_id'] for r in db.execute('SELECT party_id FROM scope_party')}
        old_topics = {r['topic_id']: dict(r) for r in db.execute('SELECT * FROM comparison_topic WHERE taxonomy_version=?', (old_version,))}
        old_rows = {r['id']: dict(r) for r in db.execute('SELECT * FROM comparison_row WHERE taxonomy_version=?', (old_version,))}
        cross_topic = {m.get('new_row_id') for m in mappings if isinstance(m, dict) and m.get('old_row_id') in old_rows and m.get('topic_id') != old_rows[m['old_row_id']]['topic_id']}
        if (old_version >= 3 or cross_topic) and backfill.get('contract_version') != 3:
            raise ValueError('Yeni sözlük için sürüm 3 satır soyu sözleşmesi gerekli')
        topic_entries = [e['values'] for e in taxonomy_records if e.get('kind') == 'comparison_topic']
        new_topics = {entry['topic_id']: entry for entry in topic_entries}
        if not new_topics or any(t.get('taxonomy_version') != version for t in new_topics.values()):
            raise ValueError('Yeni sürümün tam konu sözlüğü gerekli')
        if len(new_topics) != len(topic_entries):
            raise ValueError('Yeni sözlükte yinelenen konu olamaz')
        direct_rows = [e['values'] for e in backfill_records if e.get('kind') == 'comparison_row']
        # Check reviewed coverage before constructing or writing any candidate.
        compare_keys = ('domain', 'parent_topic_id', 'definition', 'applicable_levels', 'basis_kind')
        changed = {tid for tid, topic in new_topics.items() if tid not in old_topics or any(topic.get(k) != old_topics[tid].get(k) for k in compare_keys)}
        affected_topics = changed | {m.get('topic_id') for m in mappings if isinstance(m, dict) and m.get('new_row_id') in cross_topic}
        covered = {tid: set() for tid in affected_topics}
        for row in direct_rows:
            if row.get('topic_id') in covered and row.get('state') in ('evidence', 'no_explicit_statement', 'document_missing'):
                covered[row['topic_id']].add(row.get('party_id'))
        for mapping in mappings:
            source = old_rows.get(mapping.get('old_row_id')) if isinstance(mapping, dict) else None
            if source and mapping.get('topic_id') in covered and source['state'] != 'not_researched':
                covered[mapping['topic_id']].add(source['party_id'])
        if len(parties) != 9 or any(found != parties for found in covered.values()):
            raise ValueError('Yeni veya değişen her konu için incelenmiş dokuz parti gerekli')
        if not changed or not set(old_topics) <= set(new_topics):
            raise ValueError('Sürüm değişikliği gerçek konu değişikliği ve tam eski konu eşlemesi gerektirir')
        records = list(taxonomy_records)
        if backfill.get('contract_version') == 3 and contract['version'] < 3:
            records.append({'kind': 'comparison_lineage_contract', 'values': {'version': 1, 'first_taxonomy_version': version}})
        used = set()
        for mapping in mappings:
            if not isinstance(mapping, dict) or set(mapping) != {'old_row_id','new_row_id','topic_id','reason','fields','changes'} or not mapping['reason']:
                raise ValueError('Açık kaynaklı satır eşlemesi gerekli')
            source = old_rows.get(mapping['old_row_id'])
            if not source or source['id'] in used or source['state'] == 'not_researched' or mapping['topic_id'] not in new_topics:
                raise ValueError('Eski satır eşlemesi geçersiz')
            used.add(source['id'])
            if backfill.get('contract_version') == 3:
                records.append({'kind': 'comparison_row_lineage', 'values': {'old_row_id': source['id'], 'new_row_id': mapping['new_row_id'], 'transition': 'mapped'}})
            row = dict(source, id=mapping['new_row_id'], topic_id=mapping['topic_id'], taxonomy_version=version,
                       selection_reason=source['selection_reason'] + ' Eşleme: ' + mapping['reason'] + ' [' + source['id'] + ']')
            records.append({'kind': 'comparison_row', 'values': row})
            for table, key in (('comparison_field','fields'), ('comparison_change','changes')):
                originals = {r['id']: dict(r) for r in db.execute(f'SELECT * FROM {table} WHERE row_id=?', (source['id'],))}
                replacements = mapping[key]
                if not isinstance(replacements, list) or any(not isinstance(x, dict) or set(x) != {'old_id','new_id'} for x in replacements) or {x['old_id'] for x in replacements} != set(originals) or len(replacements) != len(originals):
                    raise ValueError('Satırın bütün alan ve değişiklik eşlemeleri gerekli')
                for item in replacements:
                    value = dict(originals[item['old_id']], id=item['new_id'], row_id=row['id'])
                    records.append({'kind': table, 'values': value})
        direct_by_id = {r.get('id'): r for r in direct_rows}
        for item in superseded:
            if not isinstance(item, dict) or set(item) != {'old_row_id','replacement_ids','reason'} or not item['reason'] or not isinstance(item['replacement_ids'], list) or not item['replacement_ids']:
                raise ValueError('Yerine geçen satır ve gerekçe gerekli')
            source = old_rows.get(item['old_row_id'])
            if not source or source['id'] in used or any(rid not in direct_by_id or direct_by_id[rid].get('party_id') != source['party_id'] for rid in item['replacement_ids']):
                raise ValueError('Geçersiz satır değişimi')
            used.add(source['id'])
            if backfill.get('contract_version') == 3:
                for rid in item['replacement_ids']:
                    records.append({'kind': 'comparison_row_lineage', 'values': {'old_row_id': source['id'], 'new_row_id': rid, 'transition': 'superseded'}})
        if used != set(old_rows):
            raise ValueError('Bütün seçili eski satırların açık lineage eşlemesi gerekli')
        # A count is not a research review. Changed topics require an explicit
        # author-supplied decision for each selected row and references to that
        # row's actual passage, scoped absence, or missing-document record.
        candidate_records = records + backfill_records
        superseding = {rid for item in superseded for rid in item['replacement_ids']} if backfill.get('contract_version') == 3 else set()
        changed_rows = {e['values']['id']: e['values'] for e in candidate_records if e.get('kind') == 'comparison_row' and (e['values'].get('topic_id') in changed or e['values']['id'] in cross_topic or e['values']['id'] in superseding)}
        reviews = {(e['values'].get('subject_kind'), e['values'].get('subject_id')): e['values'] for e in backfill_records if e.get('kind') == 'comparison_semantic_review'}
        links = backfill.get('row_reviews')
        if not isinstance(links, list): raise ValueError('Yeni anlam incelemesi ve kaynak ilişkileri gerekli')
        by_row = {item.get('row_id'): item for item in links if isinstance(item, dict)}
        if len(by_row) != len(links) or set(by_row) != set(changed_rows):
            raise ValueError('Her değişen satır için yeni anlam incelemesi gerekli')
        candidate_fields = [e['values'] for e in candidate_records if e.get('kind') == 'comparison_field']
        extra_evidence = [e['values'] for e in candidate_records if e.get('kind') == 'finding_evidence']
        for rid, row in changed_rows.items():
            link = by_row[rid]
            review = reviews.get(('comparison_row', rid))
            if set(link) != {'row_id','topic_id','party_id','definition','conditions','refs'} or link['topic_id'] != row['topic_id'] or link['party_id'] != row['party_id'] or link['definition'] != new_topics[row['topic_id']]['definition'] or not isinstance(link['conditions'], str) or not link['conditions'].strip():
                raise ValueError('Satır anlam incelemesi konu, parti ve koşullarla uyuşmalı')
            if not review or review.get('reviewer_kind') != 'agent' or review.get('result') != 'reviewed' or not isinstance(review.get('reason'), str) or not review['reason'].strip() or not review.get('reviewed_at'):
                raise ValueError('Her değişen satır için yeni anlam incelemesi gerekli')
            try:
                reviewed_at = dt.datetime.fromisoformat(review['reviewed_at'].replace('Z', '+00:00'))
            except (TypeError, ValueError, AttributeError):
                raise ValueError('Anlam incelemesi geçerli zaman gerektirir')
            if reviewed_at.tzinfo is None:
                raise ValueError('Anlam incelemesi zaman dilimi gerektirir')
            if row['state'] == 'evidence':
                fids = {f[k] for f in candidate_fields if f['row_id'] == rid for k in ('summary_finding_id','quote_finding_id')}
                refs = {e['passage_id'] for e in extra_evidence if e.get('finding_id') in fids}
                for fid in fids:
                    refs.update(r['passage_id'] for r in db.execute('SELECT passage_id FROM finding_evidence WHERE finding_id=?', (fid,)))
            elif row['state'] == 'no_explicit_statement': refs = {row.get('scope_id')}
            elif row['state'] == 'document_missing': refs = {row.get('missing_id')}
            else: refs = set()
            refs.discard(None)
            if not isinstance(link['refs'], list) or not link['refs'] or set(link['refs']) != refs:
                raise ValueError('Satır anlam incelemesi gerçek kanıt veya kapsamla uyuşmalı')
            if link['definition'] not in review['reason'] or link['conditions'] not in review['reason'] or any(ref not in review['reason'] for ref in refs):
                raise ValueError('Anlam incelemesi tanım, koşul ve tüm kaynak ilişkilerini açıklamalı')
            if backfill.get('contract_version') == 3:
                records.append({'kind': 'comparison_row_meaning', 'values': {'row_id': rid, 'definition': link['definition'], 'conditions': link['conditions'], 'refs': json.dumps(sorted(refs), ensure_ascii=False)}})
    finally:
        db.close()
    records.extend(comparison_inventory_records(inventory, version))
    records.extend(backfill_records)
    records = [r for r in records if r['kind'] not in LINEAGE_TABLES] + [r for r in records if r['kind'] in LINEAGE_TABLES]
    payload = dict(backfill, records=records)
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        candidate = Path(tmp)
        shutil.copyfile(work / 'records.sqlite3', candidate / 'records.sqlite3')
        shutil.copyfile(work / 'workspace.json', candidate / 'workspace.json')
        load_comparison(candidate, payload, reconciled=True)
        os.replace(candidate / 'records.sqlite3', work / 'records.sqlite3')


def check_comparison_input(path, inventory_path=None):
    payload = json.loads(Path(path).read_text(encoding='utf-8'))
    inventory = json.loads(Path(inventory_path).read_text(encoding='utf-8')) if inventory_path else None
    with tempfile.TemporaryDirectory() as temp:
        work = open_workspace(temp)
        try:
            load_comparison(work, payload, inventory)
        finally:
            try: assert_lock(work)
            except (ValueError,OSError): pass
            else: (DATA / '.write.lock').unlink()
    return True


def validate_synthesis_v2(data, synthesis):
    """Validate an author's explicit claim sides without inferring source meaning."""
    matching = [r for r in data.get('comparison_semantic_review', [])
                if r.get('subject_kind') == 'comparison_synthesis'
                and r.get('subject_id') == synthesis['id'] and r.get('reviewer_kind') == 'agent']
    if len(matching) != 1 or matching[0].get('result') != 'reviewed':
        raise ValueError('Sentez için yazarın ayrı anlam incelemesi gerekli')
    review = matching[0]
    try:
        reviewed_at = dt.datetime.fromisoformat(review['reviewed_at'].replace('Z', '+00:00'))
        decision = json.loads(review['reason'])
    except (KeyError, ValueError, TypeError, AttributeError):
        raise ValueError('Sentez incelemesi sürümlü ve zamanlı olmalı')
    if reviewed_at.tzinfo is None or not isinstance(decision, dict) or set(decision) != {'contract_version','claim_type','explanation','sides'} or decision['contract_version'] != 2 or not isinstance(decision['explanation'], str) or not decision['explanation'].strip() or not isinstance(decision['sides'], list) or not decision['sides']:
        raise ValueError('Sentez iddiası ve gerekçeli tarafları gerekli')
    rows = {r['id']: r for r in data['comparison_row']}
    scopes = {r['id']: r for r in data.get('comparison_review_scope', [])}
    missing = {r['id']: r for r in data.get('missing', [])}
    attempts = {r['id']: r for r in data.get('attempt', [])}
    passages = {r['id']: r for r in data['passage']}
    claimed, positive_parties, seen = set(), set(), set()
    for side in decision['sides']:
        if not isinstance(side, dict) or set(side) != {'party_id','row_id','support','refs'} or not isinstance(side['refs'], list) or not side['refs'] or any(not isinstance(ref, str) or not ref for ref in side['refs']) or len(side['refs']) != len(set(side['refs'])):
            raise ValueError('Sentez tarafı ve dayanakları geçersiz')
        row = rows.get(side['row_id'])
        if not row or row['party_id'] != side['party_id'] or (row['topic_id'], row['taxonomy_version']) != (synthesis['topic_id'], synthesis['taxonomy_version']) or row['id'] in seen:
            raise ValueError('Sentez tarafı konu ve partiyle uyuşmalı')
        seen.add(row['id'])
        refs = set(side['refs'])
        if side['support'] == 'passage' and row['state'] == 'evidence':
            fids = {f[k] for f in data['comparison_field'] if f['row_id'] == row['id'] for k in ('summary_finding_id','quote_finding_id')}
            available = {e['passage_id'] for e in data['finding_evidence'] if e['finding_id'] in fids}
            if not refs <= available or any(p not in passages or passages[p]['version_id'] != row['version_id'] for p in refs):
                raise ValueError('Olumlu tarafın kendi konu pasajı gerekli')
            positive_parties.add(row['party_id'])
            claimed.update(refs)
        elif side['support'] == 'scope' and row['state'] == 'no_explicit_statement':
            scope = scopes.get(row['scope_id'])
            if refs != {row['scope_id']} or not scope or scope['party_id'] != row['party_id'] or scope['version_id'] != row['version_id'] or scope.get('result') != 'no_explicit_statement' or not all(scope.get(k) for k in ('sections','query_terms','reviewed_at','reason')):
                raise ValueError('Yokluk gerçek incelenmiş kapsam gerektirir')
            try:
                scope_time = dt.datetime.fromisoformat(scope['reviewed_at'].replace('Z', '+00:00'))
            except (ValueError, TypeError, AttributeError):
                raise ValueError('Kapsam incelemesi geçerli zaman gerektirir')
            if scope_time.tzinfo is None: raise ValueError('Kapsam incelemesi zaman dilimi gerektirir')
        elif side['support'] == 'missing' and row['state'] == 'document_missing':
            m = missing.get(row['missing_id'])
            attempt = attempts.get(m['attempt_id']) if m else None
            allowed = {'Bulunamadı':('search','no_result'), 'Erişilemedi':('access','failure'), 'Doğrulanamadı':('verification','inconclusive')}
            if not m or not attempt or refs != {m['id'], attempt['id']} or m['party_id'] != row['party_id'] or not m.get('reason') or any(attempt[k] != m[k] for k in ('party_id','heading','topic_id')) or allowed.get(m['status']) != (attempt['type'],attempt['result']):
                raise ValueError('Belge açığı gerçek eksik ve girişim gerektirir')
            if m['heading'] != {'program':'Program', 'charter':'Tüzük'}.get(row.get('source_role')):
                raise ValueError('Belge açığı aynı türde kaynak aramasına bağlanmalı')
        else:
            raise ValueError('İncelenmemiş veya uyumsuz durum sentez dayanağı olamaz')
    kind = decision['claim_type']
    if not ((kind == 'multi_positive' and len(positive_parties) >= 2) or
            (kind == 'one_positive' and len(positive_parties) == 1 and any(s['support'] != 'passage' and s['party_id'] not in positive_parties for s in decision['sides'])) or
            (kind == 'status_only' and not positive_parties)):
        raise ValueError('İddia türü dayanaklı olumlu taraflarla uyuşmuyor')
    linked = {e['passage_id'] for e in data['comparison_synthesis_evidence'] if e['synthesis_id'] == synthesis['id']}
    if linked != claimed:
        raise ValueError('Sentez pasaj ilişkileri iddiadaki olumlu taraflarla uyuşmalı')
    return True


def validate_source_basis_cells(data, taxonomy_version, cells, assertions):
    """Match authored source contexts to selected records, including their evidence.

    This checks individual cells only. The revision contract must additionally
    establish the completeness and immutability of the independent universe.
    """
    rows = {r['id']: r for r in data['comparison_row'] if r['taxonomy_version'] == taxonomy_version}
    scopes = {s['id']: s for s in data.get('comparison_review_scope', [])}
    fields = {}
    for field in data.get('comparison_field', []):
        fields.setdefault(field['row_id'], []).append(field)
    evidence = {}
    for item in data.get('finding_evidence', []):
        evidence.setdefault(item['finding_id'], set()).add(item['passage_id'])
    missing = {m['id']: m for m in data.get('missing', [])}
    attempts = {a['id']: a for a in data.get('attempt', [])}
    dimensions = ('topic_id', 'party_id', 'source_role', 'version_id', 'level', 'organ')
    for cell in cells:
        key = cell['logical_key']
        original = cell['source_judgment_record']
        if (original.get('id') != key.get('context_judgment') or
                any(original.get(k) != key.get(k) for k in dimensions if k != 'topic_id') or
                original.get('state') != cell['disposition'] or not cell['basis_ids']):
            raise ValueError('Kaynak yükümlülüğü özgün karar ile uyuşmuyor')
        for field in cell['field_dispositions']:
            if field.get('disposition') == 'source_supported' and field.get('basis_id') not in cell['basis_ids']:
                raise ValueError('Kaynak yükümlülüğü alan dayanağı eksik')
        ident = key['context_judgment']
        for mapping in cell['mapping_records']:
            if mapping.get('old_row_id') != ident or not mapping.get('new_row_id') or not mapping.get('reason'):
                raise ValueError('Kaynak yükümlülüğü eşleme zinciri geçersiz')
            ident = mapping['new_row_id']
        row = rows.get(ident)
        if not row or any(row.get(k) != key.get(k) for k in dimensions) or row.get('state') != cell['disposition']:
            raise ValueError('Kaynak yükümlülüğü satır, düzey veya organ eksik')
        kinds = {assertions.get(bid, {}).get('kind') for bid in cell['basis_ids']}
        expected_kind = {'evidence': 'supported_field', 'no_explicit_statement': 'dated_source_scope',
                         'document_missing': 'documentary_gap'}.get(cell['disposition'])
        if not expected_kind or expected_kind not in kinds:
            raise ValueError('Kaynak yükümlülüğü durum dayanağı eksik')
        for bid in cell['basis_ids']:
            assertion = assertions.get(bid)
            if not isinstance(assertion, dict):
                raise ValueError('Kaynak yükümlülüğü dayanağı eksik')
            kind = assertion.get('kind')
            if kind == 'dated_source_scope':
                scope = assertion.get('scope') or {}
                if row.get('scope_id') != scope.get('id') or scopes.get(scope.get('id')) != scope or any(scope.get(k) != row.get(k) for k in ('party_id', 'version_id')):
                    raise ValueError('Kaynak yükümlülüğü araştırma kapsamı değişmiş')
            elif kind == 'documentary_gap':
                item, attempt = assertion.get('missing') or {}, assertion.get('attempt') or {}
                if row.get('missing_id') != item.get('id') or missing.get(item.get('id')) != item or attempts.get(attempt.get('id')) != attempt or item.get('attempt_id') != attempt.get('id') or item.get('party_id') != row['party_id']:
                    raise ValueError('Kaynak yükümlülüğü belge araması değişmiş')
            elif kind == 'supported_field':
                matches = [f for f in fields.get(ident, []) if all(f.get(k) == assertion.get(k) for k in ('field', 'condition_key', 'summary_finding_id', 'quote_finding_id'))]
                passage_ids = assertion.get('passage_ids', [])
                if not matches or not passage_ids or len(passage_ids) != len(set(passage_ids)) or not set(passage_ids) <= (evidence.get(assertion.get('summary_finding_id'), set()) | evidence.get(assertion.get('quote_finding_id'), set())):
                    raise ValueError('Kaynak yükümlülüğü alanı veya pasajı eksik')
                semantic = assertion.get('semantic_reviews', [])
                finding_reviews = assertion.get('finding_reviews', [])
                if not semantic and not finding_reviews:
                    raise ValueError('Kaynak yükümlülüğü anlam incelemesi eksik')
                for item in semantic + finding_reviews:
                    review = item.get('record') or {}
                    source = item.get('source') or {}
                    if review.get('reviewer_kind') != 'agent' or review.get('result') != 'reviewed' or not all(review.get(k) for k in ('reason', 'reviewed_at', 'subject_id')) or not source.get('path') or not source.get('pointer'):
                        raise ValueError('Kaynak yükümlülüğü anlam inceleme kökeni eksik')
                    try:
                        if dt.datetime.fromisoformat(review['reviewed_at'].replace('Z', '+00:00')).tzinfo is None:
                            raise ValueError('Zaman dilimi eksik')
                    except (TypeError, ValueError, AttributeError) as exc:
                        raise ValueError('Kaynak yükümlülüğü inceleme tarihi geçersiz') from exc
                if semantic:
                    mapped = set()
                    for item in semantic:
                        subject = item['record']['subject_id']
                        for mapping in cell['mapping_records']:
                            successor = next((f['new_id'] for f in mapping.get('fields', []) if f['old_id'] == subject), None)
                            if successor:
                                subject = successor
                        mapped.add(subject)
                    if not mapped.intersection(f['id'] for f in matches):
                        raise ValueError('Kaynak yükümlülüğü alan inceleme soyu uyuşmuyor')
                elif not {assertion['summary_finding_id'], assertion['quote_finding_id']} <= {r['record']['subject_id'] for r in finding_reviews}:
                    raise ValueError('Kaynak yükümlülüğü bulgu incelemeleri uyuşmuyor')
            else:
                raise ValueError('Kaynak yükümlülüğü dayanak türü geçersiz')
    return True


def validate_source_basis_universe(data, basis, superseded_cells=(), superseded_syntheses=()):
    """Validate a source-authored obligation universe against a candidate.

    Establishing the provenance and immutable adoption of the supplied basis
    remains the responsibility of the revision/import contract.
    """
    if basis.get('reviewer_kind') != 'agent' or basis.get('human_acceptance') is not False or basis.get('unresolved') != []:
        raise ValueError('Kaynak evreni çözümlenmemiş veya kökeni geçersiz')
    version = basis['taxonomy_version']
    topics = {t['topic_id']: t for t in basis['topics']}
    parties = {p['party_id'] for p in data['scope_party']}
    cells = {c['id']: c for c in basis['cells']}
    assertions = basis['source_assertions']
    if len(topics) != len(basis['topics']) or len(cells) != len(basis['cells']) or not topics or not parties:
        raise ValueError('Kaynak evreninde yinelenen veya eksik konu/hücre var')
    for bid, assertion in assertions.items():
        canonical = json.dumps(assertion, ensure_ascii=False, sort_keys=True, separators=(',', ':'))
        if bid != 'basis-' + hashlib.sha256(canonical.encode()).hexdigest()[:24]:
            raise ValueError('Kaynak evreninde dayanak kimliği uyuşmuyor')
    for cid, cell in cells.items():
        canonical = canonical_json(cell['logical_key'])
        if cid != 'cell-' + hashlib.sha256(canonical.encode()).hexdigest()[:24]:
            raise ValueError('Kaynak evreninde hücre kimliği uyuşmuyor')
    found = {}
    for item in basis['universe']:
        pair = (item['topic_id'], item['party_id'])
        if pair in found or not item.get('cell_ids') or len(set(item['cell_ids'])) != len(item['cell_ids']):
            raise ValueError('Kaynak evreninde parti-konu yükümlülüğü eksik')
        found[pair] = item['cell_ids']
        for cid in item['cell_ids']:
            cell = cells.get(cid)
            if not cell or (cell['logical_key']['topic_id'], cell['logical_key']['party_id']) != pair:
                raise ValueError('Kaynak evreninde parti-konu dayanağı uyuşmuyor')
    if set(found) != {(topic, party) for topic in topics for party in parties} or set(cells) != {cid for ids in found.values() for cid in ids}:
        raise ValueError('Kaynak evreni parti-konu kapsamını kapatmıyor')
    actual_topics = {t['topic_id']: t for t in data['comparison_topic'] if t['taxonomy_version'] == version}
    if topics != actual_topics:
        raise ValueError('Kaynak evrenindeki konu tanımları değişmiş')
    active_cells = [cell for cid, cell in cells.items() if cid not in superseded_cells]
    for pair, ids in found.items():
        if not any(cid not in superseded_cells for cid in ids):
            raise ValueError('Kaynak evreninde etkin parti-konu yükümlülüğü eksik')
    validate_source_basis_cells(data, version, active_cells, assertions)
    required_rows = {c['mapping_records'][-1]['new_row_id'] if c['mapping_records'] else c['logical_key']['context_judgment']
                     for c in active_cells}
    actual_rows = {r['id'] for r in data['comparison_row'] if r['taxonomy_version'] == version}
    if required_rows != actual_rows:
        raise ValueError('Kaynak evreni seçili satırları bağlamıyor')
    fields_by_row = {}
    for field in data['comparison_field']:
        if field['row_id'] in actual_rows:
            fields_by_row.setdefault(field['row_id'], []).append(field)
    required_fields = set()
    for cell in active_cells:
        row_id = cell['mapping_records'][-1]['new_row_id'] if cell['mapping_records'] else cell['logical_key']['context_judgment']
        for bid in cell['basis_ids']:
            assertion = assertions[bid]
            if assertion['kind'] != 'supported_field':
                continue
            matches = [f for f in fields_by_row.get(row_id, []) if all(f.get(k) == assertion.get(k) for k in ('field', 'condition_key', 'summary_finding_id', 'quote_finding_id'))]
            if len(matches) != 1:
                raise ValueError('Kaynak evreni alan yükümlülüğü tekil değil')
            required_fields.add(matches[0]['id'])
    if required_fields != {field['id'] for fields in fields_by_row.values() for field in fields}:
        raise ValueError('Kaynak evreni seçili alanları bağlamıyor')
    expected_inventory = comparison_inventory_records(dict(status='complete', taxonomy_version=version,
                                                          sections=basis['inventory_sections']), version)
    expected = {}
    for entry in expected_inventory:
        item = dict(entry['values'])
        for key in ('topic_ids', 'unmatched_headings'):
            item[key] = json.dumps(item[key], ensure_ascii=False)
        expected[item['id']] = item
    if len(expected) != len(expected_inventory):
        raise ValueError('Kaynak evreni envanter bölümleri yinelenmiş')
    actual = {i['id']: i for i in data['comparison_source_inventory'] if i['taxonomy_version'] == version}
    if expected != actual:
        raise ValueError('Kaynak evreni envanter bölümü eksik veya değişmiş')
    claims = {s['id']: s for s in data['comparison_synthesis'] if s['taxonomy_version'] == version}
    reviews = {r['subject_id']: r for r in data['comparison_semantic_review']
               if r['subject_kind'] == 'comparison_synthesis' and r['reviewer_kind'] == 'agent'}
    obligations = [o for o in basis['synthesis_obligations'] if o['id'] not in superseded_syntheses]
    if len({o['id'] for o in obligations}) != len(obligations) or set(claims) != {o['id'] for o in obligations}:
        raise ValueError('Kaynak evreni sentez yükümlülüğü eksik')
    for obligation in obligations:
        if claims[obligation['id']] != obligation['source_authored_claim'] or reviews.get(obligation['id']) != obligation['original_review']:
            raise ValueError('Kaynak evreni sentez kararı değişmiş')
    return True


def validate_registered_decision(item):
    try:
        origin, decision = item['origin'], item['decision']
        content = origin['content']
        if not origin['path'].startswith('data/') or hashlib.sha256(content.encode('utf-8')).hexdigest() != origin['sha256']:
            raise ValueError('Kayıt özeti uyuşmuyor')
        pointer = origin['pointer']
        if not pointer.startswith('/'):
            raise ValueError('Kayıt göstericisi geçersiz')
        value = json.loads(content)
        for token in pointer[1:].split('/'):
            token = token.replace('~1', '/').replace('~0', '~')
            value = value[int(token)] if isinstance(value, list) else value[token]
        if value != decision:
            raise ValueError('Kayıt içeriği uyuşmuyor')
        return decision
    except (TypeError, ValueError, KeyError, IndexError) as exc:
        raise ValueError('Yeni kaynak kararının özgün kaydı geçersiz') from exc


def registered_reading_fingerprints(registry):
    """Authenticate original readings and independently registered additions."""
    if not isinstance(registry, dict) or not isinstance(registry.get('initial'), list) or not isinstance(registry.get('additional'), list):
        raise ValueError('Kaynak okuması kayıt kataloğu eksik')
    digest = hashlib.sha256(canonical_json(registry['initial']).encode()).hexdigest()
    if digest != '94570eb54fd0c0a3e6f8f52a1afeb7941f1df7f8aa24ee81e9ff9d754bb16c95':
        raise ValueError('Özgün kaynak okuması kataloğu değişmiş')
    def fingerprint(decision):
        return canonical_json({key: value for key, value in decision.items() if key != 'id'})
    readings = {fingerprint(d) for d in registry['initial']}
    for item in registry['additional']:
        readings.add(fingerprint(validate_registered_decision(item)))
    return readings


def validate_basis_registry_origins(basis):
    """Bind retained registered decision bodies to the stored source catalog."""
    documents = {item['path']: item for item in basis['source_documents']}
    if len(documents) != len(basis['source_documents']):
        raise ValueError('Kaynak karar kataloğunda yinelenen belge var')
    registry = basis.get('_reading_registry')
    registered_reading_fingerprints(registry)
    corrections = basis.get('_correction_registry')
    if not isinstance(corrections, list):
        raise ValueError('Kaynak düzeltme kararları kataloğu eksik')
    for registration in registry['additional'] + corrections:
        validate_registered_decision(registration)
        origin = registration['origin']
        if origin['path'] not in documents or documents[origin['path']]['sha256'] != origin['sha256']:
            raise ValueError('Kaynak kararının kayıtlı kökeni uyuşmuyor')
    return True


def validate_source_risk_review(data, basis, risk_universe, decisions, *, reading_registry=None):
    """Require a linked substantive witness for each authored applicable risk."""
    by_id = {d['id']: d for d in decisions}
    if len(by_id) != len(decisions):
        raise ValueError('Kaynak anlamı risk kararları yinelenmiş')
    registry = reading_registry if reading_registry is not None else basis.get('_reading_registry')
    registered = registered_reading_fingerprints(registry)
    for decision in decisions:
        if canonical_json({k: v for k, v in decision.items() if k != 'id'}) not in registered:
            raise ValueError('Kaynak anlamı kararı kayıtlı özgün okumayla uyuşmuyor')
    cells = {c['id']: c for c in basis['cells']}
    rows = {r['id']: r for r in data['comparison_row']}
    fields = {f['id']: f for f in data['comparison_field']}
    syntheses = {s['id']: s for s in data['comparison_synthesis']}
    reviews = {r['subject_id']: r for r in data['comparison_semantic_review']
               if r['subject_kind'] == 'comparison_synthesis' and r['reviewer_kind'] == 'agent'}
    finding_reviews = {r['id']: r for r in data.get('review', []) if r.get('kind') == 'finding'}
    passages = {p['id']: p for p in data['passage']}
    versions = {v['id']: v for v in data['document_version']}
    changes = {c['id']: c for c in data['comparison_change']}
    missing = {m['id']: m for m in data['missing']}
    attempts = {a['id']: a for a in data['attempt']}
    evidence = {}
    for item in data['finding_evidence']:
        evidence.setdefault(item['finding_id'], set()).add(item['passage_id'])

    initial_origins = {}
    for item in registry['initial']:
        fingerprint = canonical_json({k: v for k, v in item.items() if k != 'id'})
        initial_origins.setdefault(fingerprint, set()).add(item['id'])

    def eligible(risk, decision):
        """Use authored historical examples plus typed facts for new witnesses."""
        fingerprint = canonical_json({k: v for k, v in decision.items() if k != 'id'})
        if initial_origins.get(fingerprint, set()).intersection(risk.get('witness_decision_ids', [])):
            return True
        category, _, value = risk['id'].partition(':')
        if category == 'party':
            return decision.get('party_id') == value
        if category == 'role':
            return decision.get('source_role') == value
        if category == 'field':
            return decision.get('kind') == 'field_support' and decision.get('field') == value
        if category == 'synthesis':
            return decision.get('kind') == 'synthesis_support' and decision.get('claim_type') == value
        if category == 'format':
            version = versions.get(decision.get('version_id'))
            mime = (version or {}).get('mime', '').lower()
            return bool(version and ((value == 'pdf' and 'pdf' in mime) or (value == 'html' and 'html' in mime)))
        if risk['id'] == 'semantic:multiple_evidence':
            return len(set(decision.get('summary_passage_ids', []))) >= 2
        if risk['id'] == 'semantic:before_after':
            return decision.get('kind') == 'change_support'
        if risk['id'] == 'semantic:real_document_gap':
            return decision.get('kind') == 'scope_or_document_gap' and bool(decision.get('missing_id'))
        if risk['id'] == 'semantic:narrow_negative_scope':
            return decision.get('kind') == 'scope_or_document_gap' and bool(decision.get('scope_id'))
        if risk['id'] == 'semantic:physical_page_gap':
            return decision.get('kind') == 'physical_page_gap'
        if risk['id'] == 'semantic:same_hash_copy':
            return decision.get('kind') == 'same_hash_copy'
        # A new contextual classification requires its own registered,
        # source-linked rationale; a naked category name is insufficient.
        refs = set(decision.get('summary_passage_ids', []) + decision.get('quote_passage_ids', []))
        refs.update(v for k in ('scope_id', 'missing_id', 'change_id', 'synthesis_id') if (v := decision.get(k)))
        return any(claim.get('risk_id') == risk['id'] and claim.get('reason') and
                   isinstance(claim.get('refs'), list) and claim['refs'] and set(claim['refs']) <= refs
                   for claim in decision.get('risk_claims', []))

    def witnessed(decision, constraints):
        kind = decision.get('kind')
        if kind not in constraints['allowed_decision_kinds'] or decision.get('reviewer_kind') != 'agent' or not all(decision.get(k) for k in ('judgment', 'recorded_at', 'reading_origin')):
            return False
        try:
            if dt.datetime.fromisoformat(decision['recorded_at'].replace('Z', '+00:00')).tzinfo is None:
                return False
        except (TypeError, ValueError, AttributeError):
            return False
        if kind in ('field_support', 'scope_or_document_gap') and decision.get('decision') not in ('supported_with_stated_scope', 'documentary_limitation_preserved'):
            return False
        cell = cells.get(decision.get('cell_id'))
        if kind in ('field_support', 'scope_or_document_gap', 'change_support'):
            row = rows.get(decision.get('row_id'))
            if not cell or not row or row['id'] != (cell['mapping_records'][-1]['new_row_id'] if cell['mapping_records'] else cell['logical_key']['context_judgment']):
                return False
            if not decision.get('source_reading'):
                return False
        if kind == 'field_support':
            field = fields.get(decision.get('field_id'))
            if not field or field['row_id'] != row['id'] or any(field.get(k) != decision.get(k) for k in ('field', 'condition_key', 'summary_finding_id', 'quote_finding_id')):
                return False
            if any(row.get(k) != decision.get(k) for k in ('party_id', 'version_id', 'source_role')):
                return False
            if not set(decision.get('basis_ids', [])) & set(cell['basis_ids']):
                return False
            for side in ('summary', 'quote'):
                ids = decision.get(side + '_passage_ids', [])
                if not ids or not set(ids) <= evidence.get(decision[side + '_finding_id'], set()) or any(pid not in passages or passages[pid]['version_id'] != row['version_id'] for pid in ids):
                    return False
            lineage = decision.get('original_field_review')
            if lineage:
                if not isinstance(lineage, dict) or not isinstance(lineage.get('finding_reviews'), list):
                    return False
                prior = lineage['finding_reviews']
                if not {decision['summary_finding_id'], decision['quote_finding_id']} <= {r.get('subject_id') for r in prior}:
                    return False
                for record in prior:
                    if finding_reviews.get(record.get('id')) != record or record.get('reviewer_kind') != 'agent' or record.get('result') != 'reviewed' or not record.get('reason'):
                        return False
                    try:
                        if dt.datetime.fromisoformat(record['reviewed_at'].replace('Z', '+00:00')).tzinfo is None:
                            return False
                    except (KeyError, TypeError, ValueError, AttributeError):
                        return False
                return True
            return bool(decision['reading_origin'] in ('new_bounded_original_html_reading', 'new_bounded_original_reading') and
                        decision.get('source_sha256') == versions[row['version_id']]['sha256'] and decision.get('limit'))
        if kind == 'scope_or_document_gap':
            return (row.get('scope_id') == decision.get('scope_id') and row.get('missing_id') == decision.get('missing_id') and
                    all(row.get(k) == decision.get(k) for k in ('party_id', 'version_id', 'source_role')) and
                    bool(set(decision.get('basis_ids', [])) & set(cell['basis_ids'])))
        if kind == 'change_support':
            change = changes.get(decision.get('change_id'))
            before, after = passages.get(decision.get('before_passage_id')), passages.get(decision.get('after_passage_id'))
            return bool(change and before and after and change['row_id'] == row['id'] and
                        change['before_passage_id'] == before['id'] and change['after_passage_id'] == after['id'] and
                        before['version_id'] != after['version_id'] and change['order_basis'] == decision.get('order_basis'))
        if kind == 'synthesis_support':
            sid = decision.get('synthesis_id')
            if sid not in syntheses or reviews.get(sid) != decision.get('original_semantic_review'):
                return False
            try:
                authored = json.loads(reviews[sid]['reason'])
                if any(authored.get(k) != decision.get(k) for k in ('claim_type', 'sides', 'explanation')):
                    return False
                return validate_synthesis_v2(data, syntheses[sid])
            except (KeyError, TypeError, ValueError):
                return False
        if kind == 'physical_page_gap':
            m, a = missing.get(decision.get('missing_id')), attempts.get(decision.get('attempt_id'))
            return bool(m and a and m['attempt_id'] == a['id'] and decision.get('version_id') in versions and
                        a.get('source_version_id') == decision['version_id'] and
                        all(m.get(k) == a.get(k) for k in ('party_id', 'heading', 'topic_id')) and decision.get('source_reading'))
        if kind == 'same_hash_copy':
            copies = decision.get('versions', [])
            return len(copies) >= 2 and all(versions.get(v.get('id')) == v for v in copies) and len({v['sha256'] for v in copies}) == 1
        return False

    for decision in decisions:
        if not witnessed(decision, {'allowed_decision_kinds': [decision.get('kind')]}):
            raise ValueError('Kaynak anlamı kararı kaynak bağları veya kökeni geçersiz: ' + str(decision.get('id')))
    for risk in risk_universe:
        if not risk.get('required'):
            continue
        if not risk.get('selection_rationale') or not any(
                eligible(risk, decision) and witnessed(decision, risk['witness_constraints'])
                for decision in decisions):
            raise ValueError('Kaynak anlamı riski için maddi inceleme eksik: ' + str(risk.get('id')))
    return True


def validate_legacy_completion_projection(data):
    """Validate retained v1 proofs against their own immutable record sets."""
    for marker in data.get('comparison_completion', []):
        try:
            proof = json.loads(marker['evidence'])
            projection = dict(data)
            for table in COMPLETION_V2_TABLES:
                projection.pop(table, None)
            for name, table, identity in (
                ('topics', 'comparison_topic', lambda x: (x['topic_id'], x['taxonomy_version'])),
                ('rows', 'comparison_row', lambda x: x['id']),
                ('fields', 'comparison_field', lambda x: x['id']),
                ('syntheses', 'comparison_synthesis', lambda x: x['id']),
                ('inventory', 'comparison_source_inventory', lambda x: x['id']),
            ):
                expected = proof[name]
                actual = {identity(item): item for item in data[table]}
                if len({identity(item) for item in expected}) != len(expected) or any(actual.get(identity(item)) != item for item in expected):
                    raise ValueError('Önceki kaynak kapanışı kayıtları değiştirilmiş')
                projection[table] = expected
            projection['comparison_completion'] = [marker]
            projection['comparison_contract'] = [dict(data['comparison_contract'][0],
                                                      taxonomy_version=marker['taxonomy_version'], stage='complete')]
            validate_completion(projection)
        except (KeyError, TypeError, json.JSONDecodeError) as exc:
            raise ValueError('Önceki kaynak kapanışı kanıtı geçersiz') from exc
    return True


def completion_selection(data, taxonomy_version):
    rows = [r for r in data['comparison_row'] if r['taxonomy_version'] == taxonomy_version]
    row_ids = {r['id'] for r in rows}
    return dict(topics=[t for t in data['comparison_topic'] if t['taxonomy_version'] == taxonomy_version],
                rows=rows, fields=[f for f in data['comparison_field'] if f['row_id'] in row_ids],
                syntheses=[s for s in data['comparison_synthesis'] if s['taxonomy_version'] == taxonomy_version],
                inventory=[i for i in data['comparison_source_inventory'] if i['taxonomy_version'] == taxonomy_version])


def completion_manifest_fields(data):
    """Bind the active immutable revision and its substantive stored inputs."""
    revisions = data.get('comparison_completion_revision', [])
    if not revisions:
        return {}
    active = max(revisions, key=lambda r: r['epoch'])
    head = next(b for b in data['comparison_completion_basis'] if b['id'] == active['basis_id'])
    cells = sorted((c for c in data['comparison_coverage_disposition'] if c['basis_id'] == head['id']),
                   key=lambda c: c['cell_id'])
    basis_digest = hashlib.sha256(canonical_json({'basis': head, 'dispositions': cells}).encode()).hexdigest()
    return dict(comparison_completion_revision_id=active['id'], comparison_completion_epoch=active['epoch'],
                comparison_completion_basis_id=head['id'], comparison_completion_stage=active['stage'],
                comparison_completion_basis_sha256=basis_digest,
                comparison_completion_selection_sha256=hashlib.sha256(active['selection'].encode()).hexdigest(),
                comparison_completion_review_sha256=hashlib.sha256(active['review'].encode()).hexdigest())


def completion_adoption_payload(data, basis, risk, created_at):
    """Prepare the first v2 adoption without changing its historical marker."""
    marker = data.get('comparison_completion', [])
    contract = data['comparison_contract'][0]
    if len(marker) != 1 or contract['stage'] != 'complete' or basis['taxonomy_version'] != contract['taxonomy_version']:
        raise ValueError('Kaynak kapanışı başlangıç tabanı geçersiz')
    registry = {'initial': risk['decisions'], 'additional': []}
    verify_initial_completion_basis(basis, risk['expected_risk_universe'], reading_registry=registry)
    validate_source_basis_universe(data, basis)
    validate_source_risk_review(data, basis, risk['expected_risk_universe'], risk['decisions'], reading_registry=registry)
    basis_id = 'completion-basis-v2-' + hashlib.sha256(canonical_json(basis).encode()).hexdigest()[:24]
    head, cells = completion_basis_records(basis, risk['expected_risk_universe'], basis_id, created_at, reading_registry=registry)
    anchor = canonical_json(dict(release_id=data['release_id'], marker_sha256=hashlib.sha256(canonical_json(marker[0]).encode()).hexdigest()))
    revision = dict(version=2, epoch=1, parent_revision_id=None, taxonomy_version=contract['taxonomy_version'],
                    basis_id=basis_id, stage='complete', created_at=created_at, legacy_anchor=anchor,
                    selection=canonical_json(completion_selection(data, contract['taxonomy_version'])),
                    review=canonical_json({'decisions': risk['decisions']}),
                    reason='Bağımsız kaynak evreni ve tarihli anlam kararlarıyla ilk sürüm 2 kapanışı.')
    revision['id'] = 'completion-revision-v2-' + hashlib.sha256(canonical_json(revision).encode()).hexdigest()[:24]
    records = ([dict(kind='comparison_completion_basis', values=head)] +
               [dict(kind='comparison_coverage_disposition', values=cell) for cell in cells] +
               [dict(kind='comparison_completion_revision', values=revision)])
    return dict(contract_version=contract['version'], taxonomy_version=contract['taxonomy_version'], stage='complete', records=records)


def validate_completion_basis_successor(old, new):
    """An appended basis may extend, but must retain, earlier obligations."""
    old_registry, new_registry = old.get('_reading_registry'), new.get('_reading_registry')
    if old_registry is not None:
        registered_reading_fingerprints(old_registry)
        registered_reading_fingerprints(new_registry)
        if old_registry['initial'] != new_registry['initial'] or any(item not in new_registry['additional'] for item in old_registry['additional']):
            raise ValueError('Önceki kaynak okuması kayıtları değiştirilemez')
    old_corrections = old.get('_correction_registry')
    if old_corrections is not None:
        if not isinstance(new.get('_correction_registry'), list) or any(item not in new['_correction_registry'] for item in old_corrections):
            raise ValueError('Önceki kaynak düzeltme kararları değiştirilemez')
    if new['taxonomy_version'] != old['taxonomy_version']:
        if new['taxonomy_version'] != old['taxonomy_version'] + 1:
            raise ValueError('Yeni kaynak sözlüğü öncekinin hemen ardılı olmalı')
        for key, value in old['source_assertions'].items():
            if new['source_assertions'].get(key) != value:
                raise ValueError('Önceki kaynak dayanağı değiştirilemez')
        documents = {item['path']: item for item in new['source_documents']}
        if any(documents.get(item['path']) != item for item in old['source_documents']):
            raise ValueError('Önceki kaynak paketinin kökeni değiştirilemez')
        # Row and topic replacements are authorized separately by the
        # contract-3 lineage and its source-backed meaning decisions.
        return True
    for name, identity in (('topics', lambda x: x['topic_id']),
                           ('cells', lambda x: x['id']),
                           ('synthesis_obligations', lambda x: x['id'])):
        latest = {identity(x): x for x in new[name]}
        if any(latest.get(identity(item)) != item for item in old[name]):
            raise ValueError('Önceki kaynak yükümlülüğü değiştirilemez: ' + name)
    for key, value in old['source_assertions'].items():
        if new['source_assertions'].get(key) != value:
            raise ValueError('Önceki kaynak dayanağı değiştirilemez')
    documents = {item['path']: item for item in new['source_documents']}
    if any(documents.get(item['path']) != item for item in old['source_documents']):
        raise ValueError('Önceki kaynak paketinin kökeni değiştirilemez')
    latest_inventory = {canonical_json(item) for item in new['inventory_sections']}
    if any(canonical_json(item) not in latest_inventory for item in old['inventory_sections']):
        raise ValueError('Önceki kaynak envanteri değiştirilemez')
    pairs = {(x['topic_id'], x['party_id']): x for x in new['universe']}
    for item in old['universe']:
        successor = pairs.get((item['topic_id'], item['party_id']))
        if not successor or not set(item['cell_ids']) <= set(successor['cell_ids']):
            raise ValueError('Önceki parti-konu kapsamı değiştirilemez')
    return True


def verify_successor_completion_basis(old, new):
    """Reconcile newly authored obligations with their actual source packages."""
    validate_completion_basis_successor(old, new)
    old_registry, new_registry = old.get('_reading_registry'), new.get('_reading_registry')
    if old_registry is not None:
        for registration in new_registry['additional']:
            if registration in old_registry['additional']:
                continue
            origin = registration['origin']
            document = next((d for d in new['source_documents'] if d['path'] == origin['path']), None)
            if not document or document['sha256'] != origin['sha256']:
                raise ValueError('Yeni kaynak okuması bağımsız kaynak kataloğunda yok')
            file = safe_path(DATA, origin['path'][len('data/'):])
            if sha(file) != origin['sha256'] or file.read_text(encoding='utf-8') != origin['content']:
                raise ValueError('Yeni kaynak okumasının kayıt dosyası uyuşmuyor')
    for registration in new.get('_correction_registry', []):
        if registration in (old.get('_correction_registry') or []):
            continue
        validate_registered_decision(registration)
        origin = registration['origin']
        document = next((d for d in new['source_documents'] if d['path'] == origin['path']), None)
        if not document or document['sha256'] != origin['sha256']:
            raise ValueError('Yeni düzeltme bağımsız kaynak kataloğunda yok')
        file = safe_path(DATA, origin['path'][len('data/'):])
        if sha(file) != origin['sha256'] or file.read_text(encoding='utf-8') != origin['content']:
            raise ValueError('Yeni düzeltmenin kaynak kaydı uyuşmuyor')
    documents, record_index = {}, {}
    for item in new['source_documents']:
        path = item['path']
        if not path.startswith('data/') or path in documents:
            raise ValueError('Kaynak paket yolu geçersiz')
        file = safe_path(DATA, path[len('data/'):])
        if sha(file) != item['sha256']:
            raise ValueError('Kaynak paketi özgün özeti uyuşmuyor: ' + path)
        payload = json.loads(file.read_text(encoding='utf-8'))
        documents[path] = payload
        for entry in payload.get('records', []):
            if isinstance(entry, dict) and isinstance(entry.get('values'), dict):
                value = entry['values']
                if value.get('id'):
                    record_index.setdefault((entry.get('kind'), value['id']), []).append(value)

    def resolve(ref):
        try:
            value = documents[ref['path']]
            pointer = ref['pointer']
            if not pointer.startswith('/'):
                raise ValueError('geçersiz gösterici')
            for token in pointer[1:].split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                value = value[int(token)] if isinstance(value, list) else value[token]
            return value
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ValueError('Yeni kaynak kararının özgün adresi geçersiz') from exc

    previous_cells = {c['id']: c for c in old['cells']}
    added_cells = [c for c in new['cells'] if previous_cells.get(c['id']) != c]
    new_assertions = set(new['source_assertions']) - set(old['source_assertions'])
    if not new_assertions <= {bid for cell in added_cells for bid in cell['basis_ids']}:
        raise ValueError('Yeni kaynak dayanağı kaynak hücresine bağlanmalı')
    for cell in added_cells:
        if resolve(cell['source_judgment']) != cell['source_judgment_record'] or len(cell['mapping_refs']) != len(cell['mapping_records']) or any(resolve(ref) != record for ref, record in zip(cell['mapping_refs'], cell['mapping_records'])):
            raise ValueError('Yeni kaynak kararı veya eşlemesi uyuşmuyor')
    for bid in new_assertions:
        item = new['source_assertions'][bid]
        kind = item.get('kind')
        if kind == 'supported_field':
            original = resolve(item['original_field'])
            if any(original.get(k) != item.get(k) for k in ('field', 'condition_key', 'summary_finding_id', 'quote_finding_id')):
                raise ValueError('Yeni alanın özgün kaynak kararı uyuşmuyor')
            reviews = item.get('semantic_reviews', []) + item.get('finding_reviews', [])
            if not reviews or any(resolve(r['source']) != r['record'] or not r['record'].get('reason') or not r['record'].get('reviewed_at') or r['record'].get('reviewer_kind') != 'agent' or r['record'].get('result') != 'reviewed' for r in reviews):
                raise ValueError('Yeni alanın gerekçeli anlam incelemesi eksik')
        elif kind == 'dated_source_scope':
            if resolve(item['source']) != item['scope']:
                raise ValueError('Yeni tarihli kaynak kapsamı uyuşmuyor')
        elif kind == 'documentary_gap':
            m, a = item.get('missing') or {}, item.get('attempt') or {}
            if m not in record_index.get(('missing', m.get('id')), []) or a not in record_index.get(('attempt', a.get('id')), []) or m.get('attempt_id') != a.get('id'):
                raise ValueError('Yeni belge açığının özgün araması uyuşmuyor')
        else:
            raise ValueError('Yeni kaynak dayanağı türü geçersiz')
    old_claims = {c['id'] for c in old['synthesis_obligations']}
    for claim in new['synthesis_obligations']:
        if claim['id'] not in old_claims and (resolve(claim['source']) != claim['source_authored_claim'] or resolve(claim['review_source']) != claim['original_review']):
            raise ValueError('Yeni sentez kararının kökeni uyuşmuyor')
    previous_inventory = {canonical_json(item) for item in old['inventory_sections']}
    authored_inventory = {canonical_json(item) for payload in documents.values() for item in payload.get('sections', []) if isinstance(item, dict)}
    if any(canonical_json(item) not in authored_inventory for item in new['inventory_sections'] if canonical_json(item) not in previous_inventory):
        raise ValueError('Yeni envanter bölümünün özgün kaynağı eksik')
    return True


def completion_superseded_cells(data, revision, revisions, basis, selection):
    """Verify explicit source-backed replacements while retaining prior records."""
    epochs = {r['id']: r['epoch'] for r in revisions}
    taxonomies = {r['id']: r['taxonomy_version'] for r in revisions}
    by_epoch = {r['epoch']: r for r in revisions}
    cells = {c['id']: c for c in basis['cells']}
    rows = {r['id']: r for r in data['comparison_row']}
    findings = {f['id']: f for f in data['finding']}
    assertions = basis['source_assertions']
    registry = basis.get('_correction_registry')
    if not isinstance(registry, list):
        raise ValueError('Kaynak düzeltme kararları kataloğu eksik')
    corrections = {}
    for item in registry:
        decision = validate_registered_decision(item)
        if not isinstance(decision, dict) or not decision.get('id') or decision['id'] in corrections:
            raise ValueError('Kaynak düzeltme kararları yinelenmiş')
        corrections[decision['id']] = decision

    def context(cell):
        original = cell['source_judgment_record']
        result = dict(logical_key=cell['logical_key'], disposition=cell['disposition'],
                      source_reason=original.get('selection_reason'), fields=[], scope=None, missing=None, attempt=None)
        for bid in cell['basis_ids']:
            assertion = assertions[bid]
            if assertion['kind'] == 'supported_field':
                summary, quote = findings[assertion['summary_finding_id']], findings[assertion['quote_finding_id']]
                result['fields'].append(dict(field=assertion['field'], condition_key=assertion['condition_key'],
                    summary_finding_id=summary['id'], summary_text=summary['text'],
                    quote_finding_id=quote['id'], quote_text=quote['text'], passage_ids=assertion['passage_ids']))
            elif assertion['kind'] == 'dated_source_scope':
                result['scope'] = assertion['scope']
            elif assertion['kind'] == 'documentary_gap':
                result['missing'], result['attempt'] = assertion['missing'], assertion['attempt']
        result['fields'].sort(key=canonical_json)
        return result
    active = {r['id'] for r in selection['rows']}
    excluded = set()
    links = data.get('comparison_completion_supersession', [])
    if any(link['revision_id'] not in epochs for link in links):
        raise ValueError('Kaynak ardıllığının revizyonu yok')
    links = sorted((link for link in links if epochs[link['revision_id']] <= revision['epoch'] and
                    taxonomies[link['revision_id']] == revision['taxonomy_version']),
                   key=lambda link: epochs[link['revision_id']])
    for index, link in enumerate(links):
        epoch = epochs.get(link['revision_id'])
        if epoch <= 1:
            raise ValueError('Kaynak ardıllığı önceki bir revizyon gerektirir')
        old, new = cells.get(link['old_cell_id']), cells.get(link['new_cell_id'])
        if not old or not new or old['id'] in excluded or old['id'] == new['id'] or not link.get('reason'):
            raise ValueError('Kaynak ardıllığının hücreleri geçersiz')
        old_key, new_key = old['logical_key'], new['logical_key']
        if any(old_key[k] != new_key[k] for k in ('topic_id', 'party_id', 'source_role')):
            raise ValueError('Kaynak ardıllığı konu, parti veya belge türünü değiştiremez')
        old_id = old['mapping_records'][-1]['new_row_id'] if old['mapping_records'] else old_key['context_judgment']
        new_id = new['mapping_records'][-1]['new_row_id'] if new['mapping_records'] else new_key['context_judgment']
        try:
            reference = json.loads(link['source_basis_refs'])
        except (TypeError, ValueError) as exc:
            raise ValueError('Kaynak ardıllığı dayanağı geçersiz') from exc
        if not isinstance(reference, dict) or set(reference) != {'correction_id', 'basis_ids'}:
            raise ValueError('Kaynak ardıllığı bağımsız düzeltme kararı gerektirir')
        refs = reference['basis_ids']
        correction = corrections.get(reference['correction_id'])
        if not correction or correction.get('result') != 'supersedes' or correction.get('reviewer_kind') != 'agent' or not correction.get('reason'):
            raise ValueError('Kaynak ardıllığı bağımsız düzeltme kararı gerektirir')
        try:
            reviewed = dt.datetime.fromisoformat(correction['reviewed_at'].replace('Z', '+00:00'))
            created = dt.datetime.fromisoformat(by_epoch[epoch]['created_at'].replace('Z', '+00:00'))
            if reviewed.tzinfo is None or created.tzinfo is None or reviewed > created:
                raise ValueError('Zaman dilimi gerekli')
        except (KeyError, TypeError, ValueError, AttributeError) as exc:
            raise ValueError('Kaynak düzeltme tarihi geçersiz') from exc
        old_context, new_context = context(old), context(new)
        if (correction.get('old_cell_id'), correction.get('new_cell_id'), correction.get('old_row_id'), correction.get('new_row_id')) != (old['id'], new['id'], old_id, new_id) or correction.get('old_context') != old_context or correction.get('new_context') != new_context:
            raise ValueError('Kaynak düzeltmesi eski ve yeni kaynak bağlamlarıyla uyuşmuyor')
        if old['disposition'] == 'document_missing' and new['disposition'] == 'no_explicit_statement':
            missing, attempt, scope = old_context['missing'], old_context['attempt'], new_context['scope']
            reassessment = correction.get('gap_reassessment')
            versions = {v['id']: v for v in data['document_version']}
            documents = {d['id']: d for d in data['document']}
            attributions = {a['version_id']: a for a in data.get('source_attribution', [])}
            version = versions.get(new_key['version_id'])
            document = documents.get(version['document_id']) if version else None
            attribution = attributions.get(new_key['version_id'])
            title_terms = {'program': ('program',), 'charter': ('tüzük', 'tüzüğü')}
            if (not missing or not attempt or not scope or not version or not document or not attribution or
                    missing.get('attempt_id') != attempt.get('id') or
                    any(missing.get(k) != attempt.get(k) for k in ('party_id', 'heading', 'topic_id')) or
                    missing.get('party_id') != new_key['party_id'] or document.get('party_id') != new_key['party_id'] or
                    missing.get('heading') != {'program': 'Program', 'charter': 'Tüzük'}.get(new_key['source_role']) or
                    {'Bulunamadı': ('search', 'no_result'), 'Erişilemedi': ('access', 'failure'), 'Doğrulanamadı': ('verification', 'inconclusive')}.get(missing.get('status')) != (attempt.get('type'), attempt.get('result')) or
                    attribution.get('kind') != 'party_publication' or
                    not any(term in document.get('title', '').casefold() for term in title_terms.get(new_key['source_role'], ())) or
                    scope.get('party_id') != new_key['party_id'] or scope.get('version_id') != version['id'] or
                    scope.get('result') != 'no_explicit_statement' or not all(scope.get(k) for k in ('sections', 'query_terms', 'reason', 'reviewed_at')) or
                    not isinstance(reassessment, dict) or reassessment.get('missing_id') != missing['id'] or
                    reassessment.get('attempt_id') != attempt['id'] or reassessment.get('version_id') != version['id'] or
                    reassessment.get('scope_id') != scope['id'] or reassessment.get('query_terms') != scope['query_terms'] or
                    reassessment.get('sections') != scope['sections'] or reassessment.get('reviewed_at') != scope['reviewed_at'] or
                    reassessment.get('coverage') != 'complete_relevant_scope' or not reassessment.get('reason')):
                raise ValueError('Belge açığından tarihli kaynak kapsamına geçiş geçersiz')
            try:
                scanned = dt.datetime.fromisoformat(scope['reviewed_at'].replace('Z', '+00:00'))
                searched = dt.datetime.fromisoformat(attempt['attempted_at'].replace('Z', '+00:00'))
                if scanned.tzinfo is None or searched.tzinfo is None or scanned < searched or scanned > reviewed:
                    raise ValueError('Tarih sırası geçersiz')
            except (KeyError, TypeError, ValueError, AttributeError) as exc:
                raise ValueError('Belge araması ve kapsam tarihleri geçersiz') from exc
        elif old['disposition'] != new['disposition']:
            # A positive statement and a bounded negative scope are distinct
            # judgments. Reclassification needs a decision that explicitly
            # re-examines that scope against passages from the same version.
            scope_context = old_context if old['disposition'] == 'no_explicit_statement' else new_context
            evidence_context = new_context if new['disposition'] == 'evidence' else old_context
            scope = scope_context.get('scope')
            reassessment = correction.get('scope_reassessment')
            supported = {pid for field in evidence_context['fields'] for pid in field['passage_ids']}
            if scope:
                if (not isinstance(reassessment, dict) or reassessment.get('scope_id') != scope['id'] or
                        reassessment.get('query_terms') != scope['query_terms'] or reassessment.get('sections') != scope['sections'] or
                        reassessment.get('version_id') != scope['version_id'] or not reassessment.get('reason') or
                        not isinstance(reassessment.get('passage_ids'), list) or not reassessment['passage_ids'] or
                        not set(reassessment['passage_ids']) <= supported or
                        any(next((p['version_id'] for p in data['passage'] if p['id'] == pid), None) != scope['version_id'] for pid in reassessment['passage_ids'])):
                    raise ValueError('Farklı kaynak durumu için aynı kapsamın kaynaklı yeniden değerlendirilmesi gerekli')
            else:
                gap_context = old_context if old['disposition'] == 'document_missing' else new_context
                missing, attempt = gap_context.get('missing'), gap_context.get('attempt')
                reassessment = correction.get('gap_reassessment')
                version = evidence_context['logical_key']['version_id']
                if (not missing or not attempt or not isinstance(reassessment, dict) or
                        reassessment.get('missing_id') != missing['id'] or reassessment.get('attempt_id') != attempt['id'] or
                        reassessment.get('version_id') != version or not reassessment.get('reason') or
                        not isinstance(reassessment.get('passage_ids'), list) or not reassessment['passage_ids'] or
                        not set(reassessment['passage_ids']) <= supported or
                        any(next((p['version_id'] for p in data['passage'] if p['id'] == pid), None) != version for pid in reassessment['passage_ids'])):
                    raise ValueError('Belge açığı için kaynaklı yeniden değerlendirme gerekli')
        validate_source_basis_cells(data, revision['taxonomy_version'], [old, new], assertions)
        replaced_later = any(later['old_row_id'] == new_id and epochs[later['revision_id']] > epoch for later in links[index + 1:])
        previous_rows = {r['id'] for r in json.loads(by_epoch[epoch - 1]['selection'])['rows']}
        if (old_id != link['old_row_id'] or new_id != link['new_row_id'] or old_id not in rows or new_id not in rows or
                old_id not in previous_rows or old_id in active or (new_id not in active and not replaced_later) or not isinstance(refs, list) or not refs or
                not set(refs) <= set(new['basis_ids'])):
            raise ValueError('Kaynak ardıllığı etkin seçim ve dayanakla uyuşmuyor')
        excluded.add(old['id'])
    return excluded


def completion_superseded_syntheses(data, revision, revisions, basis, selection):
    """Bind retained source claims to separately authored replacement claims."""
    epochs = {r['id']: r['epoch'] for r in revisions}
    taxonomies = {r['id']: r['taxonomy_version'] for r in revisions}
    obligations = {item['id']: item for item in basis['synthesis_obligations']}
    selected = {s['id'] for s in selection['syntheses']}
    rows = {r['id']: r for r in data['comparison_row']}
    links = data.get('comparison_completion_supersession', [])
    retired = set()
    decisions = [validate_registered_decision(item) for item in basis.get('_correction_registry', [])]
    decisions = [d for d in decisions if d.get('kind') == 'synthesis_supersession']
    for decision in decisions:
        epoch = epochs.get(decision.get('revision_id'))
        if epoch is None:
            raise ValueError('Sentez ardıllığının revizyonu yok')
        # Earlier taxonomies are validated in their own revision and source
        # basis by validate_completion_revisions; their retained registry
        # entries must not retire claims from this taxonomy's selection.
        if epoch > revision['epoch'] or taxonomies[decision['revision_id']] != revision['taxonomy_version']:
            continue
        old, new = obligations.get(decision.get('old_id')), obligations.get(decision.get('new_id'))
        prior = next((r for r in revisions if r['epoch'] == epoch - 1), None)
        prior_ids = {s['id'] for s in json.loads(prior['selection'])['syntheses']} if prior else set()
        later_successor = any(d.get('old_id') == decision.get('new_id') and
                              epoch < epochs.get(d.get('revision_id'), -1) <= revision['epoch'] and
                              taxonomies.get(d.get('revision_id')) == revision['taxonomy_version']
                              for d in decisions)
        if (not old or not new or old['id'] in retired or old['id'] == new['id'] or
                not prior or prior['taxonomy_version'] != revision['taxonomy_version'] or
                old['source_authored_claim']['taxonomy_version'] != revision['taxonomy_version'] or
                new['source_authored_claim']['taxonomy_version'] != revision['taxonomy_version'] or
                old['topic_id'] != new['topic_id'] or decision.get('result') != 'supersedes' or
                decision.get('reviewer_kind') != 'agent' or not decision.get('reason') or
                decision.get('old_claim') != old['source_authored_claim'] or decision.get('new_claim') != new['source_authored_claim'] or
                decision.get('old_review') != old['original_review'] or decision.get('new_review') != new['original_review'] or
                old['id'] not in prior_ids or old['id'] in selected or
                (new['id'] not in selected and not later_successor)):
            raise ValueError('Kaynaklı sentez ardıllığı uyuşmuyor')
        try:
            reviewed = dt.datetime.fromisoformat(decision['reviewed_at'].replace('Z', '+00:00'))
            created = dt.datetime.fromisoformat(next(r for r in revisions if r['epoch'] == epoch)['created_at'].replace('Z', '+00:00'))
            if reviewed.tzinfo is None or created.tzinfo is None or reviewed > created:
                raise ValueError('invalid date')
            old_meaning = json.loads(old['original_review']['reason'])
            new_meaning = json.loads(new['original_review']['reason'])
        except (KeyError, ValueError, TypeError, StopIteration, AttributeError) as exc:
            raise ValueError('Sentez ardıllığı tarihi veya kararı geçersiz') from exc
        if decision.get('mode') == 'mechanical_rebind':
            if old['source_authored_claim']['text'] != new['source_authored_claim']['text'] or old['original_review']['reviewed_at'] != new['original_review']['reviewed_at']:
                raise ValueError('Mekanik sentez soyu metni ve gerçek inceleme tarihini korumalı')
            row_map = {link['old_row_id']: link['new_row_id'] for link in links
                       if epochs.get(link['revision_id'], 0) <= epoch and
                       taxonomies.get(link['revision_id']) == revision['taxonomy_version']}
            for side in old_meaning.get('sides', []):
                if side['row_id'] in row_map:
                    before, after = rows.get(side['row_id']), rows.get(row_map[side['row_id']])
                    old_fields = {(f['field'], f.get('condition_key'), f['summary_finding_id'], f['quote_finding_id']) for f in data['comparison_field'] if f['row_id'] == side['row_id']}
                    new_fields = {(f['field'], f.get('condition_key'), f['summary_finding_id'], f['quote_finding_id']) for f in data['comparison_field'] if f['row_id'] == row_map[side['row_id']]}
                    if not before or not after or any(before.get(k) != after.get(k) for k in ('topic_id', 'party_id', 'source_role', 'version_id', 'level', 'organ', 'state')) or old_fields != new_fields:
                        raise ValueError('Mekanik sentez soyu aynı kaynak anlamını gerektirir')
                    side['row_id'] = row_map[side['row_id']]
            if old_meaning != new_meaning:
                raise ValueError('Mekanik sentez soyu anlam ve dayanakları korumalı')
        elif decision.get('mode') == 'substantive':
            try:
                new_reviewed = dt.datetime.fromisoformat(new['original_review']['reviewed_at'].replace('Z', '+00:00'))
                old_reviewed = dt.datetime.fromisoformat(old['original_review']['reviewed_at'].replace('Z', '+00:00'))
                if new_reviewed.tzinfo is None or old_reviewed.tzinfo is None or new_reviewed <= old_reviewed or new_reviewed > reviewed or not new['original_review'].get('reason'):
                    raise ValueError('review date')
            except (KeyError, TypeError, ValueError, AttributeError) as exc:
                raise ValueError('Yeni sentez için tarihli kaynaklı anlam incelemesi gerekli') from exc
        else:
            raise ValueError('Yeni sentez için kaynaklı anlam incelemesi gerekli')
        retired.add(old['id'])
    return retired


def verify_initial_completion_basis(basis, risk_universe, *, reading_registry=None):
    """Reconcile the independently authored initial ledger to source packages.

    These reviewed corpus identities establish which complete ledger was
    adopted; source judgments, mapping bodies and dates are checked separately.
    Later audit uses the frozen records, not the files read here.
    """
    digest = completion_basis_digest(basis)
    registered_reading_fingerprints(reading_registry if reading_registry is not None else basis.get('_reading_registry'))
    risk_digest = hashlib.sha256(canonical_json(risk_universe).encode()).hexdigest()
    if digest != '1255473709cc4815a288d1f214cd9c96d111cf56a715ae6fbc64cb615fd2c719' or risk_digest != 'b513d957f49f2df597beafbc58969095d498e1cfeb78f96235cf55cb0a37feb9':
        raise ValueError('İlk kaynak evreni bağımsız hazırlanmış bütüne uyuşmuyor')
    sources = {}
    for item in basis['source_documents']:
        path = item['path']
        if not path.startswith('data/') or path in sources:
            raise ValueError('Kaynak paket yolu geçersiz')
        file = safe_path(DATA, path[len('data/'):])
        if sha(file) != item['sha256']:
            raise ValueError('Kaynak paketi özgün özeti uyuşmuyor: ' + path)
        sources[path] = json.loads(file.read_text(encoding='utf-8'))

    def resolve(ref):
        if not isinstance(ref, dict) or ref.get('path') not in sources or not ref.get('pointer', '').startswith('/'):
            raise ValueError('Kaynak kararının özgün adresi geçersiz')
        value = sources[ref['path']]
        try:
            for token in ref['pointer'][1:].split('/'):
                token = token.replace('~1', '/').replace('~0', '~')
                value = value[int(token)] if isinstance(value, list) else value[token]
        except (ValueError, TypeError, IndexError, KeyError) as exc:
            raise ValueError('Kaynak kararının özgün adresi bulunamadı') from exc
        return value

    for cell in basis['cells']:
        if resolve(cell['source_judgment']) != cell['source_judgment_record'] or len(cell['mapping_refs']) != len(cell['mapping_records']):
            raise ValueError('Özgün kaynak kararının içeriği uyuşmuyor')
        if any(resolve(ref) != record for ref, record in zip(cell['mapping_refs'], cell['mapping_records'])):
            raise ValueError('Özgün kaynak eşlemesinin içeriği uyuşmuyor')
    for claim in basis['synthesis_obligations']:
        if resolve(claim['source']) != claim['source_authored_claim'] or resolve(claim['review_source']) != claim['original_review']:
            raise ValueError('Özgün sentez kararı uyuşmuyor')
    inventory = sources.get('data/comparisons/03-source-inventory-v4.json', {})
    if inventory.get('sections') != basis['inventory_sections']:
        raise ValueError('Özgün kaynak envanteri uyuşmuyor')
    return True


def validate_completion_revisions(data):
    """Check immutable revision selections; the last epoch is the active one."""
    revisions = sorted(data.get('comparison_completion_revision', []), key=lambda r: r['epoch'])
    bases = {b['id']: b for b in data.get('comparison_completion_basis', [])}
    dispositions = data.get('comparison_coverage_disposition', [])
    if not revisions or len(bases) != len(data.get('comparison_completion_basis', [])):
        raise ValueError('Kaynak kapanışı revizyonu eksik')
    validate_legacy_completion_projection(data)
    previous = previous_source = previous_risk = previous_stamp = None
    spec = {'topics': ('comparison_topic', lambda x: (x['topic_id'], x['taxonomy_version'])),
            'rows': ('comparison_row', lambda x: x['id']),
            'fields': ('comparison_field', lambda x: x['id']),
            'syntheses': ('comparison_synthesis', lambda x: x['id']),
            'inventory': ('comparison_source_inventory', lambda x: x['id'])}
    for index, revision in enumerate(revisions):
        if revision['version'] != 2 or revision['epoch'] != index + 1 or revision['parent_revision_id'] != (previous['id'] if previous else None) or revision['stage'] not in ('partial', 'complete') or not revision['reason']:
            raise ValueError('Kaynak kapanışı revizyon zinciri geçersiz')
        try:
            stamp = dt.datetime.fromisoformat(revision['created_at'].replace('Z', '+00:00'))
            if stamp.tzinfo is None or (previous_stamp is not None and stamp < previous_stamp):
                raise ValueError('Zaman dilimi gerekli')
            if data.get('comparison_completion'):
                anchor = json.loads(revision['legacy_anchor'])
                anchor_markers = [m for m in data['comparison_completion']
                                  if hashlib.sha256(canonical_json(m).encode()).hexdigest() == anchor.get('marker_sha256')]
                if not anchor.get('release_id') or len(anchor_markers) != 1 or (previous and revision['legacy_anchor'] != previous['legacy_anchor']):
                    raise ValueError('Önceki kaynak kapanışı çapası uyuşmuyor')
            elif revision['legacy_anchor'] is not None:
                raise ValueError('Var olmayan önceki kaynak kapanışı çapası reddedildi')
            selection = json.loads(revision['selection'])
            review = json.loads(revision['review'])
            head = bases[revision['basis_id']]
            if head['version'] != 2 or head['taxonomy_version'] != revision['taxonomy_version']:
                raise ValueError('Sözlük uyuşmuyor')
            source, risk = decode_completion_basis(head, [d for d in dispositions if d['basis_id'] == head['id']])
            validate_basis_registry_origins(source)
            registered = registered_reading_fingerprints(source['_reading_registry'])
            for decision in review.get('decisions', []):
                if canonical_json({k: v for k, v in decision.items() if k != 'id'}) not in registered:
                    raise ValueError('Kaynak anlamı kararı kayıtlı özgün okumayla uyuşmuyor')
                read_at = dt.datetime.fromisoformat(decision['recorded_at'].replace('Z', '+00:00'))
                if read_at.tzinfo is None or read_at > stamp:
                    raise ValueError('Kaynak okuması revizyon zamanını aşamaz')
            if previous_source is None and source['_reading_registry']['additional']:
                raise ValueError('İlk kaynak evreninde ek okuma kaydı bulunamaz')
            if not isinstance(source.get('_correction_registry'), list):
                raise ValueError('Kaynak düzeltme kararları kataloğu eksik')
            if previous_source is None and source['_correction_registry']:
                raise ValueError('İlk kaynak evreninde önceki düzeltme bulunamaz')
            if previous_source is None and (completion_basis_digest(source) != '1255473709cc4815a288d1f214cd9c96d111cf56a715ae6fbc64cb615fd2c719' or hashlib.sha256(canonical_json(risk).encode()).hexdigest() != 'b513d957f49f2df597beafbc58969095d498e1cfeb78f96235cf55cb0a37feb9'):
                raise ValueError('İlk kaynak evreni bağımsız hazırlanmış bütüne uyuşmuyor')
            if previous_source is not None and revision['basis_id'] != previous['basis_id']:
                if head['parent_basis_id'] != previous['basis_id']:
                    raise ValueError('Kaynak sözlüğü soy zinciri geçersiz')
                validate_completion_basis_successor(previous_source, source)
                if source['taxonomy_version'] != previous_source['taxonomy_version']:
                    if data['comparison_contract'][0]['version'] != 3:
                        raise ValueError('Yeni kaynak sözlüğü kalıcı satır soyu gerektirir')
                    validate_versioned_row_lineage(data)
                risks = {r['id']: r for r in risk}
                if any(risks.get(r['id']) != r for r in previous_risk):
                    raise ValueError('Önceki kaynak riski değiştirilemez')
            projection = dict(data)
            for name, (table, identity) in spec.items():
                selected = selection[name]
                actual = {identity(r): r for r in data[table]}
                if len({identity(r) for r in selected}) != len(selected) or any(actual.get(identity(r)) != r for r in selected):
                    raise ValueError('Seçili tarihsel kayıt değişmiş')
                projection[table] = selected
            excluded = completion_superseded_cells(data, revision, revisions, source, selection)
            excluded_syntheses = completion_superseded_syntheses(data, revision, revisions, source, selection)
            if revision['stage'] == 'complete':
                validate_source_basis_universe(projection, source, excluded, excluded_syntheses)
                for synthesis in selection['syntheses']:
                    validate_synthesis_v2(projection, synthesis)
                validate_source_risk_review(projection, source, risk, review['decisions'])
            elif review.get('decisions'):
                validate_source_risk_review(projection, source, [], review['decisions'])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError('Kaynak kapanışı revizyon kanıtı geçersiz: ' + str(exc)) from exc
        previous = revision
        previous_source, previous_risk = source, risk
        previous_stamp = stamp
    active = revisions[-1]
    contract = data['comparison_contract'][0]
    if (active['taxonomy_version'], active['stage']) != (contract['taxonomy_version'], contract['stage']):
        raise ValueError('Kaynak kapanışı aktif aşamayla uyuşmuyor')
    selected = json.loads(active['selection'])
    current = completion_selection(data, active['taxonomy_version'])
    excluded_rows = {s['old_row_id'] for s in data.get('comparison_completion_supersession', [])}
    current['rows'] = [r for r in current['rows'] if r['id'] not in excluded_rows]
    current['fields'] = [f for f in current['fields'] if f['row_id'] not in excluded_rows]
    current['syntheses'] = [s for s in current['syntheses'] if s['id'] not in excluded_syntheses]
    for name, (_, identity) in spec.items():
        if {identity(x): x for x in selected[name]} != {identity(x): x for x in current[name]}:
            raise ValueError('Kaynak kapanışı aktif seçimi uyuşmuyor')
    return True


def validate_completion(data):
    """Validate an explicitly adopted, snapshot-bound source closure contract.

    Earlier complete snapshots have no such marker and retain their original
    contract. The review describes agent work, never a human acceptance.
    """
    if data.get('comparison_completion_revision'):
        return validate_completion_revisions(data)
    if any(data.get(name) for name in COMPLETION_V2_TABLES):
        raise ValueError('Kaynak kapanışı revizyon ailesi eksik')
    markers = data.get('comparison_completion', [])
    if not markers:
        return True
    if any(LEGACY_COMPLETION_MARKERS.get((m.get('version'), m.get('taxonomy_version'))) !=
           hashlib.sha256(canonical_json(m).encode()).hexdigest() for m in markers):
        raise ValueError('Önceki kaynak kapanışı tarihsel işaretçisi doğrulanamadı')
    contract = data['comparison_contract'][0]
    if contract['stage'] != 'complete':
        raise ValueError('Kaynak kapanışı tam aşama gerektirir')
    if any(m.get('version') != 1 for m in markers):
        raise ValueError('Bilinmeyen kaynak kapanışı sözleşmesi')
    selected = [m for m in markers if m.get('taxonomy_version') == contract['taxonomy_version']]
    if len(selected) != 1:
        raise ValueError('Seçili sözlük için kaynak kapanışı gerekli')
    try:
        proof = json.loads(selected[0]['evidence'])
    except (KeyError, TypeError, ValueError):
        raise ValueError('Kaynak kapanış kanıtı geçersiz')
    if not isinstance(proof, dict):
        raise ValueError('Kaynak kapanış kanıtı nesne olmalı')
    version = contract['taxonomy_version']
    rows = [r for r in data['comparison_row'] if r['taxonomy_version'] == version]
    row_ids = {r['id'] for r in rows}
    actual = {
        'topics': [t for t in data['comparison_topic'] if t['taxonomy_version'] == version],
        'rows': rows,
        'fields': [f for f in data['comparison_field'] if f['row_id'] in row_ids],
        'syntheses': [s for s in data['comparison_synthesis'] if s['taxonomy_version'] == version],
        'inventory': [i for i in data['comparison_source_inventory'] if i['taxonomy_version'] == version],
    }
    for name, records in actual.items():
        expected = proof.get(name)
        key = 'topic_id' if name == 'topics' else 'id'
        if not isinstance(expected, list) or not expected or any(not isinstance(r, dict) or key not in r for r in expected):
            raise ValueError('Kaynak kapanış kapsamı eksik: ' + name)
        expected_by_id = {r[key]: r for r in expected}
        actual_by_id = {r[key]: r for r in records}
        if len(expected_by_id) != len(expected) or len(actual_by_id) != len(records) or expected_by_id != actual_by_id:
            raise ValueError('Kaynak kapanış kapsamı değişmiş: ' + name)
    if any(r['state'] not in ('evidence', 'no_explicit_statement', 'document_missing') for r in rows):
        raise ValueError('Kaynak kapanışında açık inceleme var')
    review = proof.get('source_review')
    if not isinstance(review, dict) or review.get('reviewer_kind') != 'agent' or not review.get('sample_rationale') or not review.get('actual_reading_time'):
        raise ValueError('Kaynak anlamı incelemesinin kökeni eksik')
    versions = {v['id']: v for v in data['document_version']}
    sources = review.get('source_versions')
    if not isinstance(sources, list) or not sources:
        raise ValueError('Kaynak incelemesinin belge sürümleri eksik')
    for source in sources:
        version_record = versions.get(source.get('id'))
        if not version_record or source.get('sha256') != version_record['sha256'] or source.get('computed_sha256') != version_record['sha256'] or source.get('original_path') != version_record['original_path'] or not source.get('reading_provenance'):
            raise ValueError('Kaynak incelemesinin belge sürümü uyuşmuyor')
    checks = review.get('checks')
    if not isinstance(checks, list) or not checks:
        raise ValueError('Kaynak anlamı incelemesi eksik')
    row_map = {r['id']: r for r in rows}
    field_map = {f['id']: f for f in actual['fields']}
    synthesis_map = {s['id']: s for s in actual['syntheses']}
    finding_map = {f['id']: f for f in data['finding']}
    parties = set()
    for check in checks:
        if not isinstance(check, dict) or check.get('reviewer_kind') != 'agent' or check.get('result') not in ('supported_with_stated_scope', 'documentary_limitation_preserved') or not all(check.get(k) for k in ('id', 'source_reading', 'judgment', 'expansion')):
            raise ValueError('Kaynak anlamı kararı eksik')
        for reviewed in check.get('selected_rows', []):
            row = row_map.get(reviewed.get('id'))
            if not row or any(reviewed.get(k) != v for k, v in row.items()):
                raise ValueError('Kaynak anlamı kararı seçili satırla uyuşmuyor')
            for reviewed_field in reviewed.get('fields', []):
                field = field_map.get(reviewed_field.get('id'))
                if not field or any(reviewed_field.get(k) != v for k, v in field.items()):
                    raise ValueError('Kaynak incelemesi seçili alanla uyuşmuyor')
                if reviewed_field.get('summary') != finding_map[field['summary_finding_id']]['text']:
                    raise ValueError('Kaynak incelemesi özetle uyuşmuyor')
            parties.add(row['party_id'])
        for reviewed_claim in check.get('inspected_synthesis', []):
            claim = synthesis_map.get(reviewed_claim.get('id'))
            if not claim or any(reviewed_claim.get(k) != v for k, v in claim.items()):
                raise ValueError('Kaynak incelemesi sentezle uyuşmuyor')
    if parties != {p['party_id'] for p in data['scope_party']}:
        raise ValueError('Kaynak anlamı örneklemi bütün partileri kapsamıyor')
    coverage = proof.get('coverage_review')
    if not isinstance(coverage, dict) or not isinstance(coverage.get('parties'), list) or not isinstance(coverage.get('semantic_packages'), list):
        raise ValueError('Paketlerin kaynak inceleme izi eksik')
    party_coverage = {p.get('party_id'): p for p in coverage['parties']}
    if set(party_coverage) != parties:
        raise ValueError('Parti kapsam incelemesi eksik')
    for party, item in party_coverage.items():
        selected_rows = [r for r in rows if r['party_id'] == party]
        ids = {r['id'] for r in selected_rows}
        if item.get('row_count') != len(selected_rows) or item.get('topic_count') != len({r['topic_id'] for r in selected_rows}) or item.get('field_count') != sum(f['row_id'] in ids for f in actual['fields']):
            raise ValueError('Parti kapsam incelemesi seçili kayıtlarla uyuşmuyor')
    field_reviews = {r['subject_id'] for r in data.get('comparison_semantic_review', [])
                     if r['subject_kind'] == 'comparison_field' and r['reviewer_kind'] == 'agent'
                     and r['result'] == 'reviewed' and r['reason'] and r['reviewed_at']}
    reviewed_pairs = {(f['summary_finding_id'], f['quote_finding_id']) for f in data['comparison_field'] if f['id'] in field_reviews}
    finding_reviews = {r['subject_id'] for r in data.get('review', [])
                       if r['kind'] == 'finding' and r['reviewer_kind'] == 'agent'
                       and r['result'] == 'reviewed' and r['reason'] and r['reviewed_at']}
    for field in actual['fields']:
        pair = (field['summary_finding_id'], field['quote_finding_id'])
        if field['id'] not in field_reviews and pair not in reviewed_pairs and not set(pair) <= finding_reviews:
            raise ValueError('Seçili alanın kaynak anlamı inceleme izi eksik')
    packages = coverage['semantic_packages']
    if not packages or any(not p.get('path') or not p.get('sha256') or p.get('invalid_decisions') or not p.get('original_review_time_range') for p in packages):
        raise ValueError('Önceki anlam kararlarının kökeni eksik')
    return True


def validate_comparisons(data):
    """Validate ownership and the evidence contract for every comparison."""
    contracts = data.get('comparison_contract', [])
    if not contracts:
        if any(data.get(n) for n in COMPARISON_TABLES if n != 'comparison_contract'):
            raise ValueError('Karşılaştırma sözleşmesi eksik')
        return True
    if len(contracts) != 1 or contracts[0]['version'] not in (1, 2, 3) or contracts[0]['stage'] not in ('tracer', 'partial', 'complete'):
        raise ValueError('Karşılaştırma sözleşmesi geçersiz')
    contract = contracts[0]
    validate_completion(data)
    active_row_ids = None
    synthesis_projections = {}
    if data.get('comparison_completion_revision'):
        active_revision = max(data['comparison_completion_revision'], key=lambda r: r['epoch'])
        active_row_ids = {row['id'] for row in json.loads(active_revision['selection'])['rows']}
        for revision in sorted(data['comparison_completion_revision'], key=lambda r: r['epoch']):
            selection = json.loads(revision['selection'])
            projected = dict(data, comparison_row=selection['rows'], comparison_field=selection['fields'])
            for synthesis in selection['syntheses']:
                synthesis_projections[synthesis['id']] = projected
    if contract['version'] >= 2 and contract['taxonomy_version'] < 3:
        raise ValueError('Sentez sözleşmesi seçili sözlük sürümü 3 gerektirir')
    topics = {(t['topic_id'], t['taxonomy_version']): t for t in data['comparison_topic']}
    if not topics: raise ValueError('En az bir karşılaştırma konusu gerekli')
    rows = {r['id']: r for r in data['comparison_row']}
    parties = {p['party_id'] for p in data['scope_party']}
    versions = {v['id']: v for v in data['document_version']}
    documents = {d['id']: d for d in data['document']}
    passages = {p['id']: p for p in data['passage']}
    findings = {f['id']: f for f in data['finding']}
    attribution = {a['version_id']: a for a in data.get('source_attribution', [])}
    attrs = set(attribution)
    evidence = data['finding_evidence']
    scopes = {s['id']: s for s in data['comparison_review_scope']}
    missing = {m['id']: m for m in data.get('missing', [])}
    attempts = {a['id']: a for a in data.get('attempt', [])}
    all_inventory = data.get('comparison_source_inventory', [])
    if any(type(item['taxonomy_version']) is not int or item['taxonomy_version'] < 1 or item['taxonomy_version'] > contract['taxonomy_version'] for item in all_inventory):
        raise ValueError('Kaynak envanteri sürümü geçersiz')
    inventory = [item for item in all_inventory if item['taxonomy_version'] == contract['taxonomy_version']]
    coverage = set()
    for item in inventory:
        if item['party_id'] not in parties or item['source_role'] not in ('charter','program','supplement','historical') or not all(item[k] for k in ('section','scanned_at','search_boundary')) or item['full_text_available'] not in (0,1):
            raise ValueError('Kaynak envanteri kapsamı geçersiz')
        try:
            matched, unmatched = json.loads(item['topic_ids']), json.loads(item['unmatched_headings'])
        except (TypeError, ValueError):
            raise ValueError('Kaynak envanteri konu listeleri geçersiz')
        if not isinstance(matched, list) or not isinstance(unmatched, list) or any(not isinstance(t, str) or not t for t in matched + unmatched):
            raise ValueError('Kaynak envanteri konu listeleri geçersiz')
        if any((t, item['taxonomy_version']) not in topics for t in matched):
            raise ValueError('Kaynak envanteri bilinmeyen konuya bağlanamaz')
        if item['full_text_available']:
            version = versions.get(item['version_id'])
            if not version or documents[version['document_id']]['party_id'] != item['party_id'] or item['version_id'] not in attrs or item['missing_id']:
                raise ValueError('Envanterdeki metin kaynakla uyuşmuyor')
            if item['source_role'] in ('charter','program'):
                title = documents[version['document_id']]['title'].lower()
                terms = ('tüzük','tüzüğü') if item['source_role'] == 'charter' else ('program',)
                if attribution[item['version_id']]['kind'] != 'party_publication' or not any(term in title for term in terms):
                    raise ValueError('Envanter belge türü kaynakla uyuşmuyor')
            if contract['stage'] == 'complete' and not matched:
                raise ValueError('Tam envanterde metin konusu gerekli')
        else:
            m = missing.get(item['missing_id'])
            if item['version_id'] or not m or m['party_id'] != item['party_id'] or m['heading'] != {'charter':'Tüzük','program':'Program'}.get(item['source_role']):
                raise ValueError('Elde olmayan belge ortak eksik kaydına bağlanmalı')
            attempt = attempts.get(m['attempt_id'])
            valid_attempts = {'Bulunamadı':('search','no_result'), 'Erişilemedi':('access','failure'), 'Doğrulanamadı':('verification','inconclusive')}
            if not attempt or any(attempt[k] != m[k] for k in ('party_id','heading','topic_id')) or valid_attempts.get(m['status']) != (attempt['type'],attempt['result']):
                raise ValueError('Envanter belge açığı geçerli araştırma kaydı gerektirir')
        if contract['stage'] == 'complete' and unmatched:
            raise ValueError('Tam envanterde eşleşmemiş başlık olamaz')
        if item['source_role'] in ('charter','program'):
            coverage.add((item['party_id'],item['source_role']))
    if contract['stage'] == 'complete' and coverage != {(party, role) for party in parties for role in ('charter','program')}:
        raise ValueError('Tam karşılaştırma bütün partilerin belge envanterini gerektirir')
    seen = set()
    positions = set()
    for key, topic in topics.items():
        if key[1] > contract['taxonomy_version'] or not all(topic[k] for k in ('domain', 'definition', 'applicable_levels', 'basis_kind')):
            raise ValueError('Karşılaştırma konusu geçersiz')
        if key[1] >= 2:
            dictionary_topic = next((t for t in data.get('topic', []) if (t['id'], t['taxonomy_version']) == key), None)
            bases = [b for b in data.get('topic_basis', []) if (b['topic_id'], b['taxonomy_version']) == key]
            if not dictionary_topic or dictionary_topic['status'] != 'verified' or not bases:
                raise ValueError('Karşılaştırma konusu doğrulanmış kaynak dayanağı gerektirir')
            if any(b.get('source_role') not in ('charter','program','supplement','historical') or b['passage_id'] not in passages or passages[b['passage_id']]['version_id'] not in attrs or not b['rationale'] for b in bases):
                raise ValueError('Karşılaştırma konusu atıflı ve türü belirtilmiş dayanak gerektirir')
        position = (topic['taxonomy_version'],topic['parent_topic_id'],topic['order_index'])
        if position in positions or not isinstance(topic['order_index'], int) or topic['order_index'] < 0: raise ValueError('Konu sırası geçersiz')
        positions.add(position)
        parent, visited = topic['parent_topic_id'], {topic['topic_id']}
        while parent:
            if parent in visited or (parent,topic['taxonomy_version']) not in topics: raise ValueError('Konu üst hiyerarşisi geçersiz')
            visited.add(parent)
            parent = topics[parent,topic['taxonomy_version']]['parent_topic_id']
        topic_rows = [r for r in rows.values() if (r['topic_id'],r['taxonomy_version']) == key and
                      (active_row_ids is None or r['taxonomy_version'] != contract['taxonomy_version'] or r['id'] in active_row_ids)]
        active = key[1] == contract['taxonomy_version']
        if active and contract['stage'] in ('tracer','complete') and {r['party_id'] for r in topic_rows} != parties: raise ValueError('Konu kapsamındaki tüm partiler gerekli')
        if active and contract['stage'] == 'tracer' and sum(r['state'] == 'evidence' for r in topic_rows) < 2: raise ValueError('Tracer iki kaynaklı yanıt gerektirir')
        if active and contract['stage'] == 'complete' and any(r['state'] == 'not_researched' for r in topic_rows): raise ValueError('Tam aşamada incelenmemiş kayıt olamaz')
        if active and contract['stage'] in ('tracer','complete') and not any((s['topic_id'],s['taxonomy_version']) == key for s in data['comparison_synthesis']): raise ValueError('Konu özeti gerekli')
    for row in rows.values():
        key = (row['topic_id'],row['taxonomy_version'],row['party_id'],row['level'],row['organ'],row['version_id'],row['alternative_group'],row['source_role'])
        selected = active_row_ids is None or row['taxonomy_version'] != contract['taxonomy_version'] or row['id'] in active_row_ids
        if selected:
            if key in seen: raise ValueError('Yinelenen karşılaştırma kaydı')
            seen.add(key)
        if (row['topic_id'],row['taxonomy_version']) not in topics or row['party_id'] not in parties or not row['level'] or not row['organ'] or not row['selection_reason']:
            raise ValueError('Karşılaştırma kaydı eksik')
        if row['source_role'] not in ('program','charter','supplement','historical') or row['state'] not in ('evidence','no_explicit_statement','document_missing','not_researched'):
            raise ValueError('Karşılaştırma durumu geçersiz')
        version = versions.get(row['version_id'])
        if version and (documents[version['document_id']]['party_id'] != row['party_id'] or row['version_id'] not in attrs):
            raise ValueError('Karşılaştırma sürümü veya atfı partiyle uyuşmuyor')
        if version:
            doc = documents[version['document_id']]
            title = doc['title'].casefold()
            if row['source_role'] == 'charter' and not any(x in title for x in ('tüzük','tüzüğü')): raise ValueError('Tüzük kaynağı açıkça tanımlanmalı')
            if row['source_role'] == 'program' and 'program' not in title: raise ValueError('Program kaynağı açıkça tanımlanmalı')
        if row['version_id'] and not version: raise ValueError('Karşılaştırma sürümü yok')
        fields = [f for f in data['comparison_field'] if f['row_id'] == row['id']]
        if row['state'] == 'evidence' and (not version or not fields): raise ValueError('Kaynaklı satır için sürüm ve alan gerekli')
        if row['state'] != 'evidence' and fields: raise ValueError('Kanıtsız satırda bulgu alanı olamaz')
        if row['state'] == 'no_explicit_statement':
            scope = scopes.get(row['scope_id'])
            if not scope or scope['party_id'] != row['party_id'] or scope['version_id'] != row['version_id'] or not all(scope[k] for k in ('sections','query_terms','reviewed_at','result','reason')):
                raise ValueError('Açık ifade yokluğu için incelenen kapsam gerekli')
            if row['taxonomy_version'] >= 3 and scope['result'] != 'no_explicit_statement':
                raise ValueError('Açık ifade yokluğu incelenmemiş kapsamla kapatılamaz')
        if row['state'] == 'document_missing':
            m = missing.get(row['missing_id'])
            a = attempts.get(m['attempt_id']) if m else None
            valid_attempts = {'Bulunamadı':('search','no_result'), 'Erişilemedi':('access','failure'), 'Doğrulanamadı':('verification','inconclusive')}
            if not m or m['party_id'] != row['party_id'] or not m['reason'] or not a or any(a[k] != m[k] for k in ('party_id','heading','topic_id')) or valid_attempts.get(m['status']) != (a['type'],a['result']):
                raise ValueError('Belge eksikliği girişimli eksik kaydı gerektirir')
            if row['taxonomy_version'] >= 3 and m['heading'] != {'charter': 'Tüzük', 'program': 'Program'}.get(row['source_role']):
                raise ValueError('Belge açığı aynı türde kaynak aramasına bağlanmalı')
        if row['state'] == 'not_researched' and any(row[k] for k in ('version_id','scope_id','missing_id')):
            raise ValueError('İncelenmemiş kayıt belge sonucu içeremez')
        for field in fields:
            if field['field'] not in ('charter_answer','principle','target','instrument'): raise ValueError('Karşılaştırma alanı geçersiz')
            if field['field'] == 'charter_answer' and row['source_role'] not in ('charter','supplement','historical'): raise ValueError('Tüzük yanıtı belge türüyle uyuşmuyor')
            if field['field'] in ('principle','target','instrument') and row['source_role'] not in ('program','supplement','historical'): raise ValueError('Program alanı belge türüyle uyuşmuyor')
            summary, quote = findings.get(field['summary_finding_id']), findings.get(field['quote_finding_id'])
            if not summary or not quote or summary['party_id'] != row['party_id'] or quote['party_id'] != row['party_id'] or summary['provenance'] != 'summary' or quote['provenance'] != 'quote' or summary['pair_id'] != quote['pair_id'] or summary['heading'] != quote['heading'] or summary['epistemic_type'] != quote['epistemic_type']:
                raise ValueError('Aynı partiye ait özet ve alıntı çifti gerekli')
            for finding in (summary, quote):
                ev = [e for e in evidence if e['finding_id'] == finding['id']]
                if not ev or any(passages[e['passage_id']]['version_id'] != row['version_id'] for e in ev):
                    raise ValueError('Alan kanıtı sürümle uyuşmuyor')
            if not ({e['passage_id'] for e in evidence if e['finding_id'] == summary['id']} & {e['passage_id'] for e in evidence if e['finding_id'] == quote['id']}):
                raise ValueError('Özet ve alıntı ortak pasaj gerektirir')
    groups = {}
    for row in rows.values():
        if row['alternative_group'] and (active_row_ids is None or row['taxonomy_version'] != contract['taxonomy_version'] or row['id'] in active_row_ids):
            groups.setdefault((row['taxonomy_version'], row['alternative_group']), []).append(row)
    for group in groups.values():
        keys = {(r['topic_id'], r['taxonomy_version'], r['party_id'], r['level'], r['organ'], r['source_role']) for r in group}
        version_ids = {r['version_id'] for r in group}
        if len(group) < 2 or len(keys) != 1 or None in version_ids or len(version_ids) != len(group) or any(r['state'] != 'evidence' for r in group):
            raise ValueError('Alternatifler aynı konuya ait en az iki kaynaklı sürüm gerektirir')
        if len({versions[v]['document_id'] for v in version_ids}) != 1:
            raise ValueError('Alternatifler aynı belgenin sürümleri olmalı')
    for change in data['comparison_change']:
        row = rows[change['row_id']]
        for key in ('before_passage_id','after_passage_id'):
            p = passages[change[key]]
            v = versions[p['version_id']]
            if documents[v['document_id']]['party_id'] != row['party_id'] or v['id'] not in attrs:
                raise ValueError('Değişiklik kanıtı parti veya atıfla uyuşmuyor')
        if change['before_passage_id'] == change['after_passage_id'] or not change['summary'] or not change['order_basis']:
            raise ValueError('Değişiklik öncesi ve sonrası gerekli')
        before = versions[passages[change['before_passage_id']]['version_id']]
        after = versions[passages[change['after_passage_id']]['version_id']]
        if before['id'] == after['id'] or before['document_id'] != after['document_id']:
            raise ValueError('Değişiklik aynı belgenin iki ayrı sürümünü gerektirir')
        if before['sha256'] == after['sha256']:
            raise ValueError('Aynı içerik maddi değişiklik olarak gösterilemez')
    typed_synthesis_ids = {r.get('subject_id') for r in data.get('comparison_semantic_review', [])
                           if r.get('subject_kind') == 'comparison_synthesis'
                           and r.get('reviewer_kind') == 'agent'}
    for synthesis in data['comparison_synthesis']:
        if (synthesis['topic_id'],synthesis['taxonomy_version']) not in topics or not synthesis['text']:
            raise ValueError('Konu özeti geçersiz')
        # A typed author's review belongs to the claim, not to whichever
        # taxonomy is currently selected. Earlier contract-1 claims without
        # such a review retain their original two-owner validation below.
        typed_review = synthesis['id'] in typed_synthesis_ids
        if contract['version'] >= 2 and (synthesis['taxonomy_version'] == contract['taxonomy_version']
                                         or (synthesis['taxonomy_version'] >= 3 and typed_review)):
            validate_synthesis_v2(synthesis_projections.get(synthesis['id'], data), synthesis)
            continue
        ids = [e['passage_id'] for e in data['comparison_synthesis_evidence'] if e['synthesis_id'] == synthesis['id']]
        owners = {documents[versions[passages[p]['version_id']]['document_id']]['party_id'] for p in ids}
        if len(owners) < 2: raise ValueError('Konu özeti çok partili kanıt gerektirir')
        valid_ids = {e['passage_id'] for row in rows.values() if (row['topic_id'],row['taxonomy_version']) == (synthesis['topic_id'],synthesis['taxonomy_version']) for f in data['comparison_field'] if f['row_id'] == row['id'] for e in evidence if e['finding_id'] in (f['summary_finding_id'],f['quote_finding_id'])}
        if not set(ids) <= valid_ids: raise ValueError('Konu özeti kanıtı konu alanına bağlanmalı')
    return True


def validate_comparison_descent(base, candidate):
    """Keep previously published comparison evidence across refreshes."""
    old_contracts = base.get('comparison_contract', [])
    if any(row not in candidate.get('comparison_completion', []) for row in base.get('comparison_completion', [])):
        raise ValueError('Önceki kaynak kapanışı kaldırılamaz veya değiştirilemez')
    for name, keys in (('comparison_completion_basis', ('id',)),
                       ('comparison_coverage_disposition', ('basis_id', 'cell_id')),
                       ('comparison_completion_revision', ('id',)),
                       ('comparison_completion_supersession', ('revision_id', 'old_cell_id', 'new_cell_id'))):
        retained = {tuple(item[k] for k in keys): item for item in candidate.get(name, [])}
        if any(retained.get(tuple(item[k] for k in keys)) != item for item in base.get(name, [])):
            raise ValueError('Önceki kaynak kapanışı kaydı değiştirilemez: ' + name)
    if not old_contracts:
        return True
    new_contracts = candidate.get('comparison_contract', [])
    if len(new_contracts) != 1: raise ValueError('Önceki karşılaştırma sözleşmesi kaldırılamaz')
    old, new = old_contracts[0], new_contracts[0]
    stages = {'tracer':0,'partial':1,'complete':2}
    revisions = candidate.get('comparison_completion_revision', [])
    base_revisions = base.get('comparison_completion_revision', [])
    advanced = bool(revisions and (not base_revisions or max(r['epoch'] for r in revisions) > max(r['epoch'] for r in base_revisions)))
    if base.get('comparison_completion') and not revisions and (
            old != new or completion_selection(base, old['taxonomy_version']) != completion_selection(candidate, old['taxonomy_version'])):
        raise ValueError('Önceki kaynak kapanışından değişiklik yeni revizyon gerektirir')
    if revisions:
        validate_completion_revisions(candidate)
    if (old['version'], new['version']) not in ((1,1), (1,2), (1,3), (2,2), (2,3), (3,3)) or (new['version'] >= 2 and new['taxonomy_version'] < 3) or new['taxonomy_version'] < old['taxonomy_version'] or (stages[new['stage']] < stages[old['stage']] and not advanced):
        raise ValueError('Karşılaştırma sözleşmesi geriletilemez')
    if new['version'] == 3:
        if new['taxonomy_version'] > old['taxonomy_version'] + 1:
            raise ValueError('Satır soyu sözlüğü tabanın hemen sonraki sürümü olmalı')
        if old['version'] < 3:
            markers = candidate.get('comparison_lineage_contract', [])
            expected = {'version': 1, 'first_taxonomy_version': old['taxonomy_version'] + 1}
            if new['taxonomy_version'] != old['taxonomy_version'] + 1 or markers != [expected]:
                raise ValueError('Satır soyu başlangıcı önceki sözlük tabanıyla uyuşmuyor')
    for name in COMPARISON_TABLES:
        if name in ('comparison_contract','comparison_row'): continue
        if any(row not in candidate.get(name, []) for row in base.get(name, [])):
            raise ValueError('Önceki karşılaştırma kaydı değiştirilemez: ' + name)
    if any(row not in candidate.get('comparison_source_inventory', []) for row in base.get('comparison_source_inventory', [])):
        raise ValueError('Önceki kaynak envanteri kaydı değiştirilemez')
    for name in LINEAGE_TABLES:
        if any(row not in candidate.get(name, []) for row in base.get(name, [])):
            raise ValueError('Önceki satır soyu kaydı değiştirilemez: ' + name)
    new_rows = {r['id']: r for r in candidate['comparison_row']}
    for row in base.get('comparison_row', []):
        current_row = new_rows.get(row['id'])
        if current_row == row: continue
        if not current_row or row['state'] != 'not_researched' or current_row['state'] not in ('evidence','no_explicit_statement','document_missing') or any(row[k] != current_row[k] for k in ('id','topic_id','taxonomy_version','party_id','level','organ')):
            raise ValueError('Önceki karşılaştırma satırı değiştirilemez')
    fids = {f[k] for f in base.get('comparison_field', []) for k in ('summary_finding_id','quote_finding_id') if f[k]}
    old_evidence = [e for e in base.get('finding_evidence', []) if e['finding_id'] in fids]
    pids = {e['passage_id'] for e in old_evidence}
    pids.update(e['passage_id'] for e in base.get('comparison_synthesis_evidence', []))
    pids.update(c[k] for c in base.get('comparison_change', []) for k in ('before_passage_id','after_passage_id'))
    for name, old_rows in (('finding',[f for f in base['finding'] if f['id'] in fids]), ('finding_evidence',old_evidence), ('passage',[p for p in base['passage'] if p['id'] in pids])):
        if any(row not in candidate.get(name, []) for row in old_rows): raise ValueError('Önceki karşılaştırma kanıtı değiştirilemez: ' + name)
    return True


def open_workspace(scratch=None, fail_at=None):
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
            if name in DOSSIER_TABLES or name in POLICY_TABLES or name in VIEW_TABLES: continue
            db.execute(f'CREATE TABLE IF NOT EXISTS {name} ({definition})')
        columns = {r['name'] for r in db.execute('PRAGMA table_info(document_version)')}
        for column in ('date_precision', 'date_unknown_reason'):
            if column not in columns:
                db.execute(f'ALTER TABLE document_version ADD COLUMN {column} TEXT')
        if 'date_precision' not in columns:
            db.execute("UPDATE document_version SET date_precision=CASE WHEN document_date IS NULL THEN 'unknown' ELSE 'day' END, date_unknown_reason=CASE WHEN document_date IS NULL THEN 'Belge tarihi kaynakta belirtilmemiş veya doğrulanmamış.' ELSE NULL END")
        if 'number_format' not in {r['name'] for r in db.execute('PRAGMA table_info(financial)')}:
            db.execute('ALTER TABLE financial ADD COLUMN number_format TEXT')
        db.commit()
        migrate_workspace(db, work / 'pre-migration.sqlite3', fail_at=fail_at)
        db.close()
        (work / 'workspace.json').write_text(json.dumps({'base': base, 'token': token}), encoding='utf-8')
        return work
    except Exception:
        lock.unlink(missing_ok=True)
        raise


def record(work, kind, values):
    if kind not in TABLES or not isinstance(values, dict) or not values:
        raise ValueError('Geçersiz kayıt türü veya yükü')
    if kind == 'party_identity_revision': raise ValueError('Kimlik geçişi yalnız sicil doğrulamasıyla yapılabilir')
    if kind == 'source_policy': raise ValueError('Kaynak politikası yalnız sürümlü migration ile belirlenir')
    assert_lock(work)
    if kind == 'match': return record_match(work, values)
    if kind == 'financial': return record_financial(work, values)
    if kind == 'match_candidate': return insert_checked(work, kind, values, check_candidate)
    if kind == 'source_attribution': return insert_checked(work, kind, values, check_attribution)
    if kind == 'missing_resolution': return insert_checked(work, kind, values, check_unlinked_resolution)
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
        if kind == 'archive_view':
            validate_view(DATA,values)
            version=db.execute('SELECT sha256 FROM document_version WHERE id=?',(values['version_id'],)).fetchone()
            if not version or version['sha256']!=values['source_sha256']:raise ValueError('Arşiv görünümü özgün belgeyle uyuşmuyor')
        if kind == 'edge':
            if values.get('relation') not in ('reference','contradiction','new_version') or not values.get('relevance_reason'): raise ValueError('İlgili kenar ve gerekçe gerekli')
        if kind == 'research_state' and values.get('state') not in ('not_researched','in_progress','reviewed'):
            raise ValueError('Geçersiz araştırma durumu')
        if kind == 'report_option' and values != {'name': 'chain_links', 'value': '1'}:
            raise ValueError('Geçersiz rapor seçeneği')
        if kind == 'topic_query' and (values.get('actor_kind') not in ('institutional','authorized','individual') or not values.get('query')):
            raise ValueError('Konu sorgusu ve aktör türü gerekli')
        if kind in ('topic_search', 'url_alias'):
            raise ValueError('Durum ve takma adlar ilgili işlem tarafından yönetilir')
        if kind == 'identity_observation':
            check_identity(db, values)
        if kind == 'method':
            raise ValueError('Yöntem kesimi freeze komutuyla kaydedilir')
        if kind == 'event_date':
            method = db.execute('SELECT cutoff_at FROM method ORDER BY version DESC LIMIT 1').fetchone()
            if not method:
                raise ValueError('Önce yöntem kesimi dondurulmalı')
            owner = db.execute('SELECT d.party_id FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (values.get('passage_id'),)).fetchone()
            if not owner or owner['party_id'] != values.get('party_id'):
                raise ValueError('Olay kanıtı partiyle uyuşmuyor')
            foundation = foundation_for_party(db, values.get('party_id'))
            status = validate_dates(values.get('event_at'), values.get('date_precision'), foundation, method['cutoff_at'], values.get('date_unknown_reason'))
            if status == 'outside' or values.get('scope_status') != status:
                raise ValueError('Olay dönem dışında veya belirsizlik yanlış belirtilmiş')
        if kind == 'accounting_period':
            check_accounting_period(db, values)
        keys = list(values)
        db.execute(f"INSERT INTO {kind} ({','.join(keys)}) VALUES ({','.join('?' for _ in keys)})", [values[k] for k in keys])
        if kind == 'document_version':
            db.execute('INSERT OR IGNORE INTO url_alias VALUES (?,?,?)', (values['original_url'], values['final_url'], values['id']))
            owner = db.execute('SELECT party_id FROM document WHERE id=?', (values['document_id'],)).fetchone()
            for lead in db.execute("SELECT l.id,l.topic_id,l.normalized_url FROM lead l JOIN topic_search t ON t.topic_id=l.topic_id WHERE t.state='closed' AND l.party_id=? AND l.normalized_url=?", (owner['party_id'], normalize_url(values['original_url']))).fetchall():
                earlier = db.execute('SELECT v.original_url,v.final_url,v.sha256 FROM document_version v JOIN document d ON d.id=v.document_id WHERE d.party_id=? AND v.id<>? ORDER BY v.rowid DESC', (owner['party_id'], values['id'])).fetchall()
                previous = next((v for v in earlier if lead['normalized_url'] in (normalize_url(v['original_url']), normalize_url(v['final_url']))), None)
                if previous and previous['sha256'] == values['sha256']:
                    continue
                closure = db.execute('SELECT id FROM closure WHERE topic_id=? ORDER BY rowid DESC LIMIT 1', (lead['topic_id'],)).fetchone()
                reason = 'Aynı adreste yeni içerik sürümü' if previous else 'Uç için ilk kaynak yakalaması'
                db.execute('INSERT OR IGNORE INTO reopen VALUES (?,?,?,?)', (closure['id'],lead['id'],values['accessed_at'],reason))
                db.execute("UPDATE topic_search SET state='in_progress' WHERE topic_id=?", (lead['topic_id'],))
                db.execute("UPDATE lead SET status='pending' WHERE id=?", (lead['id'],))
        if kind in DOSSIER_TABLES:
            payload = {name: [dict(row) for row in db.execute(f'SELECT * FROM {name}')] for name in TABLES}
            validate_dossier(payload)
        db.commit()
        if kind == 'document_version': return values['id']
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


def check_examined_lead(db, lead, version_id):
    version = db.execute('SELECT v.original_url,v.final_url,d.party_id FROM document_version v JOIN document d ON d.id=v.document_id WHERE v.id=?', (version_id,)).fetchone()
    if not version or version['party_id'] != lead['party_id']:
        raise ValueError('İncelenen kaynak uç partisine ait değil')
    urls = {normalize_url(version['original_url']), normalize_url(version['final_url'])}
    # Historical aliases may have been created by hash deduplication rather
    # than a redirect; only the capture's own endpoints establish access.
    if normalize_url(lead['url']) not in urls:
        raise ValueError('İncelenen kaynak adresi uçla uyuşmuyor')


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
            if state == 'examined': check_examined_lead(db, lead, v['source_version_id'])
            if state: db.execute('UPDATE lead SET status=? WHERE id=?', (state,v['lead_id']))
    insert_checked(work, 'attempt', values, validate)


def check_document_authority(db, v):
    target = db.execute('SELECT d.party_id,v.final_url FROM document_version v JOIN document d ON d.id=v.document_id WHERE v.id=?', (v['version_id'],)).fetchone()
    source = db.execute('SELECT p.exact,d.party_id,d.source_kind,v.final_url FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (v['authority_passage_id'],)).fetchone()
    attempt = db.execute('SELECT * FROM attempt WHERE id=?', (v['verification_attempt_id'],)).fetchone()
    identity = db.execute("SELECT p.exact,v.final_url FROM identity_observation i JOIN passage p ON p.id=i.passage_id JOIN document_version v ON v.id=p.version_id WHERE i.entity_id=? AND i.entity_kind='party'", (v['registry_party_id'],)).fetchone()
    party = db.execute('SELECT legal_name FROM party WHERE id=?', (v['registry_party_id'],)).fetchone()
    if not target or not source or not attempt or not identity or not party or not v.get('reason') or v.get('status') != 'verified': raise ValueError('Otorite zinciri eksik')
    host = urllib.parse.urlsplit(target['final_url']).hostname or ''
    source_host = urllib.parse.urlsplit(source['final_url']).hostname or ''
    identity_host = urllib.parse.urlsplit(identity['final_url']).hostname or ''
    if target['party_id'] != v['registry_party_id'] or source['party_id'] != v['registry_party_id'] or source['source_kind'] != 'official' or source_host not in ('tbmm.gov.tr','www.tbmm.gov.tr','cdn.tbmm.gov.tr') or host.removeprefix('www.') not in source['exact'] or identity_host not in ('www.yargitaycb.gov.tr','yargitaycb.gov.tr') or party['legal_name'] not in identity['exact'] or attempt['party_id'] != v['registry_party_id'] or (attempt['type'],attempt['result']) != ('verification','confirmed'):
        raise ValueError('Parti veya resmî otorite zinciri uyuşmuyor')


def verify_document_authority(work, values):
    insert_checked(work, 'document_authority', values, check_document_authority)


def record_topic(work, values):
    def validate(db, v):
        if v.get('status') not in ('candidate','verified') or not v.get('label') or not v.get('change_reason') or not v.get('valid_from') or not isinstance(v.get('taxonomy_version'), int) or v['taxonomy_version'] < 1:
            raise ValueError('Konu sürümü ve gerekçesi gerekli')
    insert_checked(work, 'topic', values, validate)


def check_match(db, v):
    required = ('id', 'topic_id', 'statement_finding_id', 'action_finding_id', 'relation', 'rationale', 'eligibility', 'reviewed_at')
    if any(not v.get(k) for k in required): raise ValueError('Eşleşme ve gerekçe alanları gerekli')
    if v['relation'] not in ('benzerlik', 'farklılık', 'belirlenemiyor') or v['eligibility'] != 'eligible':
        raise ValueError('Geçersiz eşleşme durumu')
    if dt.datetime.fromisoformat(v['reviewed_at'].replace('Z', '+00:00')).tzinfo is None: raise ValueError('İnceleme zamanı saat dilimi içermeli')
    if v['eligibility'] != 'eligible' and not v.get('exclusion_reason'): raise ValueError('Dışlama gerekçesi gerekli')
    s = db.execute('SELECT * FROM finding WHERE id=?', (v['statement_finding_id'],)).fetchone()
    a = db.execute('SELECT f.*,a.actor_id,a.event_date,a.date_precision,a.occurrence_passage_id,a.context,ac.kind,ac.person_id,ac.authorization_passage_id,ac.party_id AS actor_party FROM action a JOIN finding f ON f.id=a.finding_id JOIN actor ac ON ac.id=a.actor_id WHERE a.finding_id=?', (v['action_finding_id'],)).fetchone()
    if not s or not a or s['id'] == a['id'] or s['party_id'] != a['party_id'] or a['party_id'] != a['actor_party'] or not a['context']: raise ValueError('Ayrı ve aynı partiye bağlı bulgular gerekli')
    if a['kind'] not in ('institution', 'authorized_representative', 'individual_mp'): raise ValueError('Aktör türü geçersiz')
    if a['kind'] != 'institution' and not a['person_id']: raise ValueError('Kişi kimliği gerekli')
    if a['kind'] == 'authorized_representative' and not a['authorization_passage_id']: raise ValueError('Temsil yetkisi kanıtı gerekli')
    if a['kind'] == 'authorized_representative':
        authority = db.execute('SELECT d.party_id,p.exact FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (a['authorization_passage_id'],)).fetchone()
        person = db.execute('SELECT name FROM person WHERE id=?', (a['person_id'],)).fetchone()
        if not authority or authority['party_id'] != a['party_id'] or not person or person['name'] not in authority['exact']: raise ValueError('Yetki kanıtı kişi ve partiyle uyuşmuyor')
    if a['kind'] == 'individual_mp' and v['eligibility'] == 'eligible': raise ValueError('Bireysel oy kurumsal uygulama sayılmaz')
    for finding in (s, a):
        if not db.execute("SELECT 1 FROM finding_topic ft JOIN topic t ON t.id=ft.topic_id AND t.taxonomy_version=ft.taxonomy_version WHERE ft.finding_id=? AND ft.topic_id=? AND t.status='verified'", (finding['id'],v['topic_id'])).fetchone(): raise ValueError('Doğrulanmış ortak konu gerekli')
    statement = db.execute("SELECT passage_id FROM finding_evidence WHERE finding_id=? AND role='statement'", (s['id'],)).fetchall()
    occurrence = db.execute("SELECT 1 FROM finding_evidence WHERE finding_id=? AND passage_id=? AND role='occurrence'", (a['id'],a['occurrence_passage_id'])).fetchone()
    if not statement or not occurrence or a['occurrence_passage_id'] in [x[0] for x in statement]: raise ValueError('Ayrı beyan ve oluş kanıtı gerekli')
    for finding_id, passage_id in [(s['id'], row[0]) for row in statement] + [(a['id'], a['occurrence_passage_id'])]:
        reviewed = db.execute("SELECT 1 FROM verification WHERE finding_id=? AND passage_id=? AND result='confirmed' AND reason<>''", (finding_id, passage_id)).fetchone()
        if not reviewed: raise ValueError('Kanıtın açık doğrulama kaydı gerekli')
        evidence = db.execute('SELECT d.party_id FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (passage_id,)).fetchone()
        if not evidence or evidence['party_id'] != s['party_id']: raise ValueError('Kanıt başka partiye ait')
    source = db.execute('SELECT d.source_kind,d.party_id,v.document_date FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (a['occurrence_passage_id'],)).fetchone()
    if not source or source['party_id'] != a['party_id'] or source['source_kind'] == 'party': raise ValueError('Parti duyurusu veya başka parti kaynağı oluş kanıtı olamaz')
    if source['document_date'] and source['document_date'] < a['event_date'][:10]: raise ValueError('Oluş kaynağı olaydan önce yayımlanmış')
    method = db.execute('SELECT cutoff_at FROM method ORDER BY version DESC LIMIT 1').fetchone()
    if not method or validate_dates(a['event_date'], a['date_precision'], '2026-07-24', method['cutoff_at']) != 'inside': raise ValueError('Olay tarihi kapsam dışında veya belirsiz')


def record_match(work, values):
    insert_checked(work, 'match', values, check_match)


def aware_time(value):
    parsed = dt.datetime.fromisoformat((value or '').replace('Z', '+00:00'))
    if parsed.tzinfo is None: raise ValueError('Saat dilimi içeren zaman gerekli')
    return parsed.astimezone(dt.timezone.utc)


def check_candidate(db, v):
    if any(not v.get(k) for k in ('id','party_id','topic_id','status','rationale','reviewed_at')):
        raise ValueError('Aday kimliği, kapsamı ve inceleme gerekçesi gerekli')
    aware_time(v['reviewed_at'])
    if v['status'] not in ('eligible','excluded','unverified') or not (v.get('lead_id') or v.get('passage_id')):
        raise ValueError('Aday durumu ve kaynak ucu veya pasajı gerekli')
    if v.get('lead_id'):
        lead = db.execute('SELECT party_id,topic_id FROM lead WHERE id=?', (v['lead_id'],)).fetchone()
        if not lead or lead['party_id'] != v['party_id'] or lead['topic_id'] != v['topic_id']: raise ValueError('Aday kaynak ucu kapsamla uyuşmuyor')
    if v.get('passage_id'):
        source = db.execute('SELECT d.party_id FROM passage p JOIN document_version dv ON dv.id=p.version_id JOIN document d ON d.id=dv.document_id WHERE p.id=?', (v['passage_id'],)).fetchone()
        if not source or source['party_id'] != v['party_id']: raise ValueError('Aday pasajı partiyle uyuşmuyor')
    if v['status'] == 'eligible':
        m = db.execute('SELECT m.*,f.party_id FROM match m JOIN finding f ON f.id=m.statement_finding_id WHERE m.id=?', (v.get('match_id'),)).fetchone()
        if not m or m['eligibility'] != 'eligible' or m['party_id'] != v['party_id'] or m['topic_id'] != v['topic_id']: raise ValueError('Uygun aday eşleşmeyle uyuşmuyor')
        if v.get('missing_id'):
            resolved = db.execute('SELECT r.passage_id FROM missing_resolution r JOIN missing x ON x.id=r.missing_id WHERE x.id=? AND x.party_id=? AND x.topic_id=?', (v['missing_id'],v['party_id'],v['topic_id'])).fetchone()
            if not resolved or not db.execute('SELECT 1 FROM finding_evidence WHERE passage_id=? AND finding_id IN (?,?)', (resolved['passage_id'],m['statement_finding_id'],m['action_finding_id'])).fetchone(): raise ValueError('Çözümlenen adayın yeni kanıtı eşleşmeyle uyuşmuyor')
    elif v['status'] == 'unverified':
        m = db.execute('SELECT m.*,a.attempted_at FROM missing m JOIN attempt a ON a.id=m.attempt_id WHERE m.id=?', (v.get('missing_id'),)).fetchone()
        if not m or m['party_id'] != v['party_id'] or m['topic_id'] != v['topic_id'] or m['status'] != 'Doğrulanamadı' or v.get('match_id'): raise ValueError('Doğrulanamayan aday eksikle uyuşmuyor')
        if aware_time(v['reviewed_at']) < aware_time(m['attempted_at']) or db.execute('SELECT 1 FROM missing_resolution WHERE missing_id=?', (m['id'],)).fetchone(): raise ValueError('Aday incelemesi eksik zamanı veya çözümüyle uyuşmuyor')
    elif v.get('match_id') or v.get('missing_id'): raise ValueError('Dışlanan aday eşleşme veya eksik taşıyamaz')


def check_missing_resolution(db, v):
    if any(not v.get(k) for k in ('missing_id','resolved_at','passage_id','reason')): raise ValueError('Çözüm zamanı, pasajı ve gerekçesi gerekli')
    m = db.execute('SELECT m.*,a.attempted_at FROM missing m JOIN attempt a ON a.id=m.attempt_id WHERE m.id=?', (v['missing_id'],)).fetchone()
    p = db.execute('SELECT d.party_id FROM passage p JOIN document_version dv ON dv.id=p.version_id JOIN document d ON d.id=dv.document_id WHERE p.id=?', (v['passage_id'],)).fetchone()
    if not m or not p or p['party_id'] != m['party_id'] or aware_time(v['resolved_at']) < aware_time(m['attempted_at']): raise ValueError('Çözümün parti, zaman ve kanıt ilişkisi geçersiz')
    if not db.execute('SELECT 1 FROM finding_topic ft JOIN finding_evidence e ON e.finding_id=ft.finding_id WHERE ft.topic_id=? AND e.passage_id=?', (m['topic_id'],v['passage_id'])).fetchone(): raise ValueError('Çözüm kanıtı eksik konusu ile ilişkilendirilmeli')


def check_unlinked_resolution(db, v):
    check_missing_resolution(db, v)
    if db.execute("SELECT 1 FROM match_candidate WHERE missing_id=? AND status='unverified'", (v['missing_id'],)).fetchone(): raise ValueError('Aday çözümü atomik geçişle yapılmalı')


def resolve_candidate(work, candidate_id, match_id, resolution):
    """Atomically retain the missing history and promote a candidate with evidence."""
    assert_lock(work)
    db = connect(Path(work) / 'records.sqlite3')
    try:
        candidate = db.execute('SELECT * FROM match_candidate WHERE id=?', (candidate_id,)).fetchone()
        if not candidate or candidate['status'] != 'unverified' or candidate['missing_id'] != resolution.get('missing_id'): raise ValueError('Açık aday ve eksik uyuşmuyor')
        check_missing_resolution(db, resolution)
        if aware_time(resolution['resolved_at']) < aware_time(candidate['reviewed_at']): raise ValueError('Çözüm aday incelemesinden önce olamaz')
        candidate = dict(candidate, status='eligible', match_id=match_id, reviewed_at=resolution['resolved_at'], rationale=resolution['reason'])
        match = db.execute('SELECT statement_finding_id,action_finding_id FROM match WHERE id=?', (match_id,)).fetchone()
        if not match or not db.execute('SELECT 1 FROM finding_evidence WHERE passage_id=? AND finding_id IN (?,?)', (resolution['passage_id'],match[0],match[1])).fetchone(): raise ValueError('Çözüm pasajı eşleşmenin kanıtı olmalı')
        db.execute('INSERT INTO missing_resolution VALUES (?,?,?,?)', (resolution['missing_id'],resolution['resolved_at'],resolution['passage_id'],resolution['reason']))
        check_candidate(db, candidate)
        db.execute('UPDATE match_candidate SET status=?,match_id=?,reviewed_at=?,rationale=? WHERE id=?', ('eligible',match_id,resolution['resolved_at'],resolution['reason'],candidate_id))
        db.commit()
    finally: db.close()


def validate_evidence(db, finding, passage, *, validated_policy=None):
    row = db.execute('SELECT d.party_id,d.source_kind,v.id AS version_id FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (passage['id'],)).fetchone()
    if not row or row['party_id'] != finding['party_id']: raise ValueError('Kanıt başka partiye ait')
    if finding['provenance'] == 'quote' and finding['text'] not in passage['exact']: raise ValueError('Alıntı pasajda bulunamadı')
    compiled = check_evidence_attribution(db,finding,row,validated_policy=validated_policy)
    if not compiled and finding['heading'] in ('Tüzük','Program') and not db.execute("SELECT 1 FROM document_authority WHERE version_id=? AND registry_party_id=? AND status='verified'", (row['version_id'],finding['party_id'])).fetchone(): raise ValueError('Belge otoritesi doğrulanmadı')
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
            attempt = db.execute("SELECT * FROM attempt WHERE lead_id=? AND result IN ('examined','failure','excluded') ORDER BY attempted_at DESC LIMIT 1", (lead['id'],)).fetchone()
            expected = {'examined':'examined','blocked':'failure','excluded':'excluded'}[lead['status']]
            if not attempt or not attempt['reason'] or attempt['result'] != expected or (lead['status'] == 'examined' and not attempt['source_version_id']): raise ValueError('Uç gerçek girişimle desteklenmeli')
            if lead['status'] == 'examined': check_examined_lead(db, lead, attempt['source_version_id'])
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


def check_accounting_period(db, v):
    foundation = foundation_for_party(db, v.get('party_id'))
    method = db.execute('SELECT cutoff_at FROM method ORDER BY version DESC LIMIT 1').fetchone()
    owner = db.execute('SELECT d.party_id FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (v.get('passage_id'),)).fetchone()
    if not method or not owner or owner['party_id'] != v.get('party_id'): raise ValueError('Hesap dönemi için partiye ait kaynak ve kesim gerekli')
    start, end = v.get('period_start'), v.get('period_end')
    if not start or not end:
        if v.get('date_precision') != 'unknown' or not v.get('date_unknown_reason'): raise ValueError('Eksik hesap dönemi gerekçesi gerekli')
    elif v.get('date_precision') != 'day' or dt.date.fromisoformat(end) < dt.date.fromisoformat(start):
        raise ValueError('Geçersiz hesap dönemi')
    for value in (start, end):
        if value and validate_dates(value, 'day', foundation, method['cutoff_at']) == 'outside': raise ValueError('Hesap dönemi araştırma dönemi dışında')


def check_financial(db, v):
    required = ('id', 'party_id', 'version_id', 'category', 'currency', 'period_start', 'period_end', 'organization_scope', 'published_at')
    if any(not v.get(k) for k in required): raise ValueError('Mali dönem, kapsam ve kaynak alanları gerekli')
    try:
        start, end, published = (dt.date.fromisoformat(v[k]) for k in ('period_start', 'period_end', 'published_at'))
    except (ValueError, TypeError): raise ValueError('Geçersiz mali tarih')
    foundation = foundation_for_party(db, v['party_id'])
    method = db.execute('SELECT cutoff_at FROM method ORDER BY version DESC LIMIT 1').fetchone()
    source = db.execute('SELECT d.party_id,d.source_kind,v.document_date,p.exact FROM document_version v JOIN document d ON d.id=v.document_id LEFT JOIN passage p ON p.version_id=v.id AND p.id=? WHERE v.id=?', (v.get('passage_id'), v['version_id'])).fetchone()
    if not method or not source or source['party_id'] != v['party_id'] or not source['document_date'] or source['document_date'] != v['published_at'] or start < dt.date.fromisoformat(foundation) or end < start or end >= dt.datetime.fromisoformat(method[0]).date() or published < end:
        raise ValueError('Mali kimlik, dönem veya yayın tarihi uyuşmuyor')
    if not re.fullmatch(r'[A-Z]{3}', v['currency']): raise ValueError('Para birimi gerekli')
    if not db.execute('SELECT 1 FROM accounting_period ap JOIN passage p ON p.id=ap.passage_id WHERE ap.party_id=? AND ap.period_start=? AND ap.period_end=? AND ap.date_precision=? AND p.version_id=?', (v['party_id'],v['period_start'],v['period_end'],'day',v['version_id'])).fetchone(): raise ValueError('Kaynakla ilişkili hesap dönemi gerekli')
    if source['source_kind'] == 'party':
        if active_policy(db):
            attribution = db.execute('SELECT * FROM source_attribution WHERE version_id=?', (v['version_id'],)).fetchone()
            if not attribution: raise ValueError('Mali parti yayını için kaynak atfı gerekli')
            check_attribution(db,dict(attribution))
        elif not db.execute("SELECT 1 FROM document_authority WHERE version_id=? AND registry_party_id=? AND status='verified'", (v['version_id'],v['party_id'])).fetchone(): raise ValueError('Parti kaynağının yetkisi doğrulanmadı')
    if v.get('amount') is None:
        missing = db.execute('SELECT party_id,heading FROM missing WHERE id=?', (v.get('missing_id'),)).fetchone()
        if not missing or missing['party_id'] != v['party_id'] or missing['heading'] != 'Finansman ve harcamalar': raise ValueError('Bilinmeyen tutar girişime bağlı eksik gerektirir')
    else:
        if not isinstance(v['amount'], str) or not re.fullmatch(r'\d+(?:\.\d+)?', v['amount']) or not source['exact'] or v.get('missing_id'): raise ValueError('Mali tutar ondalık metin ve pasaj gerektirir')
        if v['organization_scope'].casefold() not in source['exact'].casefold() or (v['currency'] == 'TRY' and not re.search(r'\b(TL|TRY|lira)\b',source['exact'],re.I)) or (v['currency'] != 'TRY' and v['currency'] not in source['exact']): raise ValueError('Kapsam ve para birimi kaynak pasajında gerekli')
        try: amount = Decimal(v['amount'])
        except InvalidOperation: raise ValueError('Geçersiz tutar')
        if not db.execute("SELECT 1 FROM review WHERE kind='financial' AND subject_id=? AND result='reviewed' AND reviewer_kind IN ('agent','human') AND reviewed_at<>'' AND reason<>''", (v['id'],)).fetchone(): raise ValueError('Mali ifade için kaynak incelemesi gerekli')
        currency = r'(?:TL|TRY|lira)' if v['currency'] == 'TRY' else re.escape(v['currency'])
        clauses = re.split(r'[;\n]|(?<=[.!?])\s+', source['exact'])
        numbers = [n for clause in clauses if v['category'].casefold() in clause.casefold()
                   for n in re.findall(r'(?<![\w.\-])(?<!\d[./-])(\d+(?:[.,]\d+)*)\s*' + currency + r'\b', clause, re.I)]
        fmt = v.get('number_format')
        if fmt not in ('tr', 'canonical'): raise ValueError('Kaynak sayı biçimi tr veya canonical olarak belirtilmeli')
        def numeric(s):
            if fmt == 'tr':
                if not re.fullmatch(r'(?:\d+|[1-9]\d{0,2}(?:\.\d{3})+)(?:,\d+)?', s): return None
                return Decimal(s.replace('.', '').replace(',', '.'))
            if not re.fullmatch(r'\d+(?:\.\d+)?', s): return None
            return Decimal(s)
        if not any(numeric(n) == amount for n in numbers): raise ValueError('Tutar ve para birimi belirtilen sayı biçiminde kaynakta birlikte bulunmalı')


def record_financial(work, values):
    insert_checked(work, 'financial', values, check_financial)


def audit_finance(path):
    db = connect_readonly(path)
    try:
        if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='financial'").fetchone(): raise ValueError('Mali kayıt tablosu yok')
        for row in db.execute('SELECT * FROM financial'): check_financial(db, dict(row))
        states = {r['heading']: r['state'] for r in db.execute("SELECT heading,state FROM research_state WHERE party_id='yeni-parti'")}
        for heading in ('Kuruluş', 'Tüzük', 'Program', 'Söylem ve uygulama', 'Finansman ve harcamalar'):
            if states.get(heading) == 'not_researched' or (heading in ('Söylem ve uygulama', 'Finansman ve harcamalar') and states.get(heading) != 'reviewed'): raise ValueError('Pilot başlığı araştırılmamış: ' + heading)
            if not db.execute('SELECT 1 FROM finding WHERE party_id=? AND heading=? UNION SELECT 1 FROM missing WHERE party_id=? AND heading=? UNION SELECT 1 FROM financial WHERE party_id=? AND ?=? LIMIT 1', ('yeni-parti',heading,'yeni-parti',heading,'yeni-parti',heading,'Finansman ve harcamalar')).fetchone(): raise ValueError('Pilot başlığı boş: ' + heading)
        for row in db.execute("SELECT * FROM missing WHERE heading='Finansman ve harcamalar'"):
            a = db.execute('SELECT * FROM attempt WHERE id=?', (row['attempt_id'],)).fetchone()
            allowed = {'Bulunamadı':('search','no_result'), 'Erişilemedi':('access','failure'), 'Doğrulanamadı':('verification','inconclusive')}
            if not a or any(a[k] != row[k] for k in ('party_id','heading','topic_id')) or allowed.get(row['status']) != (a['type'],a['result']): raise ValueError('Mali eksik girişimi geçersiz')
    finally: db.close()


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


def export_db(path, release_id, strict_identity=False):
    db = connect_readonly(path)
    try:
        if db.execute('PRAGMA integrity_check').fetchone()[0] != 'ok' or db.execute('PRAGMA foreign_key_check').fetchall():
            raise ValueError('Veritabanı bütünlük hatası')
        existing = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        v2_present = existing.intersection(COMPLETION_V2_TABLES)
        has_v2 = any(db.execute(f'SELECT 1 FROM {name} LIMIT 1').fetchone() for name in v2_present)
        if has_v2 and (v2_present != set(COMPLETION_V2_TABLES) or not db.execute('SELECT 1 FROM comparison_completion_revision LIMIT 1').fetchone()):
            raise ValueError('Kaynak kapanışı sürüm 2 şeması veya revizyonu eksik')
        names = [n for n in TABLES if n in existing] if 'scope_party' in existing else list(LEGACY_TABLES)
        present = existing.intersection(COMPARISON_TABLES)
        if present and present != set(COMPARISON_TABLES): raise ValueError('Eksik karşılaştırma şeması')
        has_comparisons = bool(present and db.execute('SELECT 1 FROM comparison_contract').fetchone())
        if has_v2 and not has_comparisons:
            raise ValueError('Kaynak kapanışı karşılaştırma sözleşmesi gerektirir')
        if present and not has_comparisons and any(db.execute(f'SELECT 1 FROM {n} LIMIT 1').fetchone() for n in COMPARISON_TABLES if n != 'comparison_contract'):
            raise ValueError('Karşılaştırma kayıtları için sözleşme işaretçisi gerekli')
        if has_comparisons:
            names += list(COMPARISON_TABLES)
            if 'comparison_source_inventory' in existing: names.append('comparison_source_inventory')
            if 'comparison_completion' in existing and db.execute('SELECT 1 FROM comparison_completion LIMIT 1').fetchone():
                names.append('comparison_completion')
            if has_v2:
                names += list(COMPLETION_V2_TABLES)
            contract_version = db.execute('SELECT version FROM comparison_contract').fetchone()[0]
            if contract_version >= 3:
                if not set(LINEAGE_TABLES) <= existing: raise ValueError('Sürüm 3 satır soyu şeması eksik')
                names += list(LINEAGE_TABLES)
        cols = {r['name'] for r in db.execute('PRAGMA table_info(document_version)')}
        policy = active_policy(db)
        result = {'schema_version': 6 if has_comparisons and policy else (5 if policy else (4 if set(DOSSIER_TABLES).issubset(existing) else (3 if 'date_precision' in cols else (2 if 'scope_party' in existing else 1)))), 'release_id': release_id}
        if has_comparisons and not policy: raise ValueError('Karşılaştırma kaynak politikası gerektirir')
        if existing.intersection(POLICY_TABLES) and (not set(POLICY_TABLES).issubset(existing) or not policy): raise ValueError('Kaynak politikası eksik')
        if existing.intersection(DOSSIER_TABLES) and not set(DOSSIER_TABLES).issubset(existing): raise ValueError('Eksik dosya şeması')
        v2_order = {'comparison_completion_basis': 'id',
                    'comparison_coverage_disposition': 'basis_id,cell_id',
                    'comparison_completion_revision': 'epoch',
                    'comparison_completion_supersession': 'revision_id,old_cell_id,new_cell_id'}
        for name in names:
            order = v2_order.get(name, 'rowid')
            result[name] = [dict(row) for row in db.execute(f'SELECT * FROM {name} ORDER BY {order}')]
        validated_policy = validate_policy(db,result)
        for view in result.get('archive_view',[]):
            validate_view(DATA,view)
            if not any(v['id']==view['version_id'] and v['sha256']==view['source_sha256'] for v in result['document_version']):raise ValueError('Arşiv görünümü özgün belgeyle uyuşmuyor')
        if strict_identity:
            for identity in result.get('identity_observation', []): check_identity(db, identity)
        if result['schema_version'] >= 3:
            versions = {v['id']: v for v in result['document_version']}
            for method in result['method']:
                v = versions[method['cutoff_capture_version_id']]
                if method['cutoff_at'] != v['accessed_at'] or urllib.parse.urlsplit(v['final_url']).hostname not in ('tbmm.gov.tr', 'www.tbmm.gov.tr'):
                    raise ValueError('Kesim kaynak yakalaması ile eşleşmiyor')
            if result['event_date'] and not result['method']: raise ValueError('Olay için yöntem kesimi gerekli')
            for event in result['event_date']:
                method = max(result['method'], key=lambda m: m['version'])
                owner = db.execute('SELECT d.party_id FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id WHERE p.id=?', (event['passage_id'],)).fetchone()
                if not owner or owner['party_id'] != event['party_id']: raise ValueError('Olay kanıtı partiyle uyuşmuyor')
                foundation = foundation_for_party(db, event['party_id'])
                actual = validate_dates(event['event_at'], event['date_precision'], foundation, method['cutoff_at'], event['date_unknown_reason'])
                if actual == 'outside' or actual != event['scope_status']: raise ValueError('Olay kapsamı geçersiz')
            for period in result['accounting_period']:
                check_accounting_period(db, period)
        if any(not any(e['finding_id'] == f['id'] for e in result['finding_evidence']) for f in result['finding']):
            raise ValueError('Kanıtsız bulgu')
        if any(not any(e['comparison_id'] == c['id'] for e in result['comparison_evidence']) for c in result['comparison']):
            raise ValueError('Kanıtsız karşılaştırma')
        for v in result['document_version']:
            safe_url(v['original_url']); safe_url(v['final_url'])
            original = safe_path(DATA, v['original_path']); readable = safe_path(DATA, v['readable_path'])
            if sha(original) != v['sha256']:
                raise ValueError('Arşiv özeti eşleşmiyor')
            kind = 'pdf' if original.name == 'original.pdf' else 'html'
            raw=original.read_bytes()
            acceptable=[readable_bytes(raw,kind)]
            try: acceptable.append(readable_bytes(raw,kind,legacy=False))
            except ValueError: pass # Historical derivatives retain their original bytes.
            if readable.read_bytes() not in acceptable:
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
            else:
                raw=path.read_bytes()
                content=html_source_text(raw)
                if p['exact'] not in content and safe_path(DATA,v['readable_path']).read_bytes()==readable_bytes(raw,'html'):
                    content=raw.decode('utf-8',errors='replace')
            if p['exact'] not in content:
                raise ValueError('Pasaj özgün belgede bulunamadı')
        for f in result['finding']:
            if f['provenance'] == 'quote' and not any(f['text'] == p['exact'] for e in result['finding_evidence'] if e['finding_id'] == f['id'] for p in result['passage'] if p['id'] == e['passage_id']):
                raise ValueError('Alıntı kanıt pasajıyla eşleşmiyor')
            if 'document_authority' in existing:
                for e in (e for e in result['finding_evidence'] if e['finding_id'] == f['id']):
                    validate_evidence(db, f, next(p for p in result['passage'] if p['id'] == e['passage_id']), validated_policy=validated_policy)
        if 'topic' in existing:
            for authority in result['document_authority']: check_document_authority(db, authority)
            for t in result['topic']:
                if t['status'] == 'verified':
                    bases = [b for b in result['topic_basis'] if b['topic_id'] == t['id'] and b['taxonomy_version'] == t['taxonomy_version']]
                    if not bases: raise ValueError('Doğrulanmış konu dayanağı bulunamadı')
                    for b in bases:
                        attr_column = 's.kind' if 'source_attribution' in existing else 'NULL AS kind'
                        attr_join = 'LEFT JOIN source_attribution s ON s.version_id=v.id' if 'source_attribution' in existing else ''
                        row = db.execute(f"SELECT a.status,d.title,{attr_column} FROM passage p JOIN document_version v ON v.id=p.version_id JOIN document d ON d.id=v.document_id LEFT JOIN document_authority a ON a.version_id=v.id {attr_join} WHERE p.id=?", (b['passage_id'],)).fetchone()
                        role = b.get('source_role')
                        if not b['rationale'] or not row:
                            raise ValueError('Konu dayanağı geçersiz')
                        if role is None:
                            if t['taxonomy_version'] >= 2:
                                raise ValueError('Yeni konu dayanağı için açık kaynak türü gerekli')
                            if row['status'] != 'verified' or not any(x in row['title'].lower() for x in ('tüzük','program')):
                                raise ValueError('Konu tüzük/program dayanağı geçersiz')
                        elif not active_policy(db) or not row['kind'] or role not in ('charter','program','supplement','historical'):
                            raise ValueError('Atıflı konu dayanağı için açık kaynak türü gerekli')
                        elif role in ('charter','program') and (row['kind'] != 'party_publication' or not any(term in row['title'].lower() for term in (('tüzük','tüzüğü') if role == 'charter' else ('program',)))):
                            raise ValueError('Konu dayanağının kaynak türü belgeyle uyuşmuyor')
                        elif role == 'supplement' and row['kind'] != 'party_publication':
                            raise ValueError('Ek parti metni parti yayınına dayanmalı')
        if 'match' in existing:
            for match in result['match']:
                check_match(db, match)
        if 'match_candidate' in existing:
            for candidate in result['match_candidate']: check_candidate(db, candidate)
            eligible = [c['match_id'] for c in result['match_candidate'] if c['status'] == 'eligible']
            if len(eligible) != len(set(eligible)) or set(eligible) != {m['id'] for m in result['match'] if m['eligibility'] == 'eligible'}: raise ValueError('Uygun aday ve eşleşme kümeleri uyuşmuyor')
            for resolution in result['missing_resolution']: check_missing_resolution(db, resolution)
        if 'financial' in existing:
            for financial in result['financial']: check_financial(db, financial)
        if result['schema_version'] >= 4:
            validate_dossier(result)
        if has_comparisons:
            validate_comparisons(result)
            validate_changed_topic_reviews(result)
        return result
    finally:
        db.close()


def comparison_render_data(data):
    """Project a report view without modifying the historical snapshot."""
    contracts = data.get('comparison_contract', [])
    if not contracts or contracts[0]['taxonomy_version'] < 3:
        return data
    version = contracts[0]['taxonomy_version']
    visible = dict(data)
    for name in ('comparison_topic', 'comparison_row', 'comparison_synthesis'):
        visible[name] = [item for item in data.get(name, []) if item['taxonomy_version'] == version]
    if data.get('comparison_completion_revision'):
        revision = max(data['comparison_completion_revision'], key=lambda item: item['epoch'])
        selection = json.loads(revision['selection'])
        for name, label, key in (('comparison_topic', 'topics', 'topic_id'),
                                 ('comparison_row', 'rows', 'id'),
                                 ('comparison_synthesis', 'syntheses', 'id')):
            ids = {item[key] for item in selection[label]}
            visible[name] = [item for item in visible[name] if item[key] in ids]
    active_rows = {r['id'] for r in visible['comparison_row']}
    active_fields = [f for f in data.get('comparison_field', []) if f['row_id'] in active_rows]
    active_findings = {f[k] for f in active_fields for k in ('summary_finding_id', 'quote_finding_id')}
    comparison_findings = {f[k] for f in data.get('comparison_field', []) for k in ('summary_finding_id', 'quote_finding_id')}
    # Retain independently used findings, including their paired quotation or
    # summary, so removing obsolete comparison-only findings cannot break a
    # dossier or a version-history reference.
    referenced = set(active_findings)
    for table in ('action', 'match', 'dossier_field', 'dossier_event', 'version_context', 'version_relation'):
        for row in data.get(table, []):
            referenced.update(value for key, value in row.items() if key.endswith('finding_id') and value)
    for policy in data.get('source_policy', []):
        referenced.update(json.loads(policy.get('legacy_findings') or '[]'))
    pairs = {f['pair_id'] for f in data.get('finding', []) if f['id'] in referenced and f['pair_id']}
    referenced.update(f['id'] for f in data.get('finding', []) if f['pair_id'] in pairs)
    hidden = comparison_findings - referenced
    visible['finding'] = [f for f in data.get('finding', []) if f['id'] not in hidden]
    visible['finding_evidence'] = [e for e in data.get('finding_evidence', []) if e['finding_id'] not in hidden]
    visible['comparison_field'] = active_fields
    return visible


def render_comparison_snapshot(data, renderer):
    """Render the selected dictionary while retaining historical snapshot data."""
    return renderer(comparison_render_data(data))


def audit_release(release='current', _seen=None):
    release = current() if release == 'current' else release
    if not release or not all(c in '0123456789abcdef' for c in release):
        raise ValueError('Geçersiz sürüm')
    _seen = set() if _seen is None else _seen
    if release in _seen: raise ValueError('Sürüm taban zincirinde döngü')
    _seen.add(release)
    folder = safe_path(DATA / 'releases', release)
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    if 'phase2_refresh' in manifest and (manifest['phase2_refresh'] is not True or not manifest.get('phase2_delivery')):
        raise ValueError('Yenileme manifesti geçersiz')
    if manifest['release_id'] != release or set(manifest['files']) != {'records.sqlite3', 'records.json', 'index.html'}:
        raise ValueError('Geçersiz manifest')
    for name, digest in manifest['files'].items():
        if sha(safe_path(folder, name)) != digest:
            raise ValueError('Manifest özeti eşleşmiyor')
    exported = export_db(folder / 'records.sqlite3', release)
    if manifest.get('source_policy_version') and exported['schema_version'] not in (5,6):raise ValueError('Kaynak politikası snapshot sözleşmesiyle uyuşmuyor')
    if exported['schema_version'] in (5,6):
        if (manifest.get('data_schema_version'),manifest.get('dossier_validation_version'),manifest.get('source_policy_version'))!=(exported['schema_version'],2,2):raise ValueError('Kaynak politikası manifesti geçersiz')
        if exported['schema_version'] == 6:
            c = exported['comparison_contract'][0]
            if (manifest.get('comparison_validation_version'),manifest.get('comparison_taxonomy_version'),manifest.get('comparison_stage')) != (c['version'],c['taxonomy_version'],c['stage']): raise ValueError('Karşılaştırma manifesti geçersiz')
            if manifest.get('comparison_synthesis_contract_version') != (2 if c['version'] >= 2 else None): raise ValueError('Sentez sözleşmesi manifesti geçersiz')
            if manifest.get('comparison_lineage_version') != (1 if c['version'] >= 3 else None): raise ValueError('Satır soyu manifesti geçersiz')
            if manifest.get('comparison_view_version') != (1 if c['taxonomy_version'] >= 3 else None): raise ValueError('Karşılaştırma görünümü manifesti geçersiz')
            markers = exported.get('comparison_completion', [])
            active = [m for m in markers if m['taxonomy_version'] == c['taxonomy_version']]
            if manifest.get('comparison_completion_version') != (active[0]['version'] if len(active) == 1 else None):
                raise ValueError('Kaynak kapanışı manifesti geçersiz')
            if {k: manifest[k] for k in COMPLETION_MANIFEST_KEYS if k in manifest} != completion_manifest_fields(exported):
                raise ValueError('Kaynak kapanışı revizyon manifesti geçersiz')
        if not manifest.get('phase2_delivery'):
            base_id=manifest.get('base_release')
            if not base_id and json.loads(exported['source_policy'][0]['legacy_versions']):raise ValueError('Kaynak politikası tabanı eksik')
            if base_id:
                audit_release(base_id,_seen)
                base_data = json.loads((DATA/'releases'/base_id/'records.json').read_text())
                validate_policy_descent(base_data, exported)
                validate_comparison_descent(base_data, exported)
    if exported['schema_version'] >= 4 and any(exported.get(name) for name in DOSSIER_TABLES) and not manifest.get('phase2_delivery'):
        raise ValueError('Dosya kayıtları için Faz 2 teslim manifesti gerekli')
    if manifest.get('phase2_delivery'):
        expected = (exported['schema_version'],2) if exported['schema_version'] in (5,6) else (4,1)
        valid_renderers=(16,17,18,19,20,21,22,RENDERER_VERSION) if exported['schema_version']==6 else ((11,12,13,14,15) if exported['schema_version']==5 else (9,10))
        if (manifest.get('data_schema_version'),manifest.get('dossier_validation_version')) != expected or manifest.get('renderer_version') not in valid_renderers or (exported['schema_version'] in (5,6) and manifest.get('source_policy_version')!=2):
            raise ValueError('Faz 2 manifest sürümleri geçersiz')
        base_id = manifest.get('base_release')
        if not base_id or base_id == release or not re.fullmatch(r'[0-9a-f]{32}', base_id): raise ValueError('Faz 2 tabanı geçersiz')
        audit_release(base_id, _seen)
        base_folder = safe_path(DATA / 'releases', base_id)
        base_manifest = json.loads((base_folder / 'manifest.json').read_text(encoding='utf-8'))
        base_data = json.loads((base_folder / 'records.json').read_text(encoding='utf-8'))
        base_contracts, next_contracts = base_data.get('comparison_contract', []), exported.get('comparison_contract', [])
        if base_manifest.get('renderer_version', 0) >= 20 and base_contracts and next_contracts and next_contracts[0]['taxonomy_version'] > base_contracts[0]['taxonomy_version'] and next_contracts[0]['version'] < 3:
            raise ValueError('Yeni sözlük için sürüm 3 satır soyu sözleşmesi gerekli')
        validate_policy_descent(base_data,exported)
        validate_comparison_descent(base_data,exported)
        validate_delivery_prefix(base_manifest, manifest)
        for party in manifest['phase2_delivery']['completed_prefix']:
            validate_dossier(exported, party, 'complete')
        d = manifest['phase2_delivery']
        validate_dossier(exported, d['party_id'], d['stage'])
        if base_manifest.get('phase2_delivery'):
            base_data = json.loads((base_folder / 'records.json').read_text(encoding='utf-8'))
            for table in DOSSIER_TABLES:
                if any(row not in exported[table] for row in base_data[table]): raise ValueError('Önceki dosya kayıtları silinemez veya değiştirilemez')
    if json.loads((folder / 'records.json').read_text(encoding='utf-8')) != exported:
        raise ValueError('JSON kapalı snapshot ile eşleşmiyor')
    renderer = {
        None: render_legacy_report, 2: render_v2_report, 3: render_v3_report,
        4: render_v4_report, 5: render_v5_report, 6: render_v6_report, 7: render_v7_report, 8: render_v8_report,
        9: render_v9_report, 10: render_v10_report, 11: render_v11_report, 12: render_v12_report, 13: render_v13_report, 14: render_v14_report, 15: render_v15_report, 16: render_v16_report, 17: render_v17_report, 18: render_v18_report, 19: render_v19_report, 20: render_v20_report, 21: render_v21_report, 22: render_v22_report, RENDERER_VERSION: render_report,
    }.get(manifest.get('renderer_version'))
    if renderer is None: raise ValueError('Bilinmeyen rapor sürümü')
    if (folder / 'index.html').read_bytes() != render_comparison_snapshot(exported, renderer).encode('utf-8'):
        raise ValueError('HTML kapalı snapshot ile eşleşmiyor')
    return release


def validate_phase_one_workspace(work, strict_identity=True):
    path = Path(work) / 'records.sqlite3'
    data = export_db(path, 'workspace', strict_identity=strict_identity)
    db = connect_readonly(path)
    try:
        for attempt in db.execute("SELECT * FROM attempt WHERE lead_id IS NOT NULL AND type='access' AND result='examined'"):
            lead = db.execute('SELECT * FROM lead WHERE id=?', (attempt['lead_id'],)).fetchone()
            if not lead or any(lead[k] != attempt[k] for k in ('party_id','heading','topic_id')): raise ValueError('Girişim uçla uyuşmuyor')
            check_examined_lead(db, lead, attempt['source_version_id'])
    finally: db.close()
    audit_finance(path)
    if len(data['scope_party']) != 9 or len({s['party_id'] for s in data['scope_party']}) != 9:
        raise ValueError('Dokuz kapsam kararı gerekli')
    if not data['method'] or not data['scope_observation'] or not data['identity_observation']:
        raise ValueError('Kapsam, kimlik ve yöntem kaydı gerekli')
    if any(not s['inclusion_reason'] or not s['decision_origin'] for s in data['scope_party']):
        raise ValueError('Kapsam gerekçesi gerekli')
    for v in data['document_version']:
        if not all(v[k] for k in ('original_url','accessed_at','verified_at','date_precision')):
            raise ValueError('Kaynak tarihleri veya adresi eksik')
        if v['date_precision'] == 'unknown' and not v['date_unknown_reason']:
            raise ValueError('Bilinmeyen tarih için gerekçe gerekli')
    for p in data['passage']:
        if not p['exact'] or not any(p.get(k) is not None and p.get(k) != '' for k in ('article','section','pdf_page_index','prefix','suffix')):
            raise ValueError('Pasaj veya konum eksik')
    attempts = {a['id']: a for a in data['attempt']}
    allowed = {'Bulunamadı': ('search','no_result'), 'Erişilemedi': ('access','failure'), 'Doğrulanamadı': ('verification','inconclusive')}
    for m in data['missing']:
        a = attempts.get(m['attempt_id'])
        if not a or any(a[k] != m[k] for k in ('party_id','heading','topic_id')) or allowed.get(m['status']) != (a['type'],a['result']) or not m['reason']:
            raise ValueError('Eksik kaydı girişimiyle uyuşmuyor')
    for f in data['finding']:
        if f['provenance'] not in ('quote','summary') or f['epistemic_type'] not in ('registry','fact','claim','comment'):
            raise ValueError('Bulgu kökeni veya bilgi türü geçersiz')
        if not any(r['kind']=='finding' and r['subject_id']==f['id'] and r['reviewer_kind']=='agent' and r['result']=='reviewed' and r['reason'] and r['reviewed_at'] for r in data.get('review', [])):
            raise ValueError('Bulgu için kaynak incelemesi eksik: ' + f['id'])
    return data


def validate_changed_topic_reviews(data):
    """Audit changed selected topics using persisted row review decisions."""
    contracts = data.get('comparison_contract', [])
    if not contracts or contracts[0]['taxonomy_version'] < 3:
        return True
    if contracts[0].get('version', 1) >= 3:
        return validate_versioned_row_lineage(data)
    version = contracts[0]['taxonomy_version']
    topics = {(t['topic_id'], t['taxonomy_version']): t for t in data['comparison_topic']}
    parties = {p['party_id'] for p in data['scope_party']}
    reviews = {(r['subject_kind'], r['subject_id']): r for r in data.get('comparison_semantic_review', []) if r.get('reviewer_kind') == 'agent'}
    compare_keys = ('domain', 'parent_topic_id', 'definition', 'applicable_levels', 'basis_kind')
    for (tid, tv), topic in topics.items():
        if tv != version:
            continue
        old = topics.get((tid, version - 1))
        if old and all(old.get(key) == topic.get(key) for key in compare_keys):
            continue
        rows = [r for r in data['comparison_row'] if (r['topic_id'], r['taxonomy_version']) == (tid, version)]
        if len(parties) != 9 or {r['party_id'] for r in rows} != parties:
            raise ValueError('Değişen konuda dokuz parti incelemesi gerekli')
        for row in rows:
            review = reviews.get(('comparison_row', row['id']))
            if row['state'] == 'evidence':
                fids = {f[k] for f in data['comparison_field'] if f['row_id'] == row['id'] for k in ('summary_finding_id', 'quote_finding_id')}
                refs = {e['passage_id'] for e in data['finding_evidence'] if e['finding_id'] in fids}
            elif row['state'] == 'no_explicit_statement': refs = {row.get('scope_id')}
            elif row['state'] == 'document_missing': refs = {row.get('missing_id')}
            else: refs = set()
            refs.discard(None)
            if not review or review.get('result') != 'reviewed' or not review.get('reviewed_at') or not isinstance(review.get('reason'), str) or topic['definition'] not in review['reason'] or not refs or any(ref not in review['reason'] for ref in refs):
                raise ValueError('Değişen satır için kaynaklı yeni anlam incelemesi gerekli')
            try:
                reviewed_at = dt.datetime.fromisoformat(review['reviewed_at'].replace('Z', '+00:00'))
            except (TypeError, ValueError, AttributeError):
                raise ValueError('Anlam incelemesi geçerli zaman gerektirir')
            if reviewed_at.tzinfo is None:
                raise ValueError('Anlam incelemesi zaman dilimi gerektirir')
    return True


def validate_versioned_row_lineage(data):
    """Contract 3: audit every recorded transition and its authored new meanings."""
    rows = {r['id']: r for r in data['comparison_row']}
    topics = {(t['topic_id'], t['taxonomy_version']): t for t in data['comparison_topic']}
    edges = data.get('comparison_row_lineage')
    meanings = data.get('comparison_row_meaning')
    if not isinstance(edges, list) or not edges or not isinstance(meanings, list):
        raise ValueError('Sürüm 3 için kalıcı satır soyu ve anlam kararları gerekli')
    decisions = {m['row_id']: m for m in meanings}
    if len(decisions) != len(meanings): raise ValueError('Yinelenen satır anlam kararı')
    reviews = {(r['subject_kind'], r['subject_id']): r for r in data['comparison_semantic_review'] if r.get('reviewer_kind') == 'agent'}
    parties = {p['party_id'] for p in data['scope_party']}
    fields_by_row, changes_by_row = {}, {}
    for f in data['comparison_field']:
        fields_by_row.setdefault(f['row_id'], []).append((f['field'], f.get('summary_finding_id') or '', f.get('quote_finding_id') or '', f.get('condition_key') or ''))
    for c in data.get('comparison_change', []):
        changes_by_row.setdefault(c['row_id'], []).append((c['before_passage_id'], c['after_passage_id'], c['summary'], c['order_basis']))
    grouped = {}
    for edge in edges:
        old, new = rows.get(edge.get('old_row_id')), rows.get(edge.get('new_row_id'))
        if not old or not new or edge.get('transition') not in ('mapped', 'superseded') or new['taxonomy_version'] != old['taxonomy_version'] + 1 or old['party_id'] != new['party_id']:
            raise ValueError('Geçersiz satır soyu')
        if edge['transition'] == 'mapped':
            keys = ('party_id', 'level', 'organ', 'version_id', 'alternative_group', 'source_role', 'state', 'scope_id', 'missing_id')
            if any(old.get(k) != new.get(k) for k in keys): raise ValueError('Mekanik satır soyu kaynakla uyuşmuyor')
            if sorted(fields_by_row.get(old['id'], [])) != sorted(fields_by_row.get(new['id'], [])) or sorted(changes_by_row.get(old['id'], [])) != sorted(changes_by_row.get(new['id'], [])):
                raise ValueError('Mekanik satır alanları kaynakla uyuşmuyor')
        grouped.setdefault(new['taxonomy_version'], []).append((edge, old, new))
    markers = data.get('comparison_lineage_contract')
    if not isinstance(markers, list) or len(markers) != 1 or markers[0].get('version') != 1 or type(markers[0].get('first_taxonomy_version')) is not int:
        raise ValueError('Satır soyu sözleşme işaretçisi eksik')
    first = markers[0]['first_taxonomy_version']
    if first < 3 or first > data['comparison_contract'][0]['taxonomy_version']:
        raise ValueError('Satır soyu başlangıcı geçersiz')
    if set(grouped) != set(range(first, data['comparison_contract'][0]['taxonomy_version'] + 1)):
        raise ValueError('Satır soyu sürüm zinciri eksik')
    needed = set()
    for version, links in grouped.items():
        previous = {r['id'] for r in rows.values() if r['taxonomy_version'] == version - 1}
        if {old['id'] for _, old, _ in links} != previous:
            raise ValueError('Önceki satırların tam soyu gerekli')
        for old_id in previous:
            transitions = [e['transition'] for e, old, _ in links if old['id'] == old_id]
            if 'mapped' in transitions and transitions != ['mapped']:
                raise ValueError('Mekanik soy tek hedef gerektirir')
        changed = {tid for (tid, tv), t in topics.items() if tv == version and ((tid, version-1) not in topics or any(t.get(k) != topics[tid, version-1].get(k) for k in ('domain','parent_topic_id','definition','applicable_levels','basis_kind')))}
        moved = {new['id'] for edge, old, new in links if old['topic_id'] != new['topic_id'] or edge['transition'] == 'superseded'}
        affected = changed | {rows[rid]['topic_id'] for rid in moved}
        for tid in affected:
            selected = [r for r in rows.values() if r['taxonomy_version'] == version and r['topic_id'] == tid]
            if len(parties) != 9 or {r['party_id'] for r in selected if r['state'] != 'not_researched'} != parties:
                raise ValueError('Değişen konuda dokuz parti incelemesi gerekli')
        needed.update(r['id'] for r in rows.values() if r['taxonomy_version'] == version and (r['topic_id'] in changed or r['id'] in moved))
    if set(decisions) != needed: raise ValueError('Satır anlam kararları soyla uyuşmuyor')
    for rid in needed:
        row, decision = rows[rid], decisions[rid]
        topic = topics[row['topic_id'], row['taxonomy_version']]
        review = reviews.get(('comparison_row', rid))
        if row['state'] == 'evidence':
            fids = {f[k] for f in data['comparison_field'] if f['row_id'] == rid for k in ('summary_finding_id','quote_finding_id')}
            refs = {e['passage_id'] for e in data['finding_evidence'] if e['finding_id'] in fids}
        elif row['state'] == 'no_explicit_statement': refs = {row.get('scope_id')}
        elif row['state'] == 'document_missing': refs = {row.get('missing_id')}
        else: refs = set()
        refs.discard(None)
        try: stored_refs = json.loads(decision['refs'])
        except (ValueError, TypeError): raise ValueError('Satır anlam kaynakları geçersiz')
        conditions = decision.get('conditions')
        if decision.get('definition') != topic['definition'] or not isinstance(conditions, str) or not conditions.strip() or not isinstance(stored_refs, list) or len(stored_refs) != len(refs) or set(stored_refs) != refs or not refs:
            raise ValueError('Satır anlam kararı tanım ve kaynaklarla uyuşmuyor')
        reason = review.get('reason') if review else None
        if not review or review.get('result') != 'reviewed' or not isinstance(reason, str) or topic['definition'] not in reason or conditions not in reason or any(ref not in reason for ref in refs):
            raise ValueError('Satır için yeni kaynaklı anlam incelemesi gerekli')
        try: reviewed_at = dt.datetime.fromisoformat(review['reviewed_at'].replace('Z', '+00:00'))
        except (KeyError, TypeError, ValueError, AttributeError): raise ValueError('Anlam incelemesi geçerli zaman gerektirir')
        if reviewed_at.tzinfo is None: raise ValueError('Anlam incelemesi zaman dilimi gerektirir')
    return True


def validate_phase_three_workspace(folder, stage):
    folder = Path(folder)
    data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
    actual_stage = data['comparison_contract'][0]['stage'] if data.get('schema_version') == 6 else None
    if actual_stage != stage and not (stage == 'partial' and actual_stage == 'complete'):
        raise ValueError('İstenen karşılaştırma aşaması uyuşmuyor')
    # A complete snapshot satisfies a partial request only after the stronger
    # complete-stage checks below have also run.
    stage = actual_stage
    validate_comparisons(data)
    validate_changed_topic_reviews(data)
    visible = comparison_render_data(data)
    order = ('yeni-parti','tip','dem','iyi','yeni-yol','dbp','emep','saadet','demokrat')
    for topic in data['comparison_topic']:
        rows = [r for r in visible['comparison_row'] if r['topic_id'] == topic['topic_id'] and r['taxonomy_version'] == topic['taxonomy_version']]
        active = topic['taxonomy_version'] == data['comparison_contract'][0]['taxonomy_version']
        if active and stage in ('tracer','complete') and {r['party_id'] for r in rows} != set(order): raise ValueError('Konu dokuz partiyi kapsamalı')
        if stage == 'complete' and topic['taxonomy_version'] == data['comparison_contract'][0]['taxonomy_version'] and any(r['state'] == 'not_researched' for r in rows): raise ValueError('Tam aşamada incelenmemiş kayıt var')
        if active and stage == 'tracer' and sum(r['state'] == 'evidence' for r in rows) < 2: raise ValueError('Tracer iki kaynaklı yanıt gerektirir')
    report = (folder / 'index.html').read_text(encoding='utf-8')
    for row in visible['comparison_row']:
        if data['comparison_contract'][0]['taxonomy_version'] >= 3 and row['taxonomy_version'] != data['comparison_contract'][0]['taxonomy_version']:
            continue
        rid = html.escape(row['id'], quote=True)
        encoded = urllib.parse.quote(row['id'], safe='')
        if f'id="comparison-{rid}"' not in report or f'id="dossier-comparison-{rid}"' not in report or not any(f'href="#comparison-{part}"' in report for part in (rid, encoded)) or not any(f'href="#dossier-comparison-{part}"' in report for part in (rid, encoded)):
            raise ValueError('İki görünüm arasındaki bağlantı eksik')
    return True


def validate_phase_three(release, stage):
    return validate_phase_three_workspace(DATA / 'releases' / release, stage)


def validate_phase_one(release='current'):
    release = audit_release(release)
    folder = DATA / 'releases' / release
    manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
    data = validate_phase_one_workspace(folder, strict_identity=manifest.get('identity_validation_version', 0) >= 1)
    validate_phase_one_html(data, (folder / 'index.html').read_text(encoding='utf-8'))
    return release


def validate_phase_one_html(data, report):
    data = comparison_render_data(data)
    for f in data['finding']:
        if 'data-finding-id="' + html.escape(f['id'], quote=True) + '"' not in report:
            raise ValueError('Bulgu HTML içinde eksik')
    for m in data['match']:
        if m['eligibility'] == 'eligible' and 'data-match-id="' + html.escape(m['id'], quote=True) + '"' not in report:
            raise ValueError('Uygun eşleşme HTML içinde eksik')


def assert_lock(work):
    metadata = json.loads((Path(work) / 'workspace.json').read_text(encoding='utf-8'))
    lock = DATA / '.write.lock'
    if not lock.is_file() or json.loads(lock.read_text(encoding='utf-8')).get('token') != metadata.get('token') or not metadata.get('token'):
        raise ValueError('Çalışma alanının yazıcı kilidi bulunamadı')
    return metadata


def publish_release(work, fail_at=None, party=None, stage='complete', refresh=False):
    work = Path(work)
    metadata = assert_lock(work)
    release = uuid.uuid4().hex
    staging = DATA / '.staging' / release
    staging.mkdir(parents=True)
    try:
        if current() != metadata['base']:
            raise ValueError('Çalışma alanının taban sürümü eskidi')
        base_manifest = json.loads((DATA / 'releases' / metadata['base'] / 'manifest.json').read_text(encoding='utf-8')) if metadata['base'] else {}
        base_delivery = base_manifest.get('phase2_delivery')
        if refresh and (party is not None or stage != 'complete'): raise ValueError('Yenileme parti veya tracer ile birlikte kullanılamaz')
        if base_delivery and not party and not refresh: raise ValueError('Faz 2 tabanında parti teslimi zorunlu')
        if refresh:
            phase_delivery = dict(base_delivery) if base_delivery else None
            validate_delivery_prefix(base_manifest, {'phase2_delivery':phase_delivery,'phase2_refresh':True})
        elif party:
            old = base_delivery['completed_prefix'] if base_delivery else []
            completed = old + [party] if stage == 'complete' else old[:]
            phase_delivery = dict(party_id=party, stage=stage, completed_prefix=completed)
            validate_delivery_prefix(base_manifest, {'phase2_delivery': phase_delivery})
        else: phase_delivery = None
        db = connect(work / 'records.sqlite3')
        db.commit(); db.close()
        if fail_at == 'close': raise RuntimeError('Enjekte edilen kapatma hatası')
        shutil.copyfile(work / 'records.sqlite3', staging / 'records.sqlite3')
        payload = export_db(staging / 'records.sqlite3', release, strict_identity=True)
        (staging / 'records.json').write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        if fail_at == 'json': raise RuntimeError('Enjekte edilen JSON hatası')
        renderer = render_v15_report if payload['schema_version'] == 5 else render_report
        renderer_version = 15 if payload['schema_version'] == 5 else RENDERER_VERSION
        (staging / 'index.html').write_text(render_comparison_snapshot(payload, renderer), encoding='utf-8')
        if fail_at == 'html': raise RuntimeError('Enjekte edilen HTML hatası')
        # Once the base is phase-capable, deleting its method cannot bypass
        # acceptance. Earlier snapshots may still be authored incrementally.
        base_phase = False
        if metadata['base']:
            base_data = json.loads((DATA / 'releases' / metadata['base'] / 'records.json').read_text(encoding='utf-8'))
            validate_policy_descent(base_data, payload)
            validate_comparison_descent(base_data, payload)
            base = connect_readonly(DATA / 'releases' / metadata['base'] / 'records.sqlite3')
            try:
                has_method = base.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='method'").fetchone()
                base_phase = bool(has_method and base.execute('SELECT 1 FROM method LIMIT 1').fetchone())
            finally: base.close()
        if base_phase or payload.get('method'):
            phase_data = validate_phase_one_workspace(staging)
            validate_phase_one_html(phase_data, (staging / 'index.html').read_text(encoding='utf-8'))
        if phase_delivery:
            from dosyalar import validate_phase_two_workspace
            validate_phase_two_workspace(staging, None if refresh else party, stage)
            for completed_party in phase_delivery['completed_prefix']:
                validate_dossier(payload, completed_party, 'complete')
        if payload['schema_version'] == 6:
            validate_phase_three_workspace(staging, payload['comparison_contract'][0]['stage'])
        manifest = {'release_id': release, 'renderer_version': renderer_version, 'identity_validation_version': 1, 'files': {n: sha(staging / n) for n in ('records.sqlite3', 'records.json', 'index.html')}}
        if payload['schema_version'] in (5,6):manifest.update(data_schema_version=payload['schema_version'],dossier_validation_version=2,source_policy_version=2,base_release=metadata['base'])
        if phase_delivery:
            manifest.update(data_schema_version=payload['schema_version'], dossier_validation_version=2, source_policy_version=2, phase2_delivery=phase_delivery, base_release=metadata['base'])
        if payload['schema_version'] == 6:
            c = payload['comparison_contract'][0]
            manifest.update(comparison_validation_version=c['version'], comparison_taxonomy_version=c['taxonomy_version'], comparison_stage=c['stage'])
            if c['version'] >= 2:
                manifest['comparison_synthesis_contract_version'] = 2
            if c['version'] >= 3:
                manifest['comparison_lineage_version'] = 1
            if c['taxonomy_version'] >= 3:
                manifest['comparison_view_version'] = 1
            markers = [m for m in payload.get('comparison_completion', []) if m['taxonomy_version'] == c['taxonomy_version']]
            if markers:
                manifest['comparison_completion_version'] = markers[0]['version']
            manifest.update(completion_manifest_fields(payload))
        if refresh: manifest['phase2_refresh'] = True
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
    rc = sub.add_parser('resolve-candidate'); rc.add_argument('--workspace', required=True); rc.add_argument('--candidate', required=True); rc.add_argument('--match', required=True); rc.add_argument('--input', default='-')
    ch = sub.add_parser('chain'); ch.add_argument('--workspace', required=True); ch.add_argument('--party', required=True); ch.add_argument('--topic', required=True)
    pub = sub.add_parser('publish'); pub.add_argument('--workspace', required=True); group=pub.add_mutually_exclusive_group(); group.add_argument('--party'); group.add_argument('--refresh', action='store_true'); pub.add_argument('--stage', choices=('tracer','complete'), default='complete')
    f = sub.add_parser('freeze'); f.add_argument('--workspace', required=True); f.add_argument('--tbmm-version', required=True); f.add_argument('--method-version', type=int, default=1)
    a = sub.add_parser('audit'); a.add_argument('--release', default='current'); a.add_argument('--check', choices=('matches', 'finance')); a.add_argument('--phase', choices=('1','2','3')); a.add_argument('--party'); a.add_argument('--stage', choices=('tracer','partial','complete'), default='complete')
    cl = sub.add_parser('comparison-load'); cl.add_argument('--workspace', required=True); cl.add_argument('--input', required=True); cl.add_argument('--inventory')
    cr = sub.add_parser('comparison-reconcile'); cr.add_argument('--workspace', required=True); cr.add_argument('--taxonomy', required=True); cr.add_argument('--inventory', required=True); cr.add_argument('--input', required=True)
    cc = sub.add_parser('comparison-check'); cc.add_argument('--input', required=True); cc.add_argument('--inventory')
    dl = sub.add_parser('dossier-load'); dl.add_argument('--workspace', required=True); dl.add_argument('--input', required=True)
    dc = sub.add_parser('dossier-check'); dc.add_argument('--input', required=True); dc.add_argument('--stage', choices=('tracer','complete'), default='complete')
    dr = sub.add_parser('delivery-receipt'); dr.add_argument('--release', required=True); dr.add_argument('--party', required=True); dr.add_argument('--out', required=True); dr.add_argument('--previous')
    rr = sub.add_parser('receipt-check'); rr.add_argument('--input', required=True)
    s = sub.add_parser('serve'); s.add_argument('--host', default='127.0.0.1'); s.add_argument('--port', type=int, default=8000)
    args = p.parse_args()
    if args.command == 'capture': print(json.dumps(capture_source(args.url, args.kind, args.out), ensure_ascii=False))
    elif args.command == 'workspace': print(open_workspace(args.scratch))
    elif args.command == 'record':
        import sys
        result = record(args.workspace, args.kind, json.load(sys.stdin) if args.input == '-' else json.loads(Path(args.input).read_text(encoding='utf-8')))
        if result is not None: print(result)
    elif args.command == 'resolve-candidate':
        import sys
        resolve_candidate(args.workspace, args.candidate, args.match, json.load(sys.stdin) if args.input == '-' else json.loads(Path(args.input).read_text(encoding='utf-8')))
    elif args.command == 'chain':
        assert_lock(args.workspace)
        db = connect(Path(args.workspace) / 'records.sqlite3')
        try:
            print(json.dumps([dict(x) for x in db.execute('SELECT * FROM lead WHERE party_id=? AND topic_id=? ORDER BY rowid', (args.party,args.topic))], ensure_ascii=False, indent=2))
        finally: db.close()
    elif args.command == 'publish': print(publish_release(args.workspace, party=args.party, stage=args.stage, refresh=args.refresh))
    elif args.command == 'comparison-load':
        inventory = json.loads(Path(args.inventory).read_text(encoding='utf-8')) if args.inventory else None
        load_comparison(args.workspace, json.loads(Path(args.input).read_text(encoding='utf-8')), inventory); print('COMPARISON_LOAD_OK')
    elif args.command == 'comparison-reconcile':
        comparison_reconcile(args.workspace, *(json.loads(Path(path).read_text(encoding='utf-8')) for path in (args.taxonomy, args.inventory, args.input))); print('COMPARISON_RECONCILE_OK')
    elif args.command == 'comparison-check':
        check_comparison_input(args.input, args.inventory); print('COMPARISON_INPUT_OK')
    elif args.command == 'dossier-load':
        from dosyalar import load_dossier
        load_dossier(args.workspace, json.loads(Path(args.input).read_text(encoding='utf-8')))
    elif args.command == 'dossier-check':
        from dosyalar import check_dossier_input
        check_dossier_input(args.input, args.stage); print('DOSSIER_INPUT_OK')
    elif args.command == 'delivery-receipt':
        from dosyalar import make_delivery_receipt
        receipt = make_delivery_receipt(args.release, args.party, args.previous)
        out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print('DELIVERY_RECEIPT_OK', receipt['release_id'])
    elif args.command == 'receipt-check':
        from dosyalar import check_delivery_receipt
        check_delivery_receipt(args.input); print('DELIVERY_RECEIPT_OK')
    elif args.command == 'freeze': print(freeze_cutoff(args.workspace, args.tbmm_version, args.method_version))
    elif args.command == 'audit':
        if args.phase == '2' and args.check is None:
            # validate_phase_two performs the full release audit itself.
            from dosyalar import validate_phase_two
            release = validate_phase_two(args.release, args.party, args.stage)
            print('PHASE2_TRACER_OK' if args.party and args.stage == 'tracer' else ('PHASE2_PARTY_OK' if args.party else 'PHASE2_AUDIT_OK'), release)
            return
        release = audit_release(args.release)
        if args.check:
            db = connect(DATA / 'releases' / release / 'records.sqlite3')
            try:
                table = {'matches': 'match', 'finance': 'financial'}[args.check]
                if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (table,)).fetchone(): raise ValueError('Bu sürüm hedef denetimi desteklemiyor')
            finally: db.close()
            if args.check == 'finance': audit_finance(DATA / 'releases' / release / 'records.sqlite3')
        if args.phase == '1':
            validate_phase_one(release)
            print('PHASE1_AUDIT_OK', release)
        elif args.phase == '2':
            from dosyalar import validate_phase_two
            validate_phase_two(release, args.party, args.stage)
            print('PHASE2_TRACER_OK' if args.party and args.stage == 'tracer' else ('PHASE2_PARTY_OK' if args.party else 'PHASE2_AUDIT_OK'), release)
        elif args.phase == '3':
            validate_phase_three(release, args.stage)
            print('PHASE3_AUDIT_OK', release)
        else: print('AUDIT_OK', release)
    elif args.command == 'serve':
        if args.host != '127.0.0.1': raise ValueError('Sunucu yalnız 127.0.0.1 üzerinde çalışabilir')
        from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
        class Handler(SimpleHTTPRequestHandler):
            def translate_path(self, path):
                relative = urllib.parse.unquote(urllib.parse.urlsplit(path).path).lstrip('/')
                if not (re.fullmatch(r'releases/[0-9a-f]+/(?:index\.html|records\.json|records\.sqlite3|manifest\.json)', relative) or
                        re.fullmatch(r'objects/[0-9a-f]{64}/(?:readable\.html|original\.pdf|original\.html\.bin)', relative) or
                        re.fullmatch(r'views/[0-9a-f]{32}/(?:index\.html|manifest\.json|assets/[0-9a-f]{64}\.(?:css|png|jpg|gif|webp|ico|woff2|woff|ttf|otf))', relative)):
                    return str(DATA / '.invalid-path')
                try: return str(safe_path(DATA, relative))
                except ValueError: return str(DATA / '.invalid-path')
            def end_headers(self):
                self.send_header('X-Content-Type-Options', 'nosniff')
                if urllib.parse.urlsplit(self.path).path.startswith('/views/'):
                    self.send_header('Content-Security-Policy', ARCHIVE_CSP)
                if urllib.parse.urlsplit(self.path).path.endswith('.bin'):
                    self.send_header('Content-Disposition', 'attachment')
                super().end_headers()
            def guess_type(self, path):
                return 'application/octet-stream' if path.endswith('.bin') else super().guess_type(path)
        ThreadingHTTPServer((args.host, args.port), Handler).serve_forever()


if __name__ == '__main__':
    main()
