"""Sürüm 2: kaynak derleme ve açık atıf; sicil kimliği ayrı bir iddiadır."""
import datetime as dt
import json
from urllib.parse import urlsplit

POLICY_VERSION = 2
POLICY_TABLES = {
    'source_policy': 'version INTEGER PRIMARY KEY, adopted_at TEXT NOT NULL, decision TEXT NOT NULL, legacy_versions TEXT NOT NULL, legacy_findings TEXT NOT NULL',
    'source_attribution': 'version_id TEXT PRIMARY KEY REFERENCES document_version(id), kind TEXT NOT NULL, publisher TEXT NOT NULL, author TEXT, social_handle TEXT, published_at TEXT, date_precision TEXT NOT NULL, public_url TEXT NOT NULL, basis TEXT NOT NULL',
}
KINDS = {'party_publication': ('party',), 'journalism': ('journalism','news'), 'social_publication': ('social',), 'registry': ('registry',), 'official': ('official',), 'other': ('unknown','unverified','academic','independent_report')}


def folded(text):
    return text.translate(str.maketrans({'İ':'i', 'I':'ı'})).casefold()


def active_policy(db):
    if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='source_policy'").fetchone():
        return None
    row = db.execute('SELECT * FROM source_policy ORDER BY version DESC LIMIT 1').fetchone()
    if row and row['version'] != POLICY_VERSION:
        raise ValueError('Bilinmeyen kaynak politikası')
    return dict(row) if row else None


def check_attribution(db, value):
    from arsiv import safe_url, safe_path, DATA
    v = db.execute('SELECT v.*,d.source_kind,d.party_id,p.legal_name FROM document_version v JOIN document d ON d.id=v.document_id JOIN party p ON p.id=d.party_id WHERE v.id=?', (value.get('version_id'),)).fetchone()
    if not v or value.get('kind') not in KINDS or v['source_kind'] not in KINDS[value['kind']]:
        raise ValueError('Kaynak türü ve atıf uyuşmuyor')
    if not value.get('publisher') or not value.get('basis'):
        raise ValueError('Yayıncı ve kaynaklı atıf gerekçesi gerekli')
    safe_url(value.get('public_url', ''))
    if value['public_url'] not in (v['original_url'],v['final_url']):
        raise ValueError('Atıf kalıcı adresi arşivlenen kaynakla uyuşmuyor')
    date, precision = value.get('published_at'), value.get('date_precision')
    if precision == 'unknown':
        if date is not None: raise ValueError('Bilinmeyen yayın tarihi boş kalmalı')
    elif precision == 'day' and date:
        dt.date.fromisoformat(date)
    else: raise ValueError('Yayın tarihi kesinliği geçersiz')
    if value['kind'] == 'social_publication' and (not (value.get('author') or value.get('social_handle')) or not date):
        raise ValueError('Sosyal paylaşım için hesap/yazar, tarih ve kalıcı adres gerekli')
    if value['kind'] == 'party_publication':
        raw = safe_path(DATA, v['original_path']).read_bytes()
        text = folded(raw.decode('utf-8', errors='replace'))
        publisher_present = folded(value['publisher']) in text
        # PDF metni sıkıştırılmış olabilir; HTML sayfası yalnız kısa parti
        # adını kullanabilir. Tam adı taşıyan arşivli HTML yayını, aynı parti
        # ve aynı ana makinedeki bu yayının atfını destekler (D-13).
        if not publisher_present and (raw.startswith(b'%PDF-') or v['mime'] == 'text/html'):
            host = urlsplit(v['final_url']).hostname
            for h in db.execute("SELECT v.original_path,v.final_url,a.publisher FROM document_version v JOIN document d ON d.id=v.document_id JOIN source_attribution a ON a.version_id=v.id WHERE d.party_id=? AND a.kind='party_publication' AND v.mime='text/html'", (v['party_id'],)):
                if urlsplit(h['final_url']).hostname == host and folded(h['publisher']) == folded(value['publisher']) and folded(value['publisher']) in folded(safe_path(DATA,h['original_path']).read_text(encoding='utf-8',errors='replace')):
                    publisher_present = True
                    break
        if folded(value['publisher']) != folded(v['legal_name']) or not publisher_present:
            raise ValueError('Parti yayını yayıncı ilişkisi kaynakta bulunamadı')
    return True


def validate_policy(db, data):
    policy = active_policy(db)
    if not policy: return
    for key in ('legacy_versions','legacy_findings'):
        if not isinstance(json.loads(policy[key]), list): raise ValueError('Eski kayıt sınırı geçersiz')
    for a in data['source_attribution']: check_attribution(db,a)
    old_versions = set(json.loads(policy['legacy_versions']))
    attrs = {a['version_id'] for a in data['source_attribution']}
    if any(v['id'] not in old_versions and v['id'] not in attrs for v in data['document_version']):
        raise ValueError('Yeni kaynak için atıf gerekli')


def check_evidence_attribution(db, finding, row):
    policy = active_policy(db)
    if not policy: return False
    if finding['id'] in json.loads(policy['legacy_findings']): return True
    a = db.execute('SELECT * FROM source_attribution WHERE version_id=?', (row['version_id'],)).fetchone()
    if not a: raise ValueError('Yeni bulgu için kaynak atıf kaydı gerekli')
    check_attribution(db, dict(a))
    if a['kind'] in ('party_publication','social_publication','journalism') and finding['epistemic_type'] not in ('claim','comment'):
        raise ValueError('Yayıncı beyanı/haberi atıflı iddia olarak derlenmeli')
    return True


def validate_policy_descent(base_data, data):
    old = base_data.get('source_policy', [])
    if old and data.get('source_policy') != old:
        raise ValueError('Kaynak politikası ve eski kayıt sınırları kaldırılamaz/değiştirilemez')
    if not old and data.get('source_policy'):
        row = data['source_policy'][0]
        if set(json.loads(row['legacy_versions'])) != {v['id'] for v in base_data['document_version']} or set(json.loads(row['legacy_findings'])) != {f['id'] for f in base_data['finding']}:
            raise ValueError('Politika geçiş sınırları taban kayıtlarıyla uyuşmuyor')
    for table in ('source_attribution','archive_view'):
        if any(row not in data.get(table,[]) for row in base_data.get(table,[])):
            raise ValueError('Önceki kaynak atıfları değiştirilemez')


def official_site_supported(data, field, evidence):
    versions = {v['id']:v for v in data['document_version']}
    passages = {p['id']:p for p in data['passage']}
    attrs = {a['version_id']:a for a in data.get('source_attribution',[])}
    host = urlsplit(field['value']).hostname.removeprefix('www.')
    return any((a := attrs.get(passages[e['passage_id']]['version_id'])) and a['kind']=='party_publication' and urlsplit(versions[a['version_id']]['final_url']).hostname.removeprefix('www.')==host for e in evidence if e['finding_id']==field['finding_id'])


def attribution_text(value):
    if value['kind'] == 'social_publication':
        return 'Sosyal medya kullanıcısı ' + (value.get('social_handle') or value['author']) + ' bunu ' + value['published_at'] + ' paylaştı.'
    name = value['publisher'] + ((' · ' + value['author']) if value.get('author') else '')
    date = (' · ' + value['published_at']) if value.get('published_at') else ' · yayın tarihi belirtilmemiş'
    return name + date
