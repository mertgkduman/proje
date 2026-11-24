"""Build the 1/284, 7414 and 7490 comparison from the reviewed Demokrat pair."""

import json
import sys
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import html_source_text, pdf_page_text
import uygulamalar as rules

checks = Path(__file__).resolve().parent
working = Path('data/practices')
source_root = working / 'sources' / 'demokrat'
case = '0412-budget-7414'
party = 'demokrat'
topic = 'maliye-vergi'
now = datetime.now(timezone.utc).isoformat(timespec='seconds')


def read(path):
    return json.loads(path.read_bytes())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


preflight = sys.argv[1:] == ['--preflight']
assert preflight or not sys.argv[1:]
if preflight:
    package_path = checks / 'fuel-4496-draft.json'
    review_path = checks / 'fuel-4496-review-draft.json'
else:
    package_path = working / '04-demokrat.json'
    review_path = working / '04-demokrat-review.json'
assert (digest(package_path), digest(review_path)) == (
    '159f22b2a895908464f9d63f79407601db385126def0e6fe06790261eb62a448',
    '2b7d003517b41b3e833a8d8a89392ab367c64eb9f90a45dceb8110e3a1e24fa9',
)
package, review = read(package_path), read(review_path)
entries, records = package['entries'], package['practice_records']
assert (len(records['practice_event']), len(records['practice_relation']), len(records['practice_closure'])) == (57, 46, 0)
source_path = checks / 'budget-7414-source-draft.json'
assert digest(source_path) == '7057e89a1c33dbf6fe5ac70764899e4ef455a27e935ff43acfd5359535c5d1ac'
new_entries = read(source_path)['entries']
entries.extend(new_entries)
versions = {r['values']['id']: r['values'] for r in new_entries if r['kind'] == 'document_version'}
source_passages = {r['values']['id']: r['values'] for r in new_entries if r['kind'] == 'passage'}


def add(table, **values):
    records[table].append(values)


def insert(table, **values):
    entries.append({'kind': table, 'values': values})


def pid(suffix):
    return f'{case}-{suffix}-p'


for suffix, role, section, page, exact in [
    ('party151-focus', 'party151', 'Uysal’ın 21 Haziran tarihli ödenek eleştirisi', None,
     "40,4 oranında artırarak 141.453 TL'ye"),
    ('proposal-filing', 'proposal', '20 Haziran sunuş kaşesi ve 1/284', 0,
     'Tarih: 20 Haziran 2022 Esas No: 1/284'),
    ('lawreg-publication', 'lawreg', 'TBMM sicilinde 31889 sayılı Resmî Gazete yayımı', None, '07/07/2022'),
    ('adopted-effective', 'adopted', '7414 madde 3, yayım günü yürürlük', None,
     'Bu Kanun yayımı tarihinde yürürlüğe girer.'),
    ('final-gap', 'final', '7490 madde 3 fıkra 2, 2022 net gider fazlası', None,
     '142.660.010.115,62 Türk lirasıdır.'),
]:
    version = f'{case}-{role}-v1'
    source = source_root / versions[version]['original_path']
    haystack = html_source_text(source.read_bytes()) if page is None else pdf_page_text(source, page)
    assert exact in haystack, (role, suffix)
    row = dict(id=pid(suffix), version_id=version, exact=exact, prefix=None, suffix=None,
               article=None, section=section, pdf_page_index=page, printed_page=None)
    insert('passage', **row)
    source_passages[row['id']] = row

scopes = {row['research_kind']: row['id'] for row in records['practice_scope_v2'] if row['topic_id'] == topic}
assert {'statement', 'event'} <= scopes.keys()
for version, row in versions.items():
    is_party_source = version in {f'{case}-party149-v1', f'{case}-party151-v1'}
    selected = ('statement', 'event') if is_party_source else ('event',)
    sections = sorted(p['section'] for p in source_passages.values() if p['version_id'] == version)
    url = row['original_url']
    for lane in selected:
        scope = scopes[lane]
        attempt = f'{version}-{lane}-reading'
        add('practice_scope_source', scope_id=scope, version_id=version,
            inspected_sections=json.dumps(sections, ensure_ascii=False), inspected_at=now)
        add('practice_attempt_v2', id=attempt, scope_id=scope, attempted_at=now,
            query=url, url=url, result='examined', reason='Belgenin ilgili ek bütçe veya kesin hesap pasajları okundu.',
            source_version_id=version)
        add('practice_lead', id=f'lead-{attempt}', scope_id=scope, url=url,
            relevance_reason='1/284 ek bütçe dosyasının söylem, sunuş, kabul veya kesin hesap bağlamı.',
            state='examined', attempt_ids=json.dumps([attempt]))


