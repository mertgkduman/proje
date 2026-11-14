"""Build review candidates only; these files are not a publication input."""
import datetime
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text

base = Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
pdf = Path('data/objects/6718b7ca1b2997d0d1f0e52999c8c5ce852af648be7e83cb26c5a7eef060805c/original.pdf')
version = '0209-saadet-current-program-v1'
pages = [pdf_page_text(pdf, n) for n in range(70)]
inventory = json.loads((base / '03-11-line-inventory-draft.json').read_text())
sections = {s['id']: s['section'] for s in inventory['sections']}
topics = {v['topic_id']: v for r in json.loads(Path('data/comparisons/03-taxonomy.json').read_text())['records']
          if r['kind'] == 'comparison_topic' and (v := r['values'])['domain'] == 'program'}
specs = defaultdict(list)
for index, line in enumerate((base / '03-11-specs.tsv').read_text().splitlines(), 1):
    page, topic, kind, anchor, summary = line.split('|')
    page = int(page)
    text = pages[page - 1]
    match = re.search(re.escape(anchor).replace(r'\ ', r'\s+'), text, re.IGNORECASE)
    if not match:
        raise ValueError((page, topic, anchor))
    tail = re.search(r'\.(?=\s|$)', text[match.end():])
    end = match.end() if anchor.endswith('.') else match.end() + tail.end() if tail else match.end()
    line_info = max((x for x in inventory['lines'] if x['pdf_page_index'] == page - 1 and x['offset'] <= match.start()), key=lambda x: x['offset'])
    specs[topic].append(dict(index=index, page=page, kind=kind, quote=text[match.start():end].strip(),
                             summary=summary, owner=line_info['owner'], section=sections.get(line_info['section_id'], 'Program')))

absence = {}
for line in (base / '03-11-absence-draft.tsv').read_text().splitlines():
    topic, question, context = line.split('|')
    absence[topic] = (question, context)
assert set(topics) == set(specs) | set(absence)
assert not set(specs) & set(absence)
records = {1: [], 2: []}
decisions = {1: [], 2: []}
equivalent = {}
now = datetime.datetime.now(datetime.timezone.utc).isoformat()

def add(part, kind, values):
    records[part].append({'kind': kind, 'values': values})

def semantic(part, kind, subject, reason, passage_ids):
    item = dict(subject_kind=kind, subject_id=subject, reviewer_kind='agent', reviewed_at=now,
                result='reviewed', reason=reason)
    add(part, 'comparison_semantic_review', item)
    decisions[part].append({**item, 'passage_ids': passage_ids})

