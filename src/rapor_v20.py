"""Kapalı kayıt snapshot'ından güvenli, sekmeli HTML üretir."""
from collections import defaultdict
from html import escape, unescape
import json
from pathlib import Path
from urllib.parse import urlsplit
from dosyalar import SOURCE_TYPE_LABELS
from kaynaklar import attribution_text


RENDERER_VERSION = 20
STYLE = Path(__file__).with_name('rapor_v20.css').read_text(encoding='utf-8')
HEADINGS = (
    ('kurulus', 'Kuruluş'),
    ('tuzuk', 'Tüzük'),
    ('program', 'Program'),
    ('soylem-uygulama', 'Söylem ve uygulama'),
    ('finansman', 'Finansman ve harcamalar'),
)
PRESENTATION_ORDER = ('yeni-parti', 'tip', 'dem', 'iyi', 'yeni-yol', 'dbp', 'emep', 'saadet', 'demokrat')
CODE_LABELS = {
    'institution': 'kurumsal', 'institutional': 'kurumsal', 'authorized': 'yetkili temsilci',
    'individual': 'bireysel', 'eligible': 'uygun', 'excluded': 'kapsam dışı',
    'unverified': 'doğrulanamadı', 'examined': 'incelendi', 'failure': 'erişilemedi',
    'inconclusive': 'doğrulanamadı', 'no_result': 'sonuç bulunamadı', 'results': 'sonuç bulundu',
    'registry': 'Birincil belge', 'official': 'Birincil belge', 'journalism': 'Gazetecilik', 'news': 'Gazetecilik',
    'unknown': 'türü doğrulanmadı', 'party': 'Birincil belge',
    'academic': 'Akademik çalışma', 'independent_report': 'Bağımsız rapor',
    'day': 'gün', 'month': 'ay', 'year': 'yıl', 'reviewed': 'incelendi', 'pending': 'bekliyor',
}


def esc(value):
    return escape(str(value) if value is not None else '', quote=True)


def web_url(value):
    parsed = urlsplit(value)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Geçersiz URL')
    return esc(value)


def date_label(value):
    if not value:
        return 'Belirtilmemiş'
    date = value[:10].split('-')
    return '.'.join(reversed(date)) if len(date) == 3 else value


def time_tag(value):
    return f'<time datetime="{esc(value)}">{esc(date_label(value))}</time>' if value else 'Belirtilmemiş'


def code_label(value):
    return esc(CODE_LABELS.get(value, 'Belirtilmemiş'))


def version_source_label(version, attribution, fallback=''):
    """Identify this source version using its own publisher and version label."""
    attribution = attribution or {}
    publisher = attribution.get('publisher') or attribution.get('social_handle') or attribution.get('author')
    label = version.get('version_label') or ('Sürüm belirtilmemiş' if publisher else fallback or 'Sürüm belirtilmemiş')
    if not publisher:
        return fallback + ' · ' + label if fallback and fallback != label else label
    if publisher.casefold() in label.casefold():
        return label
    return publisher + ' · ' + label


def finding_text(finding, legacy_html=False):
    value = esc(unescape(finding['text'])) if finding['provenance']=='quote' and legacy_html else esc(finding['text'])
    if finding['provenance'] == 'quote':
        return 'quote', f'“{value}”'
    return 'summary', value


def group_party_sources(data, passages, versions, documents):
    groups = defaultdict(set)
    for row in data.get('dossier_source', []):
        for p in passages.values():
            if p['version_id'] == row['version_id']:
                groups[row['party_id'], row['heading']].add(p['id'])
    findings = {f['id']: f for f in data['finding']}
    for e in data['finding_evidence']:
        f = findings[e['finding_id']]
        if f['heading'] in dict((h, k) for k, h in HEADINGS):
            groups[f['party_id'], f['heading']].add(e['passage_id'])
    for p in passages.values():
        owner = documents[versions[p['version_id']]['document_id']]['party_id']
        if not any(p['id'] in ids for (party, _), ids in groups.items() if party == owner):
            groups[owner, 'Kuruluş'].add(p['id'])
    return groups


def render_version_history(version, data, versions, citation, findings, evidence, format_finding, attributions):
    siblings = [v for v in versions.values() if v['document_id'] == version['document_id']]
    result = [f'<details id="version-history-{esc(version["id"])}"><summary>Belge sürüm geçmişi</summary>']
    if len(siblings) == 1:
        result.append('<p>Arşivde tek sürüm var.</p>')
    for v in sorted(siblings, key=lambda x: x['id']):
        target = f' id="version-{esc(v["id"])}"' if v['id'] == version['id'] else ''
        result.append(f'<div{target}>{esc(version_source_label(v, attributions.get(v["id"])))} · {time_tag(v["document_date"])}')
        attribution=attributions.get(v['id'])
        if attribution and attribution.get('author'):
            result.append(f'<p class="metadata">Bu sürümün yazarı: {esc(attribution["author"])} · Atıf dayanağı: {esc(attribution["basis"])}</p>')
        context = next((x for x in data.get('version_context', []) if x['version_id'] == v['id']), None)
        if context:
            if context['date_precision'] == 'unknown':
                result.append(f'<p>Dönem doğrulanamadı: {esc(context["date_unknown_reason"])}</p>')
            else:
                result.append(f'<p>Dönem: {time_tag(context["period_start"])} – {time_tag(context["period_end"])} {citation(context["passage_id"])}</p>')
        else:
            result.append('<p>Dönem doğrulanmadı.</p>')
        for entry in ([context] if context else []) + [x for x in data.get('version_relation', []) if x['version_id'] == v['id']]:
            fid = entry.get('explanation_finding_id')
            if fid:
                f = findings[fid]
                for paired in findings.values():
                    if paired['pair_id'] == f['pair_id'] and paired['party_id'] == f['party_id'] and paired['heading'] == f['heading']:
                        cls, value = format_finding(paired)
                        refs = ' '.join(citation(e['passage_id']) for e in evidence[paired['id']])
                        result.append(f'<p class="{cls}">{value} {refs}</p>')
        result.append('</div>')
    return ''.join(result) + '</details>'