def finding(suffix, text, provenance, heading, pair, refs):
    ident = f'{case}-{suffix}'
    insert('finding', id=ident, party_id=party, heading=heading, pair_id=pair,
           text=text, provenance=provenance, epistemic_type='claim')
    insert('review', id=f'review-{ident}', kind='finding', subject_id=ident, reviewer_kind='agent',
           reviewed_at=now, result='reviewed', reason='Ek bütçe metni, oy cetveli veya açıklama ilgili pasajlarla okundu.')
    for ref in refs:
        insert('finding_evidence', finding_id=ident, passage_id=pid(ref), role='support')
        insert('verification', finding_id=ident, passage_id=pid(ref), checked_at=now, result='confirmed',
               reason='Belgede bu sayı, dönem veya işlem doğrudan yer alır.')
    return ident


statement = f'{case}-statement'
summary = finding('statement-summary',
    'Gültekin Uysal, 21 Haziran 2022’de Meclise sunulan ek bütçe teklifini eleştirdi. Cumhurbaşkanının aylığının yüzde 40,4 artırılarak 141.453 TL’ye çıkacağını söyledi.',
    'summary', 'Maliye ve vergi', statement, ('party151-focus', 'party151-allocation'))
quote = finding('statement-quote', source_passages[pid('party151-focus')]['exact'],
                'quote', 'Maliye ve vergi', statement, ('party151-focus',))
base_row = next(row for row in records['practice_statement'] if row['id'] == '0412-tax-deferral-2026-statement')
add('practice_statement', id=statement, party_id=party, topic_id=topic, taxonomy_version=4,
    summary_finding_id=summary, quote_finding_id=quote, statement_at='2022-06-21', date_precision='day',
    version_id=f'{case}-party151-v1', period_basis='Demokrat Parti Basın Merkezinin 21 Haziran tarihli sayfası.',
    comparison_row_id=base_row['comparison_row_id'],
    uncertainty_reason='Konuşmacının aylık hesabı ile imzalı teklifin bütçe tertibi yüzdesi farklı ölçüler.')

bounds = ('Ödenek kararı ve fiilî aylık ödeme ayrı. Mali etkilerin veya Demokrat Parti’nin karar sonucuna katkısının kanıtı açık. '
          'Çevik’in metni 29 Haziran tarihli, parti sayfası 30 Haziran. 29 Haziran içindeki saat sırası açık.')