def add_field(part, topic, row_id, spec, index, context=False, question=None):
    tag = f'0311-saadet-p{part}-{index:03d}-{topic}'
    p, f, s, q, pair = (tag + x for x in ('-p', '-f', '-s', '-q', '-pair'))
    text = spec['summary'] if not context else f'Programın ilgili bağlamında: {spec["summary"]} İncelenen nüshada {question} hakkında açık ifade saptanmadı; bu bağlam dar soruya olumlu yanıt değildir.'
    reason = (f'{spec["section"]} bölümü, PDF ve basılı sayfa {spec["page"]}: '
              f'{spec["summary"]} Bu ifade parti programındaki yaklaşım veya öneridir; '
              'gerçekleşmiş uygulama ve bütün nüsha için yürürlük tarihi olarak yorumlanmadı.')
    add(part, 'passage', dict(id=p, version_id=version, exact=spec['quote'], prefix=None, suffix=None,
                              article=None, section=spec['section'], pdf_page_index=spec['page']-1,
                              printed_page=str(spec['page'])))
    key = (part, row_id, spec['kind'], text)
    if key in equivalent:
        prior_summary, prior_decision = equivalent[key]
        add(part, 'finding_evidence', dict(finding_id=prior_summary, passage_id=p, role='support'))
        prior_decision['passage_ids'].append(p)
        return
    for fid, body, provenance, role in ((s, text, 'summary', 'support'), (q, spec['quote'], 'quote', 'quotation')):
        add(part, 'finding', dict(id=fid, party_id='saadet', heading='Program', pair_id=pair,
                                  text=body, provenance=provenance, epistemic_type='claim'))
        add(part, 'finding_evidence', dict(finding_id=fid, passage_id=p, role=role))
        add(part, 'review', dict(id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent',
                                 reviewed_at=now, result='reviewed', reason=reason))
    condition = ('Ülkede doğmuş, ülke için çalışmış ve vergi ödemiş vatandaşlar'
                 if topic == 'temel-yurttaslik-geliri' and spec['kind'] == 'instrument' else None)
    add(part, 'comparison_field', dict(id=f, row_id=row_id, field=spec['kind'], summary_finding_id=s,
                                       quote_finding_id=q, condition_key=condition))
    links = [p]
    if topic == 'demokrasi-katilim' and spec['page'] == 34:
        preceding = pages[32]
        start = preceding.index('Çevre konusunda toplumsal')
        excerpt = re.sub(r'\n33\s*$', '', preceding[start:]).strip()
        prev_id = tag + '-previous'
        add(part, 'passage', dict(id=prev_id, version_id=version, exact=excerpt, prefix=None, suffix=None,
                                  article=None, section='2.3.4 Çevre', pdf_page_index=32, printed_page='33'))
        add(part, 'finding_evidence', dict(finding_id=s, passage_id=prev_id, role='support'))
        links.append(prev_id)
        reason += ' İfade önceki PDF sayfasından devam eder; iki sayfa birlikte değerlendirilmiştir.'
    semantic(part, 'comparison_field', f, reason, links)
    equivalent[key] = (s, decisions[part][-1])

topic_owner = {topic: entries[0]['owner'] for topic, entries in specs.items()}
# Consumer awareness occurs in the part-1 civil-society section but is an
# economic consumer topic reviewed and delivered with part 2.
topic_owner['tuketici-haklari'] = 2
for topic, entries in specs.items():
    part = topic_owner[topic]
    row = f'0311-saadet-{topic}'
    level = topics[topic]['applicable_levels']
    organ = 'Program'
    if topic == 'demokrasi-katilim':
        row, level, organ = '03-v2-saadet-demokrasi', 'ulusal ve yerel', 'Siyasal katılım'
    elif topic == 'temel-yurttaslik-geliri':
        row, level, organ = '03-v2-saadet-temel-yurttaslik-geliri', 'ulusal', 'Gelir desteği'
    add(part, 'comparison_row', dict(id=row, topic_id=topic, taxonomy_version=2, party_id='saadet', level=level,
        organ=organ, version_id=version, alternative_group=None, source_role='program', state='evidence',
        scope_id=None, missing_id=None, selection_reason='Partinin 03 Kasım 2019 kapak tarihli erişilebilir program nüshası; bütün içerik için yürürlük tarihi bilinmiyor.'))
    for spec in entries:
        add_field(part, topic, row, spec, spec['index'])