def render_identity_card(pid, fields, missing, evidence, citation):
    labels = (('legal_name','Resmî ad'), ('abbreviation','Kısaltma'), ('foundation_date','Kuruluş tarihi'), ('registry_key','Sicil kimliği'), ('official_site','Resmî site'))
    field_map = {f['field']: f for f in fields}
    result = [f'<div id="identity-{esc(pid)}"><h4>Temel bilgiler</h4><dl>']
    for name, label in labels:
        field = field_map.get(name)
        value = 'Henüz incelenmedi'
        if field and field['value'] is not None:
            refs = ' '.join(citation(e['passage_id']) for e in evidence[field['finding_id']])
            value = (f'<a href="{web_url(field["value"])}">{esc(field["value"])}</a>' if name=='official_site' else esc(field['value'])) + ' ' + refs
        elif field:
            m = missing[field['missing_id']]
            value = esc(m['status']) + ' · ' + esc(m['reason'])
        result.append(f'<dt>{label}</dt><dd>{value}</dd>')
    return ''.join(result) + '</dl></div>'


def render_foundation_timeline(pid, events, event_dates, findings, notes, citation, format_finding):
    result = [f'<div id="chronology-{esc(pid)}"><h4>Kuruluş kronolojisi</h4><ul>']
    for event in sorted(events, key=lambda x: (event_dates[x['event_date_id']]['event_at'] is None, event_dates[x['event_date_id']]['event_at'] or '')):
        date = event_dates[event['event_date_id']]
        f = findings[event['summary_finding_id']]
        result.append(f'<li>{time_tag(date["event_at"])} <span class="summary">{esc(f["text"])}</span> {citation(date["passage_id"])}</li>')
    result.append('</ul>')
    for note in notes:
        cls, value = format_finding(note, (note['own_passage_id'],note['related_passage_id']))
        result.append(f'<p id="identity-note-{esc(note["id"])}" class="{cls}">{value} {citation(note["own_passage_id"])} {citation(note["related_passage_id"])}</p>')
    return ''.join(result) + '</div>'