points = {
    'proposal-filing': ('action', 'İmzalı teklifin Meclis kaşesinde 20 Haziran 2022 ve 1/284 yer alıyor.'),
    'register-number': ('action', 'TBMM teklif sicili 1/284 dosyasını gösteriyor.'),
    'proposal-percent': ('action', 'İmzalı teklif 01.08 Cumhurbaşkanı Ödeneği için yüzde 20,2 ek başlangıç ödeneği öngörüyordu.'),
    'proposal-total': ('action', 'Teklif belirli bütçe tertiplerinde toplam 880.474.775.000 TL ek ödenek içeriyordu.'),
    'proposal-revenue': ('action', 'Teklif genel bütçe gelir tahminini 1.080.515.421.000 TL artırmayı öngörüyordu.'),
    'debate-chair': ('action', 'Kürsüde okunan sayım 383 kullanılan, 266 kabul ve 117 ret.'),
    'roll-accept': ('result', 'Kesin cetvelde kabul sayısı 265.'),
    'roll-reject': ('result', 'Kesin cetvelde ret sayısı 117.'),
    'roll-duplicate': ('result', 'Kesin cetvelde iki mükerrer oy ayrı kaydedildi.'),
    'roll-uysal': ('result', 'Afyonkarahisar Gültekin Uysal’ın Demokrat Parti satırında KATILMADI yazıyor.'),
    'roll-enginyurt': ('result', 'Ordu Cemal Enginyurt’un Demokrat Parti satırında KATILMADI yazıyor.'),
    'adopted-total': ('result', '7414 madde 1 fıkra 1, 880.474.775.000 TL tutarındaki belirli ilave ödenekleri kabul etti.'),
    'adopted-exception': ('result', '7414 madde 1 fıkra 2, 01.08 Cumhurbaşkanı Ödeneğini artış kapsamının dışında bırakıyor.'),
    'adopted-percentage': ('result', 'İstisnadan sonra aynı fıkra personel ve SGK prim tertipleri için yüzde 40,5 artış kaydediyor.'),
    'lawreg-number': ('action', 'TBMM kanun sicilinde 7414 numarası kayıtlı.'),
    'lawreg-publication': ('result', '7414 sayılı kanun 7 Temmuz 2022’de 31889 sayılı Resmî Gazete’de yayımlandı.'),
    'adopted-effective': ('result', '7414’ün yürürlük hükmü yayım tarihini belirtiyor.'),
    'final-spending': ('action', '25 Aralık 2023’te kabul edilen kesin hesap kanunu 2022 net giderini 2.942.747.714.595,65 TL kaydetti.'),
    'final-revenue': ('result', '7490, 2022 net merkezi yönetim gelirini 2.800.087.704.480,03 TL kaydetti.'),
    'final-gap': ('result', '7490, 2022 net merkezi yönetim gider fazlasını 142.660.010.115,62 TL kaydetti.'),
}
case_events = {
    'filing': ('tbmm-27-5-1-284-budget-filing', '2022-06-20', '1/284 ek bütçe teklifinin Başkanlığa sunulması',
               '20 Haziran 2022 tarihli imzalı Cumhurbaşkanlığı teklifi ve TBMM geliş kaydı.',
               ('proposal-filing', 'register-number', 'proposal-percent', 'proposal-total', 'proposal-revenue')),
    'adoption': ('tbmm-27-5-109-1-284-law-7414', '2022-06-29', '1/284 ek bütçe teklifinin 7414 sayılı kanun olarak kabulü',
                 '29 Haziran 2022 açık oylaması ve 7 Temmuz 2022 yayımı. 01.08 ödenek istisnası kabul metninde.',
                 ('debate-chair', 'roll-accept', 'roll-reject', 'roll-duplicate', 'roll-uysal', 'roll-enginyurt',
                  'adopted-total', 'adopted-exception', 'adopted-percentage', 'lawreg-number', 'lawreg-publication',
                  'adopted-effective')),
    'accounts': ('tbmm-law-7490-central-accounts-2022', '2023-12-25', '7490 kesin hesap kanununda 2022 merkezi yönetim hesabı',
                 '25 Aralık 2023 kabulü. 2022 yılının net gider, gelir ve gider fazlası kanunda yer alıyor.',
                 ('final-spending', 'final-revenue', 'final-gap')),
}
relation = f'{case}-adoption-relation'
reasons = {
    'filing': 'Başkanlığa sunuş, Demokrat Parti’nin 21 Haziran açıklamasından önce gerçekleşti.',
    'adoption': '21 Haziran açıklaması ve 29 Haziran nihai kanun aynı ek bütçe dosyasını ve 01.08 tertibini ele alıyor.',
    'accounts': '7490 bütün yılın kesin hesabını veriyor. 21 Haziran açıklamasındaki kişisel aylık ve ek bütçe alt kalemleri bu toplamlardan tespit edilemiyor.',
}
for name, (key, day, title, basis, refs) in case_events.items():
    event = f'{case}-{name}-event'
    add('practice_event', id=event, common_event_key=key, event_at=day, date_precision='day',
        date_unknown_reason=None, scope_context='2022 merkezi yönetim ek bütçesi ve kesin hesabı',
        title=title, occurrence_basis=basis)
    for suffix in refs:
        stage, point = points[suffix]
        add('practice_event_evidence', event_id=event, passage_id=pid(suffix), stage=stage,
            supported_point=point, concrete_basis=source_passages[pid(suffix)]['section'],
            limitation=bounds, epistemic_type='claim')
        add('practice_evidence_assessment', event_id=event, passage_id=pid(suffix), stage=stage, basis_kind='document')
    add('practice_candidate', id=f'{case}-{name}-candidate', scope_id=scopes['event'], event_id=event,
        relation_id=relation if name == 'adoption' else None, state='eligible' if name == 'adoption' else 'unmatched',
        reason=reasons[name], passage_ids=json.dumps([pid(ref) for ref in refs]))