for n, (topic, (question, context_topic)) in enumerate(absence.items(), 1):
    spec = specs[context_topic][0]
    if topic == 'temiz-enerji-gecisi':
        anchor = 'Hidrolik enerji imkânlarının, rüzgâr, güneş ve jeotermal'
        match = re.search(re.escape(anchor).replace(r'\ ', r'\s+'), pages[20])
        end = re.search(r'\.(?=\s|$)', pages[20][match.end():])
        spec = dict(index=0, page=21, kind='instrument', owner=2, section='2.2.6 Enerji',
                    quote=pages[20][match.start():match.end()+end.end()].strip(),
                    summary='Hidrolik, rüzgâr, güneş ve jeotermal enerji yatırımlarının ekolojik ve toplumsal hassasiyet gözetilerek desteklenmesi önerilir.')
    part = spec['owner']
    key = f'0311-saadet-scope-{topic}'
    reason = f'Bu nüshanın 1–70. PDF sayfaları {question} açısından incelendi; söz konusu dar soruda açık ifade saptanmadı. Sonuç yalnız incelenen nüsha ve bu soruyla sınırlıdır.'
    add(part, 'comparison_review_scope', dict(id=key, party_id='saadet', version_id=version,
        sections='03 Kasım 2019 kapak tarihli program nüshasının PDF 1–70. sayfaları', query_terms=question,
        reviewed_at=now, result='no_explicit_statement', reason=reason))
    level = topics[topic]['applicable_levels']
    add(part, 'comparison_row', dict(id=key+'-row', topic_id=topic, taxonomy_version=2, party_id='saadet',
        level=level, organ='Program', version_id=version, alternative_group=None, source_role='program',
        state='no_explicit_statement', scope_id=key, missing_id=None, selection_reason=reason))
    pid = f'0311-saadet-p{part}-{200+n:03d}-{topic}-context-p'
    add(part, 'passage', dict(id=pid, version_id=version, exact=spec['quote'], prefix=None, suffix=None,
        article=None, section=spec['section'], pdf_page_index=spec['page']-1, printed_page=str(spec['page'])))
    semantic(part, 'comparison_review_scope', key, reason + ' İlişkili pasaj dar soruya olumlu yanıt değildir.', [pid])

backfill = {1: [], 2: []}
backfill_specs = [
    (41, 'Ülkemizde doğmuş, ülkemiz için çalışmış, vergi ödemiş', 'Temel Vatandaşlık Geliri kapsamı',
     'Doğum, çalışma ve vergi ödeme koşulları; yalnız gelirsizlik tanımına veya koşulsuz evrensel ödemeye eşitlenmez.'),
    (27, 'Zorunlu eğitim yerine kademeli eğitim sistemine geçilecektir.', 'Eğitim sisteminde zorunluluk ve kademelendirme',
     'Zorunlu eğitim yerine kademeli eğitim sistemi önerisi; eğitim hizmetlerine erişimden ayrı sorudur.'),
    (28, 'Öğretmen alımlarında mülakat uygulaması kaldırılacaktır.', 'Öğretmen atamasında mülakat',
     'Öğretmen alımında mülakatın kaldırılması; öğrenci erişimine ilişkin bir sonuç değildir.'),
    (30, 'Çalışma barışını bozan adaletsiz performans sistemi', 'Sağlıkta performans sistemi',
     'Sağlık çalışanlarının performans düzeninin adalet için yeniden düzenlenmesi; ücretsiz hizmet anlamına gelmez.'),
    (31, 'Tıbbi teknolojide tıbbi cihaz, ilaç ve aşıda dışa bağımlılık', 'Tıbbi cihaz, ilaç ve aşı üretimi',
     'Dışa bağımlılığın kaldırılması hedefi; ücretsiz ilaç önerisi değildir.'),
    (21, 'Hidrolik enerji imkânlarının, rüzgâr, güneş ve jeotermal', 'Enerjide kaynak çeşitlendirme ve yenilenebilir kaynaklar',
     'Yenilenebilir kaynaklarda ekolojik ve toplumsal hassasiyet; fosilden çıkış tarihi veya net sıfır değildir.'),
    (41, 'Çalışanların işten çıkarma veya isteğe bağlı işten ayrılma', 'Kıdem tazminatının korunması',
     'İşten çıkarma veya isteğe bağlı ayrılma durumunda birikmiş kıdem tazminatı güvencesi.'),
    (36, 'Yerel ekonomik kaynakların ve potansiyelin değerlendirilerek', 'Yerel ekonomik gelişme programı',
     'Yerel kaynaklar ve bölgesel gelişme aracı; yerel demokratik katılımla özdeşleştirilmez.'),
    (27, 'Öğrenciyi merkeze alan alternatif okul modelleri', 'Öğrenci merkezli alternatif okul modelleri',
     'Eğitim modeli; erişimin ücretlendirilmesiyle eşitlenmez. Aynı öneri 28. sayfada da tekrarlanır.'),
    (28, 'Yeni eğitim sisteminde öğrenci merkeze alınacak', 'Öğrenci merkezli alternatif okul modelleri',
     'Eğitim modeli; erişimin ücretlendirilmesiyle eşitlenmez. Aynı öneri 27. sayfada da tekrarlanır.'),
    (21, 'Enerji temininde kaynak çeşitlendirmesini için yerli', 'Enerjide kaynak çeşitlendirme ve yenilenebilir kaynaklar',
     'Yenilenebilir kaynakları değerlendirme önerisi; fosilden çıkış tarihi veya net sıfır değildir.'),
    (27, 'Müfredatzihniyet olarak milletimizin değerleriyle', 'Eğitim müfredatının içeriği ve düzenlenmesi',
     'Program müfredatın toplumun değerleriyle uyumlu ve bilimsel bir niteliğe kavuşturulmasını önerir.'),
    (27, 'Temel eğitim müfredatı çağın gereklerine', 'Eğitim müfredatının içeriği ve düzenlenmesi',
     'Temel eğitim müfredatının ihtiyaç ve öğrenci kazanımlarına göre yeniden oluşturulması ayrıca önerilir.'),
]
for n, (page, anchor, name, scope) in enumerate(backfill_specs, 1):
    text = pages[page - 1]
    match = re.search(re.escape(anchor).replace(r'\ ', r'\s+'), text, re.IGNORECASE)
    if not match:
        raise ValueError(('backfill', page, anchor))
    tail = re.search(r'\.(?=\s|$)', text[match.end():])
    end = match.end() if anchor.endswith('.') else match.end() + tail.end()
    line = max((x for x in inventory['lines'] if x['pdf_page_index'] == page - 1 and x['offset'] <= match.start()), key=lambda x: x['offset'])
    part, pid = line['owner'], f'0311-saadet-backfill-{n:02d}-p'
    add(part, 'passage', dict(id=pid, version_id=version, exact=text[match.start():end].strip(),
        prefix=None, suffix=None, article=None, section=sections.get(line['section_id'], 'Program'),
        pdf_page_index=page-1, printed_page=str(page)))
    existing = next((b for b in backfill[part] if b['topic'] == name), None)
    if existing:
        existing['passage_ids'].append(pid)
        existing['scope'] += ' ' + scope
    else:
        backfill[part].append(dict(topic=name, source_version=version, passage_ids=[pid], backfill_plan='03-14', scope=scope))