def render_report(data):
    parties = {p['id']: p for p in data['party']}
    versions = {v['id']: v for v in data['document_version']}
    documents = {d['id']: d for d in data['document']}
    passages = {p['id']: p for p in data['passage']}
    topics = {t['id']: t['label'] for t in data.get('topic', [])}
    topics.update({
        'alan-adi-org': 'Parti alan adı (.org)', 'alan-adi-orgtr': 'Parti alan adı (.org.tr)',
        'mali-denetim': 'Mali denetim', 'mali-gelir-gider': 'Gelir ve giderler',
        'pilot-program': 'Parti programı', 'pilot-tuzuk': 'Parti tüzüğü',
    })
    findings = {f['id']: f for f in data['finding']}
    evidence = defaultdict(list)
    for row in data['finding_evidence']:
        evidence[row['finding_id']].append(row)
    def format_finding(finding, passage_ids=None):
        # Legacy HTML passages are stored as raw source markup; PDF text is literal.
        if passage_ids is None:
            passage_ids=(e['passage_id'] for e in evidence[finding['id']])
        matching=[passages[pid] for pid in passage_ids if passages[pid]['exact']==finding['text']]
        legacy_html=bool(matching) and all(not versions[p['version_id']]['original_path'].endswith('.pdf') for p in matching)
        return finding_text(finding,legacy_html)
    attempts = {a['id']: a for a in data.get('attempt', [])}
    resolutions = {r['missing_id']: r for r in data.get('missing_resolution', [])}
    attributions = {r['version_id']:r for r in data.get('source_attribution',[])}
    views = {r['version_id']:r for r in data.get('archive_view',[])}
    policies=data.get('source_policy',[])
    legacy_findings=set(json.loads(policies[-1]['legacy_findings'])) if policies else set()
    missing_by_heading = defaultdict(list)
    for row in data.get('missing', []):
        if row['id'] not in resolutions:
            missing_by_heading[row['party_id'], row['heading']].append(row)

    def topic_name(value):
        return esc(topics.get(value, str(value).replace('-', ' ').capitalize()))

    def citation(pid, label='Kaynak'):
        version = versions[passages[pid]['version_id']]
        title = version_source_label(version, attributions.get(version['id']), documents[version['document_id']]['title'])
        return f'<a class="citation" href="#source-{esc(pid)}" aria-label="{esc(label)}: {esc(title)}">[{esc(label)}]</a>'

    def named_citation(pid):
        version = versions[passages[pid]['version_id']]
        title = version_source_label(version, attributions.get(version['id']), documents[version['document_id']]['title'])
        return citation(pid, title)

    grouped = group_party_sources(data, passages, versions, documents)
    source_entries = {}
    history_seen = set()
    manual_passages = {m['passage_id']: m for m in data.get('manual_passage', [])}
    for p in passages.values():
        v = versions[p['version_id']]
        d = documents[v['document_id']]
        original = web_url(v['original_url'])
        for path in (v['readable_path'], v['original_path']):
            if path.startswith('/') or '..' in path.split('/') or not path.startswith('objects/'):
                raise ValueError('Geçersiz arşiv yolu')
        source_type = esc(SOURCE_TYPE_LABELS.get(d['source_kind'], 'Türü doğrulanamadı'))
        location = p['article'] or p['section'] or p['prefix'] or p['suffix']
        metadata = [('Sürüm kimliği', esc(v['id'])), ('Belge tarihi', time_tag(v['document_date'])),
                    ('Sürüm', esc(v['version_label'] or 'Belirtilmemiş')),
                    ('Erişim', time_tag(v['accessed_at'])), ('Doğrulama', time_tag(v['verified_at']))]
        if location:
            metadata.append(('Konum', esc(location)))
        if p['pdf_page_index'] is not None:
            metadata.append(('PDF sayfası', esc(p['pdf_page_index'] + 1)))
            if p['printed_page']:
                metadata.append(('Basılı sayfa', esc(p['printed_page'])))
        if manual := manual_passages.get(p['id']):
            metadata.append(('Sayfa kontrolü', time_tag(manual['checked_at']) + ' · ' + esc(manual['reason'])))
        if v.get('date_unknown_reason'):
            metadata.append(('Belge tarihi notu', esc(v['date_unknown_reason'])))
        if attribution:=attributions.get(v['id']):
            metadata.append(('Atıf',esc(attribution_text(attribution))))
            metadata.append(('Atıf dayanağı',esc(attribution['basis'])))
        details = ''.join(f'<dt>{label}</dt><dd>{value}</dd>' for label, value in metadata)
        if v['id'] not in history_seen:
            history = render_version_history(v, data, versions, citation, findings, evidence, format_finding, attributions)
            history_seen.add(v['id'])
        else:
            history = f'<a href="#version-history-{esc(v["id"])}">Sürüm geçmişi</a>'
        reasons = ' '.join(esc(x['reason']) for x in data.get('dossier_source', []) if x['version_id'] == v['id'])
        archive=f'<a href="../../{esc(v["readable_path"])}">Arşiv kopyası</a>'
        if view:=views.get(v['id']):
            if not __import__('re').fullmatch(r'views/[0-9a-f]{32}/index\.html',view['index_path']):raise ValueError('Geçersiz arşiv görünümü yolu')
            archive=f'<a class="archive-view" href="../../{esc(view["index_path"])}">Arşiv görünümü</a>'
        source_entries[p['id']] = (
            f'<details class="source" id="source-{esc(p["id"])}">'
            f'<summary>{esc(version_source_label(v, attributions.get(v["id"]), d["title"]))} <span class="source-type">{source_type}</span> · {time_tag(v["document_date"])}</summary>'
            f'<blockquote class="quote">“{esc(p["exact"] if v["original_path"].endswith(".pdf") else unescape(p["exact"]))}”</blockquote><dl class="source-info">{details}</dl>'
            f'<p>{reasons}</p>{history}'
            f'<div class="source-links"><a href="{original}">Özgün kaynak</a>'
            f'{archive}'
            f'<a download href="../../{esc(v["original_path"])}">Belgeyi indir</a></div></details>'
        )

    known_order = {pid: i for i, pid in enumerate(PRESENTATION_ORDER)}
    scoped = sorted(data.get('scope_party', []),
                    key=lambda row: (known_order.get(row['party_id'], len(known_order)), row['approved_order']))
    party_ids = [row['party_id'] for row in scoped] or [pid for pid in parties if pid == 'yeni-parti']
    methods = data.get('method', [])
    title = 'Türkiye siyasi partileri: kaynaklı araştırma raporu'
    pieces = [
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{title}</title><style>{STYLE}</style></head><body>',
        '<a class="skip" href="#main-content">İçeriğe geç</a><div class="shell"><aside class="sidebar">',
        '<p class="sidebar-title">Parti dosyaları</p><p class="party-scroll-hint">Diğer partiler için yatay kaydırın →</p><div role="tablist" aria-label="Partiler ve karşılaştırmalı özet">',
    ]
    for i, pid in enumerate(party_ids):
        selected, tabindex = ('true', 0) if i == 0 else ('false', -1)
        pieces.append(
            f'<button type="button" role="tab" id="tab-{esc(pid)}" aria-controls="party-{esc(pid)}" '
            f'aria-selected="{selected}" tabindex="{tabindex}">{esc(parties[pid]["legal_name"])}</button>'
        )
    pieces.append('<button type="button" role="tab" id="tab-comparison" aria-controls="comparison-summary" '
                  'aria-selected="false" tabindex="-1">Karşılaştırmalı Özet</button></div>')
    if scoped or methods or attempts:
        pieces.append('<a class="method-link" href="#scope-method">Kapsam ve yöntem</a>')
    pieces.append(f'</aside><main id="main-content" tabindex="-1"><header class="masthead"><h1>{title}</h1>')
    if methods:
        pieces.append(f'<span class="cutoff">Veri kesimi {time_tag(methods[-1]["cutoff_at"])}</span>')
    pieces.append('</header>')

    def add_missing(rows, heading):
        groups = defaultdict(list)
        for m in rows:
            groups[m['topic_id'], m['status'], m['reason']].append(m['attempt_id'])
        pieces.append('<ul class="missing-list">')
        for (topic, status, reason), attempt_ids in groups.items():
            links = ' · '.join(
                f'<a href="#attempt-{esc(aid)}">{time_tag(attempts[aid]["attempted_at"])}</a>'
                for aid in dict.fromkeys(attempt_ids)
            )
            document_topic = (heading, topic) in (('Tüzük', 'pilot-tuzuk'), ('Program', 'pilot-program'))
            label = '' if document_topic else f'<strong>{topic_name(topic)}</strong> '
            if document_topic and status == 'Doğrulanamadı' and reason == (
                'Bulunan kopyanın yetkisi ve özgün sürümle ilişkisi doğrulanamadı; belge yokluğu anlamına gelmez.'
            ):
                reason = 'Kopyanın yetkisi ve özgün sürümle ilişkisi belirsiz.'
            pieces.append(f'<li>{label}<span class="status">{esc(status)}</span>'
                          f'<p>{esc(reason)}</p><span class="metadata">Araştırma kaydı {links}</span></li>')
        pieces.append('</ul>')

    def add_findings(rows):
        pieces.append('<div class="findings">')
        previous = None
        labels = {'registry': 'Sicil kaydı', 'fact': 'Olgu', 'claim': 'Beyan', 'comment': 'Yorum'}
        for f in rows:
            if not evidence[f['id']]:
                raise ValueError('Kanıtsız bulgu')
            cls, value = format_finding(f)
            passage_ids = tuple(dict.fromkeys(e['passage_id'] for e in evidence[f['id']]))
            kind = f['epistemic_type']
            shared_source = cls == 'quote' and previous == (kind, passage_ids)
            label = ''
            links = '' if shared_source else ' '.join(citation(pid) for pid in passage_ids)
            pieces.append(f'<p id="finding-{esc(f["id"])}" class="{cls}" data-finding-id="{esc(f["id"])}" '
                          f'data-provenance="{esc(f["provenance"])}" data-epistemic-type="{esc(f["epistemic_type"])}">'
                          f'{label}{value} {links}</p>')
            previous = (kind, passage_ids)
        pieces.append('</div>')

    def add_comparison_row(row, dossier=False):
        rid = esc(row['id'])
        own = 'dossier-comparison-' if dossier else 'comparison-'
        other = 'comparison-' if dossier else 'dossier-comparison-'
        label = 'Karşılaştırmaya git' if dossier else 'Parti dosyasına git'
        pieces.append(f'<article class="comparison-row" tabindex="-1" id="{own}{rid}"><h4>{esc(parties[row["party_id"]]["legal_name"])}</h4>'
                      f'<a href="#{other}{rid}">{label}</a>')
        if row['state'] == 'evidence':
            pieces.append(f'<p class="metadata">{esc(row["level"].capitalize())} · {esc(row["organ"])}</p>')
            if row['alternative_group']:
                version = versions[row['version_id']]
                pieces.append(f'<p class="metadata">Alternatif belge nüshası: {esc(version_source_label(version, attributions.get(version["id"]), documents[version["document_id"]]["title"]))} · {esc(row["selection_reason"])}</p>')
            if row['source_role'] in ('supplement', 'historical'):
                version = versions[row['version_id']]
                kind = 'Ek belge' if row['source_role'] == 'supplement' else 'Tarihsel belge'
                pieces.append(f'<p class="metadata">{kind}: {esc(version_source_label(version, attributions.get(version["id"]), documents[version["document_id"]]["title"]))}</p>')
        if row['state'] == 'not_researched':
            pieces.append('<p class="muted">Henüz incelenmedi</p>')
        elif row['state'] == 'document_missing':
            m = next(m for m in data['missing'] if m['id'] == row['missing_id'])
            pieces.append(f'<p class="muted">{esc(m["status"])} · {esc(m["reason"])} '
                          f'<a href="#attempt-{esc(m["attempt_id"])}">Araştırma kaydı</a></p>')
        elif row['state'] == 'no_explicit_statement':
            pieces.append('<p class="muted">İncelenen kapsamda açık ifade bulunmadı.</p>')
            scope = next(s for s in data['comparison_review_scope'] if s['id'] == row['scope_id'])
            version = versions[scope['version_id']]
            archive_path = views[version['id']]['index_path'] if version['id'] in views else version['readable_path']
            if (archive_path.startswith('/') or '..' in archive_path.split('/') or
                    not (archive_path.startswith('objects/') or __import__('re').fullmatch(r'views/[0-9a-f]{32}/index\.html', archive_path))):
                raise ValueError('Geçersiz arşiv yolu')
            ref = f'<a href="../../{esc(archive_path)}">İncelenen belge: {esc(version["id"])}</a>'
            pieces.append(f'<p class="metadata">İncelenen kapsam: {esc(scope["sections"])} · {esc(scope["reason"])} {ref}</p>')
        else:
            grouped_fields = {}
            for field in (x for x in data.get('comparison_field', []) if x['row_id'] == row['id']):
                pair = [findings[field[k]] for k in ('summary_finding_id', 'quote_finding_id')]
                key = (field['field'], field['condition_key'], *(
                    (f['text'], f['provenance'], f['epistemic_type']) for f in pair
                ))
                if key not in grouped_fields:
                    grouped_fields[key] = (field, [[], []])
                for index, finding in enumerate(pair):
                    refs = grouped_fields[key][1][index]
                    for item in evidence[finding['id']]:
                        if item['passage_id'] not in refs:
                            refs.append(item['passage_id'])
            for field, passage_groups in grouped_fields.values():
                field_label = {'principle':'İlke', 'target':'Hedef', 'instrument':'Önerilen araç'}.get(field['field'])
                if field_label:
                    pieces.append(f'<h5>{field_label}</h5>')
                if field['condition_key']:
                    pieces.append(f'<p class="metadata">Koşul: {esc(field["condition_key"])}</p>')
                for fid, passage_ids in zip((field['summary_finding_id'],field['quote_finding_id']), passage_groups):
                    f = findings[fid]
                    cls, value = format_finding(f, passage_ids)
                    refs = ' '.join(named_citation(pid) for pid in passage_ids)
                    pieces.append(f'<p class="{cls}">{value} {refs}</p>')
            changes = [c for c in data.get('comparison_change', []) if c['row_id'] == row['id']]
            if changes:
                pieces.append('<details><summary>Belge sürümlerindeki değişiklikler</summary>')
                for change in sorted(changes, key=lambda c: c['id']):
                    before, after = passages[change['before_passage_id']], passages[change['after_passage_id']]
                    pieces.append(f'<p class="summary">{esc(change["summary"])} {named_citation(before["id"])} {named_citation(after["id"])}</p>'
                                  f'<p class="quote">“{esc(before["exact"])}” {named_citation(before["id"])}</p>'
                                  f'<p class="quote">“{esc(after["exact"])}” {named_citation(after["id"])}</p>'
                                  f'<p class="metadata">{esc(change["order_basis"])}</p>')
                pieces.append('</details>')
        pieces.append('</article>')

    def add_matches(matches, candidates):
        if matches:
            actions = {a['finding_id']: a for a in data['action']}
            actors = {a['id']: a for a in data['actor']}
            pieces.append('<details class="record"><summary>Söylem ve uygulama eşleşmeleri</summary>'
                          '<p class="metadata">Toplu ve yerel kayıtlar örtüşebilir. Ön seçim ile kongredeki nihai seçim ayrı olaylardır.</p>')
            for m in matches:
                action = actions[m['action_finding_id']]
                actor = actors[action['actor_id']]
                statement = findings[m['statement_finding_id']]
                prefix = 'match-' if m['eligibility'] == 'eligible' else 'candidate-'
                refs = ' '.join(citation(e['passage_id']) for e in evidence[statement['id']] if e['role'] == 'statement')
                occurrence = citation(action['occurrence_passage_id'], 'Oluş kaynağı')
                authority = citation(actor['authorization_passage_id'], 'Yetki kaynağı') if actor['authorization_passage_id'] else ''
                sc, sv = format_finding(statement)
                ac, av = format_finding(findings[action['finding_id']])
                pieces.append(
                    f'<article class="match-card" id="{prefix}{esc(m["id"])}" data-match-id="{esc(m["id"])}">'
                    f'<details><summary>{esc(action["context"])} <span class="metadata">{time_tag(action["event_date"])}</span></summary>'
                    f'<p class="{sc}">{sv} {refs}</p><p class="{ac}">{av} {occurrence}</p>'
                    f'<p class="metadata">Aktör: {code_label(actor["kind"])} {authority} · {code_label(m["eligibility"])}</p>'
                    f'<p>{esc(m["relation"])} · {esc(m["rationale"])} {esc(m["exclusion_reason"])}</p></details></article>'
                )
            pieces.append('</details>')
        if candidates:
            pieces.append('<details class="record"><summary>Eşleşme adayları</summary>')
            for c in candidates:
                ref = f' <a href="#match-{esc(c["match_id"])}">Eşleşme</a>' if c['match_id'] else ''
                pieces.append(f'<p id="candidate-ledger-{esc(c["id"])}" data-status="{esc(c["status"])}">'
                              f'{topic_name(c["topic_id"])} · {code_label(c["status"])} · {esc(c["rationale"])}{ref}</p>')
            pieces.append('</details>')

    for i, pid in enumerate(party_ids):
        hidden = ' hidden' if i else ''
        panel = f'party-{esc(pid)}'
        party_findings = [f for f in findings.values() if f['party_id'] == pid]
        matches = [m for m in data.get('match', []) if findings[m['action_finding_id']]['party_id'] == pid]
        candidates = [c for c in data.get('match_candidate', []) if c['party_id'] == pid]
        finances = [f for f in data.get('financial', []) if f['party_id'] == pid]
        party_missing = {heading: rows for (party_id, heading), rows in missing_by_heading.items() if party_id == pid}
        reviewed = {s['heading'] for s in data.get('research_state', []) if s['party_id'] == pid and s['state'] == 'reviewed'}
        dossier_fields = [f for f in data.get('dossier_field', []) if f['party_id'] == pid]
        dossier_events = [e for e in data.get('dossier_event', []) if e['party_id'] == pid]
        event_dates = {e['id']: e for e in data.get('event_date', [])}
        pieces.append(f'<div role="tabpanel" id="{panel}" aria-labelledby="tab-{esc(pid)}"{hidden}>'
                      f'<h2 class="panel-title">{esc(parties[pid]["legal_name"])}</h2>')
        official=next((f for f in dossier_fields if f['field']=='official_site' and f['value']),None)
        if official:
            pieces.append(f'<p class="official-site">Resmî site: <a href="{web_url(official["value"])}">{esc(official["value"])}</a> '+ ' '.join(citation(e['passage_id']) for e in evidence[official['finding_id']])+'</p>')
        if True:
            anchors = ''.join(f'<a href="#{panel}-{key}">{heading}</a>' for key, heading in HEADINGS)
            sources_anchor = f'<a href="#{panel}-kaynaklar">Kaynaklar</a>'
            pieces.append(f'<nav class="section-links" aria-label="Dosya başlıkları">{anchors}{sources_anchor}</nav>'
                          '<div class="reading-grid">')
            for key, heading in HEADINGS:
                rows = [f for f in party_findings if f['heading'] == heading]
                previous_rows=[f for f in rows if f['id'] in legacy_findings]
                primary_rows=[f for f in rows if f['id'] not in legacy_findings]
                card_pairs={findings[f['finding_id']]['pair_id'] for f in dossier_fields if f['finding_id'] in findings}
                card_rows=[f for f in primary_rows if f['pair_id'] in card_pairs or f['epistemic_type']=='registry'] if key=='kurulus' else []
                primary_rows=[f for f in primary_rows if f not in card_rows]
                missing = party_missing.pop(heading, [])
                wide = ' card-wide' if key in ('kurulus', 'soylem-uygulama', 'finansman') else ''
                pieces.append(f'<section class="card{wide}" id="{panel}-{key}"><h3>{heading}</h3>')
                questions={'kurulus':'Neden kuruldu?','tuzuk':'Üyelik ve yönetim nasıl düzenleniyor?','program':'Ne vaat ediyor?','soylem-uygulama':'Kaynaklar ne yaptığını söylüyor?','finansman':'Para nereden geliyor, nasıl harcanıyor?'}
                if primary_rows:pieces.append(f'<p class="reader-question">{questions[key]}</p>')
                if primary_rows:add_findings(primary_rows)
                if key == 'tuzuk':
                    for row in data.get('comparison_row', []):
                        if row['party_id'] == pid: add_comparison_row(row, dossier=True)
                if key == 'kurulus':
                    pieces.append('<details class="record"><summary>Temel bilgiler ve kuruluş kronolojisi</summary>')
                    if card_rows:add_findings(card_rows)
                    pieces.append(render_identity_card(pid, dossier_fields, {m['id']: m for m in data['missing']}, evidence, citation))
                    pieces.append(render_foundation_timeline(pid, dossier_events, event_dates, findings, [n for n in data.get('dossier_identity_note', []) if n['party_id'] == pid], citation, format_finding))
                    for field in dossier_fields:
                        if field['field'] in ('headquarters', 'chairperson') and field['value'] is not None:
                            refs = ' '.join(citation(e['passage_id']) for e in evidence[field['finding_id']])
                            pieces.append(f'<p>{"Genel merkez" if field["field"] == "headquarters" else "Genel başkan"}: {esc(field["value"])} {refs}</p>')
                    pieces.append('</details>')
                if previous_rows:
                    pieces.append(f'<details class="record" id="prior-{esc(pid)}-{key}"><summary>Önceki kaynaklı kayıtlar</summary>')
                    add_findings(previous_rows)
                    pieces.append('</details>')
                if key == 'soylem-uygulama':
                    add_matches(matches, candidates)
                if key == 'finansman':
                    for f in finances:
                        amount = 'Bilinmiyor' if f['amount'] is None else esc(f['amount'])
                        ref = citation(f['passage_id']) if f['passage_id'] else ''
                        pieces.append(f'<p id="financial-{esc(f["id"])}"><strong>{esc(f["category"])}</strong> '
                                      f'{amount} {esc(f["currency"])} · {time_tag(f["period_start"])} – {time_tag(f["period_end"])}'
                                      f' · {esc(f["organization_scope"])} · Yayın {time_tag(f["published_at"])} {ref}</p>')
                has_content = rows or (key == 'soylem-uygulama' and (matches or candidates)) or (key == 'finansman' and finances)
                if missing:
                    if has_content:
                        current_topics=dict.fromkeys(m['topic_id'] for m in missing)
                        pieces.append('<p class="current-gap">Bilgi açıkları: '+ '; '.join(topic_name(t) for t in current_topics)+'. Ayrıntılar aşağıda.</p>')
                        pieces.append('<details class="record"><summary>Eksik bilgiler</summary>')
                        add_missing(missing, heading)
                        pieces.append('</details>')
                    else:
                        add_missing(missing, heading)
                elif not has_content:
                    status = 'İncelendi' if heading in reviewed else 'Henüz incelenmedi'
                    pieces.append(f'<p class="muted">{status}</p>')
                pieces.append('</section>')
            for heading, missing in party_missing.items():
                pieces.append(f'<section class="card card-wide"><h3>{esc(heading)}</h3>')
                add_missing(missing, heading)
                pieces.append('</section>')
            pieces.append('</div>')
        else:
            pieces.append('<div class="empty"><p>Parti dosyası henüz incelenmedi.</p></div>')
        pieces.append(f'<section class="card sources" id="{panel}-kaynaklar"><h3>Kaynaklar</h3>')
        emitted = set()
        for key, heading in HEADINGS:
            pieces.append(f'<section id="sources-{esc(pid)}-{key}"><h4>{heading}</h4>')
            for passage_id in sorted(grouped[pid, heading]):
                owner = documents[versions[passages[passage_id]['version_id']]['document_id']]['party_id']
                if passage_id in emitted or owner != pid:
                    pieces.append(citation(passage_id, 'Kaynak kaydı'))
                else:
                    pieces.append(source_entries[passage_id]); emitted.add(passage_id)
            pieces.append('</section>')
        pieces.append('</section>')
        pieces.append('</div>')

    pieces.append('<div role="tabpanel" id="comparison-summary" aria-labelledby="tab-comparison" hidden>'
                  '<h2 class="panel-title">Karşılaştırmalı Özet</h2>')
    if not data.get('comparison_topic'):
        pieces.append('<div class="empty"><p>Partiler arası karşılaştırma henüz hazırlanmadı.</p></div>')
    children = {}
    for topic in data.get('comparison_topic', []):
        children.setdefault((topic['taxonomy_version'], topic['parent_topic_id']), []).append(topic)
    ordered = []
    def append_topics(version, parent, depth):
        for topic in sorted(children.get((version, parent), []), key=lambda t: (t['order_index'], t['topic_id'])):
            ordered.append((topic, depth))
            append_topics(version, topic['topic_id'], depth + 1)
    for version in sorted({t['taxonomy_version'] for t in data.get('comparison_topic', [])}):
        append_topics(version, None, 0)
    synthesis_reviews = {r['subject_id']: r for r in data.get('comparison_semantic_review', [])
                         if r['subject_kind'] == 'comparison_synthesis' and r['reviewer_kind'] == 'agent'}
    for topic, depth in ordered:
        heading = 'h' + str(min(3 + depth, 6))
        pieces.append(f'<section class="comparison-topic"><{heading}>{esc(topic["definition"])}</{heading}>')
        for synth in data.get('comparison_synthesis', []):
            if (synth['topic_id'],synth['taxonomy_version']) == (topic['topic_id'],topic['taxonomy_version']):
                refs = ' '.join(named_citation(e['passage_id']) for e in data['comparison_synthesis_evidence'] if e['synthesis_id'] == synth['id'])
                pieces.append(f'<p class="summary">{esc(synth["text"])} {refs}</p>')
                review = synthesis_reviews.get(synth['id'])
                if review:
                    try:
                        decision = json.loads(review['reason'])
                    except (ValueError, TypeError):
                        decision = None
                    if isinstance(decision, dict) and decision.get('contract_version') == 2:
                        sides = ' · '.join(f'<a href="#comparison-{esc(side["row_id"])}">{esc(parties[side["party_id"]]["legal_name"])}</a>' for side in decision['sides'])
                        pieces.append(f'<p class="metadata">İddianın dayanakları: {sides}</p>')
        for pid in PRESENTATION_ORDER:
            for row in data['comparison_row']:
                if (row['topic_id'],row['taxonomy_version'],row['party_id']) == (topic['topic_id'],topic['taxonomy_version'],pid):
                    add_comparison_row(row)
        pieces.append('</section>')
    pieces.append('</div>')

    if scoped or methods or attempts:
        pieces.append('<details id="scope-method"><summary>Kapsam ve yöntem</summary>')
        pieces.append('<p>Birincil kaynaklara, özellikle parti yayınları, resmî kayıtlar ve özgün belgelere öncelik verilir. İkincil kaynaklar da kullanılır; haber, sosyal paylaşım, akademik çalışma ve bağımsız raporlar yayıncıya ve varsa yazarına atfedilir. Sosyal paylaşımda hesap, tarih ve kalıcı adres korunur. Sicil kimliği kendi kaynağıyla tutarlı tutulur; bilinmeyen belge tarihi ve hesap dönemi açıkça belirtilir.</p>')
        for m in methods:
            cited = next((p['id'] for p in passages.values() if p['version_id'] == m['cutoff_capture_version_id']), None)
            if not cited:
                raise ValueError('Kesim pasajı bulunamadı')
            pieces.append(f'<p>Veri kesimi <time datetime="{esc(m["cutoff_at"])}">{esc(m["cutoff_at"])}</time> {citation(cited)}</p>'
                          f'<p>{esc(m["period_rule"])}</p>')
        if scoped:
            pieces.append('<h3>TBMM kayıtları</h3><ul>')
            for o in data.get('scope_observation', []):
                pieces.append(f'<li>{esc(parties[o["party_id"]]["legal_name"])} {citation(o["source_passage_id"])}'
                              f' {esc(o["discrepancy_reason"])}</li>')
            pieces.append('</ul>')
        if data.get('scope_exclusion'):
            excluded = ', '.join(esc(e['name']) for e in data['scope_exclusion'])
            pieces.append(f'<p><strong>Kapsam dışında</strong> {excluded}</p>')
            if 'aa-2023-passage' in passages:
                pieces.append(f'<p>2023 seçim ittifakları ve ortak aday listeleri {citation("aa-2023-passage")}</p>')
        if data.get('topic_basis'):
            refs = ' · '.join(f'{topic_name(b["topic_id"])} {citation(b["passage_id"], "Dayanak")}'
                              for b in data['topic_basis'])
            pieces.append(f'<p><strong>Ortak konu sözlüğü</strong> {refs}</p>')
        if attempts:
            pieces.append('<details class="record"><summary>Araştırma kayıtları</summary><ul>')
            passages_by_version = {p['version_id']: p['id'] for p in reversed(list(passages.values()))}
            for a in attempts.values():
                linked = passages_by_version.get(a['source_version_id'])
                ref = citation(linked) if linked else ''
                pieces.append(f'<li class="attempt" id="attempt-{esc(a["id"])}"><strong>{topic_name(a["topic_id"])}</strong>'
                              f' · {time_tag(a["attempted_at"])} · {code_label(a["result"])}'
                              f'<p>{esc(a["query"])} · {esc(a["reason"])} {ref}</p></li>')
            pieces.append('</ul></details>')
        if resolutions:
            pieces.append('<details class="record"><summary>Çözümlenen geçmiş eksikler</summary><ul>')
            for m in data['missing']:
                if r := resolutions.get(m['id']):
                    pieces.append(f'<li>{topic_name(m["topic_id"])} · {esc(m["status"])} · {esc(m["reason"])}'
                                  f'<p>{time_tag(r["resolved_at"])} {esc(r["reason"])} {citation(r["passage_id"], "Yeni kanıt")}</p></li>')
            pieces.append('</ul></details>')
        pieces.append('</details>')
    # These URLs remain subject to the same validation even when the research ledger is not rendered.
    for lead in data.get('lead', []):
        web_url(lead['url'])

    pieces.append('''</main></div><script>
const tabs = [...document.querySelectorAll('[role=tab]')];
let previousCitation = null;

function selectTab(tab, focus = false) {
  for (const t of tabs) {
    const selected = t === tab;
    t.setAttribute('aria-selected', String(selected));
    t.tabIndex = selected ? 0 : -1;
    document.getElementById(t.getAttribute('aria-controls')).hidden = !selected;
  }
  if (focus) tab.focus();
}
for (const [i, tab] of tabs.entries()) {
  tab.addEventListener('click', () => {
    selectTab(tab);
    window.scrollTo(0, 0);
  });
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'Home') next = 0;
    else if (event.key === 'End') next = tabs.length - 1;
    else if (event.key === 'ArrowRight') next = (i + 1) % tabs.length;
    else if (event.key === 'ArrowLeft') next = (i + tabs.length - 1) % tabs.length;
    else return;
    event.preventDefault();
    selectTab(tabs[next], true);
  });
}
function reveal(element) {
  const panel = element.closest('[role=tabpanel]');
  if (panel) selectTab(document.getElementById(panel.getAttribute('aria-labelledby')));
  for (let node = element; node; node = node.parentElement) {
    if (node.tagName === 'DETAILS') node.open = true;
  }
  if (element.matches('article.match-card')) element.firstElementChild.open = true;
}
function restoreCitation() {
  if (!previousCitation) return;
  reveal(previousCitation);
  previousCitation.focus();
  previousCitation = null;
}
function hashTarget(hash) {
  if (!hash || hash.includes('%')) return null;
  try { return document.getElementById(hash.slice(1)); }
  catch { return null; }
}
function openHash() {
  if (location.hash.includes('%')) return;
  const target = hashTarget(location.hash);
  if (!target) { restoreCitation(); return; }
  if (target) {
    reveal(target);
    if (!target.id.startsWith('source-') && previousCitation) {
      if (target.contains(previousCitation)) { restoreCitation(); return; }
      previousCitation = null;
    }
    if (!target.hasAttribute('tabindex')) target.setAttribute('tabindex', '-1');
    target.focus({preventScroll:true});
    target.scrollIntoView();
  }
}
for (const link of document.querySelectorAll('a[href^="#"]')) {
  link.addEventListener('click', () => {
    const target = hashTarget(link.hash);
    if (!target) return;
    if (link.classList.contains('citation')) previousCitation = link;
    reveal(target);
  });
}
for (const source of document.querySelectorAll('details[id^=source-]')) {
  source.addEventListener('toggle', () => {
    if (!source.open && hashTarget(location.hash) === source) restoreCitation();
  });
}
window.addEventListener('hashchange', openHash);
openHash();
</script></body></html>''')
    return '\n'.join(pieces) + '\n'