result = finding('adoption-result',
    '29 Haziran’da teklif 7414 sayılı kanun olarak kabul edildi. 7 Temmuz’da yayımlanan kanunun 1. maddesi Cumhurbaşkanı Ödeneği tertibini yüzde 40,5 artış kapsamının dışında bıraktı. Kesin cetvelde iki Demokrat Parti milletvekili KATILMADI.',
    'summary', 'Belgelenmiş uygulamalar', f'{case}-adoption-result',
    ('lawreg-number', 'lawreg-publication', 'adopted-exception', 'adopted-percentage', 'roll-uysal', 'roll-enginyurt'))
comparison = finding('adoption-comparison',
    'Uysal’ın 21 Haziran açıklaması aylık hakkında yüzde 40,4 ve 141.453 TL ifadesini içeriyor. İmzalı 1/284 metni 01.08 bütçe tertibi için yüzde 20,2 öneriyordu. Nihai 7414 metni bu kalemi artış dışında tuttu.',
    'summary', 'Belgelenmiş uygulamalar', f'{case}-adoption-comparison',
    ('party151-focus', 'proposal-percent', 'adopted-exception', 'adopted-percentage'))
add('practice_relation', id=relation, party_id=party, topic_id=topic, scope_id=scopes['event'],
    statement_id=statement, event_id=f'{case}-adoption-event', target_finding_id=summary,
    result_finding_id=result, explanation_finding_id=comparison,
    comparability_reason='Parti açıklaması ve nihai metin 1/284 ek bütçesindeki 01.08 Cumhurbaşkanı Ödeneğine değiniyor.',
    temporal_context='20 Haziran 2022 teklif, 21 Haziran parti açıklaması, 29 Haziran kabul, 7 Temmuz yayım ve yürürlük.',
    authority_context='Cumhurbaşkanlığı teklif sahibi, TBMM Genel Kurulu kabul yetkisine sahip. İki Demokrat Parti satırında KATILMADI kayıtlı.',
    uncertainty_reason=bounds)

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
claims = {ref: row['section'] for ref, row in source_passages.items()}
claims.update({pid(suffix): point for suffix, (_, point) in points.items()})
assert prior <= targets.keys()
for (kind, ident), (ids, _) in sorted(targets.items()):
    if (kind, ident) in prior:
        continue
    inspected = [passages[ref] for ref in sorted(ids)]
    material = [claims[ref] for ref in sorted(ids)]
    reviews.append(dict(subject_kind=kind, subject_id=ident, reviewer_kind='agent', reviewed_at=now,
                        source_version_ids=json.dumps(sorted({row['version_id'] for row in inspected})),
                        passage_ids=json.dumps([row['id'] for row in inspected]),
                        inspected_sections=json.dumps(sorted({row['section'] for row in inspected}), ensure_ascii=False),
                        supported_claim=' '.join(material), limitations=bounds, result='reviewed',
                        reason=f'{kind} türündeki {ident} kaydına bağlı bütçe pasajları okundu.'))
rules.validate_practice_source_review(snapshot, reviews, party_id=party, target_keys=set(targets))
refs = [{key: row[key] for key in ('subject_kind', 'subject_id')} for row in reviews]
for payload in (package, review):
    payload['source_review_refs'] = refs
if not preflight:
    for suffix, payload in (('draft', package), ('review-draft', review)):
        with (checks / f'budget-7414-{suffix}.json').open('x') as fh:
            json.dump(payload, fh, ensure_ascii=False, indent=2)
            fh.write('\n')
print('DEMOCRAT_BUDGET_7414_SEMANTIC_OK', len(records['practice_event']), len(records['practice_relation']))