prefix = os.environ.get('SAAD_PROGRAM_DRAFT_PREFIX', '/tmp/03-11')
for part in (1, 2):
    out = {'contract_version': 1, 'taxonomy_version': 2, 'stage': 'partial', 'status': 'in_progress',
           'note': 'Saadet Partisi 03 Kasım 2019 kapak tarihli 70 sayfalık program nüshası; yürürlük zinciri bilinmiyor.',
           'backfill_candidates': backfill[part], 'records': records[part]}
    Path(f'{prefix}-program-{part}-review-draft.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
    Path(f'{prefix}-semantic-{part}-review-draft.json').write_text(json.dumps(decisions[part], ensure_ascii=False, indent=2)+'\n')
    print('part', part, 'records', len(records[part]), 'decisions', len(decisions[part]))
cross = [dict(topic=topic, topic_owner=topic_owner[topic], section_owner=e['owner'], section=e['section'],
              pdf_page=e['page'], candidate_index=e['index'], status='reviewed',
              reason='İlgili bölümün kaynak ifadesi ve konu kapsamı birlikte incelendi; gerçek pasaj kendi kanonik alanında korunur.')
         for topic, entries in specs.items() for e in entries if e['owner'] != topic_owner[topic]]
(base / '03-11-cross-review-draft.json').write_text(json.dumps(cross, ensure_ascii=False, indent=2)+'\n')
print('cross-section candidate queue', len(cross))
