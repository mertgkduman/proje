"""Add the independently dated domestic and European decisions to the EMEP draft."""

import json
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text, readable_bytes
from arsiv_gorunum import build_view, validate_view
import uygulamalar as rules

checks = Path(__file__).resolve().parent
working = Path('data/practices')
source_root = working / 'sources' / 'emep'
source_checks = checks / 'encu-49976-sources'
case = '0410-encu-decisions'
party = 'emep'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')


def read(path):
    return json.loads(path.read_bytes())


def digest(data):
    return sha256(data).hexdigest()


package_path = working / '04-emep.json'
review_path = working / '04-emep-review.json'
assert (digest(package_path.read_bytes()), digest(review_path.read_bytes())) == (
    '2dd16c019b1bfe74e87dcc2da2a24664884be7f29d85bf1955be28eb4e5abe17',
    '9cb39143f4f55542102269b5d58c4dc48ff29640780ac44d9f4e96cb7af8a349',
)
package, review = read(package_path), read(review_path)
entries, records = package['entries'], package['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (73, 72, 0)
scope = next(row['id'] for row in records['practice_scope_v2']
             if row['topic_id'] == 'kurt-sorunu' and row['research_kind'] == 'event')
local = read(source_checks / 'domestic-reading.json')
french, translation = read(source_checks / 'reading.json')['sources']
points = {}


def add(table, **values):
    records[table].append(values)


def insert(table, **values):
    entries.append({'kind': table, 'values': values})


def write_once(path, data):
    if path.exists():
        assert path.read_bytes() == data, path
    else:
        path.write_bytes(data)


def source(role, kind, receipt, title, document_day, published_day, passages):
    path = source_checks / receipt['original_path']
    raw = path.read_bytes()
    checksum = digest(raw)
    assert (checksum, len(raw)) == (receipt['sha256'], receipt['bytes'])
    original_url = receipt.get('url') or receipt['retrieved_url']
    doc = f'{case}-{role}'
    ver = f'{doc}-v1'
    obj = source_root / 'objects' / checksum
    obj.mkdir(parents=True, exist_ok=True)
    original = 'original.pdf' if kind == 'pdf' else 'original.html.bin'
    write_once(obj / original, raw)
    write_once(obj / 'readable.html', readable_bytes(raw, kind, legacy=False))
    insert('document', id=doc, party_id=party, title=title,
           source_kind='party' if role == 'party' else 'official')
    insert('document_version', id=ver, document_id=doc, original_url=original_url, final_url=original_url,
           document_date=document_day, date_precision='day', date_unknown_reason=None,
           version_label=title, accessed_at=receipt['retrieved_at_utc'], verified_at=now,
           mime='application/pdf' if kind == 'pdf' else 'text/html', sha256=checksum,
           original_path=f'objects/{checksum}/{original}', readable_path=f'objects/{checksum}/readable.html')
    if kind == 'html':
        view = build_view(raw, original_url, source_root, fetch_assets=False, http_charset='utf-8')
        view['version_id'] = ver
        validate_view(source_root, view)
        insert('archive_view', **view)
    insert('source_attribution', version_id=ver, kind='party_publication' if role == 'party' else 'official',
           publisher=receipt['publisher'], author=receipt.get('author'), social_handle=None, published_at=published_day,
           date_precision='day' if published_day else 'unknown', public_url=original_url,
           basis=receipt.get('reading', title))
    for suffix, section, page, exact, point in passages:
        text = pdf_page_text(path, page) if kind == 'pdf' else html_source_text(raw)
        assert exact in text, (role, suffix)
        pid = f'{case}-{suffix}-p'
        points[pid] = point
        insert('passage', id=pid, version_id=ver, exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=None)
    sections = sorted({section for _, section, *_ in passages})
    attempt = f'{doc}-reading'
    add('practice_scope_source', scope_id=scope, version_id=ver,
        inspected_sections=json.dumps(sections, ensure_ascii=False), inspected_at=now)
    add('practice_attempt_v2', id=attempt, scope_id=scope, attempted_at=now, query=original_url, url=original_url,
        result='examined', reason=f'{title} içindeki ilgili bölüm okundu.', source_version_id=ver)
    add('practice_lead', id=f'lead-{attempt}', scope_id=scope, url=original_url, state='examined',
        relevance_reason='Roboski başvurularına ilişkin yargı ve sonraki parti kaydının zaman sırası.',
        attempt_ids=json.dumps([attempt]))


source('aym', 'pdf', local['domestic'], 'AYM 2014/11864, 2016/1 karar cildi', '2016-02-24', None, [
    ('aym-date', 'AYM başvuru kimliği, karar ve gazete günü', 133,
     'Karar Tarihi: 24/2/2016\nR.G. Tarih ve Sayı: 23/3/2016-29662',
     '2014/11864 numaralı karar 24 Şubat 2016 tarihli, gazete kaydı 23 Mart 2016 ve 29662.'),
    ('aym-result', 'AYM hüküm A', 145, 'deniyle başvurunun REDDİNE,',
     'AYM geçerli mazeret olmaksızın dosya eksikliği süresinde giderilmediği için başvuruyu reddetti.'),
    ('aym-vote', 'AYM hükmü ve karşıoy bilgisi', 146, 'Osman Alifeyyaz PAKSÜT’ün karşıoyu',
     'Karar oyçokluğuyla verildi. Osman Alifeyyaz Paksüt karşıoy kullandı.'),
])
source('echr', 'pdf', french, 'AİHM 49976/16 ve diğer başvurular, Fransızca özgün karar', '2018-04-10', None, [
    ('echr-date', 'AİHM başvuru kimliği ve karar günü', 0, 'le 10 avril 2018 en un comité composé de :',
     'AİHM İkinci Bölümü 10 Nisan 2018’de komite halinde karar verdi.'),
    ('echr-exhaustion', 'AİHM §25, 35/1 ve hüküm', 11,
     'irrecevables, en application de l’article 35 § 1 de la Convention.',
     'Karar, iç hukuk yollarının tüketilmemesine ve Sözleşme 35/1’e dayanıyor.'),
    ('echr-result', 'AİHM birleştirme ve kabul edilemezlik hükmü', 11,
     'Par ces motifs, la Cour, à l’unanimité,\nDécide de joindre les requêtes ;\nDéclare les requêtes irrecevables.',
     'AİHM başvuruları birleştirdi ve oybirliğiyle kabul edilemez buldu.'),
    ('echr-notice', 'AİHM yazılı bildirim', 12, 'communiqué par écrit le 17 mai 2018.',
     'Karar 17 Mayıs 2018’de yazılı bildirildi.'),
])
source('translation', 'pdf', translation, 'T.C. Adalet Bakanlığı gayriresmî AİHM çevirisi', '2018-04-10', None, [
    ('tr-status', 'Türkçe çevirinin kökeni ve niteliği', 0,
     '© T.C. Adalet Bakanlığı, 2018. Bu gayri resmî çeviri',
     'Türkçe metin Bakanlığın gayriresmî çevirisidir. Özgün hüküm Fransızca.'),
    ('tr-result', 'Türkçe çeviride AİHM hükmü', 17,
     'Başvuruların kabul edilemez olduğuna karar vermiştir.',
     'Çeviri AİHM’in kabul edilemezlik hükmünü aktarır.'),
])
source('party', 'html', local['party'], 'EMEP Bölge Örgütü Roboski açıklaması', '2020-06-03', '2020-06-03', [
    ('party', 'EMEP’in sonraki Roboski açıklamasındaki AİHM atfı', None,
     'serlêdanêred kir û doz vegeriyaseriyaserî.',
     'EMEP Bölge Örgütü sonraki Kürtçe açıklamada AİHM’in ret kararını tartıştı ve eleştirdi.'),
])

bounds = ('EMEP Bölge Örgütü’nün 3 Haziran 2020 yayımı iki yargı kararından sonra. '
          'Önceden eşleşebilir ölçülebilir parti tutumu, yargı yetkisi ve nedensellik bu belgelerde açık. '
          'Yargı kararları usule ilişkin, ceza sorumluluğu hakkında esastan hüküm içermiyor.')
for name, key, day, title, context, basis, items in [
    ('aym', 'aym-2014-11864-decision', '2016-02-24', 'AYM 2014/11864 Roboski başvurusunun reddi',
     'AYM İkinci Bölümü, Mehmet Encu ve Diğerleri',
     '24 Şubat 2016 usulden ret kararı ve karşıoy. 23 Mart 2016 tarihli 29662 sayılı gazete kaydı.',
     ('aym-date', 'aym-result', 'aym-vote')),
    ('echr', 'echr-49976-16-decision', '2018-04-10', 'AİHM 49976/16 Roboski başvurularında kabul edilemezlik',
     'AİHM İkinci Bölümü, Selahattin Encu ve diğerleri',
     '10 Nisan 2018 oybirliğiyle kabul edilemezlik. 17 Mayıs 2018 yazılı bildirim.',
     ('echr-date', 'echr-exhaustion', 'echr-result', 'echr-notice', 'tr-result')),
]:
    event = f'{case}-{name}-event'
    add('practice_event', id=event, common_event_key=key, event_at=day, date_precision='day',
        date_unknown_reason=None, title=title, scope_context=context, occurrence_basis=basis)
    refs = [f'{case}-{item}-p' for item in items]
    for item, pid in zip(items, refs):
        stage = 'result' if item.endswith(('result', 'notice')) else 'action'
        add('practice_event_evidence', event_id=event, passage_id=pid, stage=stage,
            supported_point=points[pid], concrete_basis=context, limitation=bounds, epistemic_type='claim')
        add('practice_evidence_assessment', event_id=event, passage_id=pid, stage=stage, basis_kind='document')
    add('practice_candidate', id=f'{case}-{name}-unmatched', scope_id=scope, event_id=event,
        relation_id=None, state='unmatched', reason=bounds, passage_ids=json.dumps(refs))

snapshot = read(Path('data/releases') / package['base_release'] / 'records.json')
for entry in entries:
    rows = snapshot.setdefault(entry['kind'], [])
    if entry['values'] not in rows:
        rows.append(entry['values'])
for table, rows in records.items():
    target = snapshot.setdefault(table, [])
    target.extend(row for row in rows if row not in target)
rules.validate_practices(snapshot)
targets = rules.practice_review_package_targets(
    snapshot, records, {row['values']['id'] for row in entries if row['kind'] == 'passage'}, party_id=party)
passages = {row['id']: row for row in snapshot['passage']}
reviews = review['practice_source_review']
prior = {(row['subject_kind'], row['subject_id']) for row in reviews}
assert prior <= targets.keys()
for (kind, identity), (ids, _) in sorted(targets.items()):
    if (kind, identity) in prior:
        continue
    inspected = [passages[pid] for pid in sorted(ids)]
    supported = [points[pid] for pid in sorted(ids) if pid in points]
    assert supported, identity
    reviews.append(dict(subject_kind=kind, subject_id=identity, reviewer_kind='agent', reviewed_at=now,
                        source_version_ids=json.dumps(sorted({row['version_id'] for row in inspected})),
                        passage_ids=json.dumps([row['id'] for row in inspected]),
                        inspected_sections=json.dumps(sorted({row['section'] for row in inspected}), ensure_ascii=False),
                        supported_claim=' '.join(supported), limitations=bounds, result='reviewed',
                        reason=f'{kind} türündeki {identity} kaydının dayandığı pasajlar ayrı ayrı okundu.'))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
refs = [{key: row[key] for key in ('subject_kind', 'subject_id')} for row in reviews]
for payload in (package, review):
    payload['source_review_refs'] = refs
for suffix, payload in (('draft', package), ('review-draft', review)):
    with (checks / f'encu-decisions-{suffix}.json').open('x') as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
print('EMEP_ENCU_SEMANTIC_OK', len(records['practice_event']), len(records['practice_relation']))
