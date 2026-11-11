"""Kapalı kayıt snapshot'ından güvenli, sekmeli HTML üretir."""
from collections import defaultdict
from html import escape
from pathlib import Path
from urllib.parse import urlsplit


RENDERER_VERSION = 8
STYLE = Path(__file__).with_name('rapor_v8.css').read_text(encoding='utf-8')
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
    'registry': 'sicil', 'official': 'resmî kayıt', 'journalism': 'haber', 'news': 'haber',
    'unknown': 'türü doğrulanmadı', 'party': 'parti kaynağı',
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


def finding_text(finding):
    value = esc(finding['text'])
    if finding['provenance'] == 'quote':
        return 'quote', f'“{value}”'
    return 'summary', value


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
    attempts = {a['id']: a for a in data.get('attempt', [])}
    resolutions = {r['missing_id']: r for r in data.get('missing_resolution', [])}
    missing_by_heading = defaultdict(list)
    for row in data.get('missing', []):
        if row['id'] not in resolutions:
            missing_by_heading[row['party_id'], row['heading']].append(row)

    def topic_name(value):
        return esc(topics.get(value, str(value).replace('-', ' ').capitalize()))

    def citation(pid, label='Kaynak'):
        title = documents[versions[passages[pid]['version_id']]['document_id']]['title']
        return f'<a class="citation" href="#source-{esc(pid)}" aria-label="{esc(label)}: {esc(title)}">[{esc(label)}]</a>'

    source_groups = defaultdict(list)
    manual_passages = {m['passage_id']: m for m in data.get('manual_passage', [])}
    for p in passages.values():
        v = versions[p['version_id']]
        d = documents[v['document_id']]
        original = web_url(v['original_url'])
        for path in (v['readable_path'], v['original_path']):
            if path.startswith('/') or '..' in path.split('/') or not path.startswith('objects/'):
                raise ValueError('Geçersiz arşiv yolu')
        source_type = 'yetkisi doğrulanmadı' if d['source_kind'] == 'unverified' else code_label(d['source_kind'])
        location = p['article'] or p['section'] or p['prefix'] or p['suffix']
        metadata = [('Belge tarihi', time_tag(v['document_date'])),
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
        details = ''.join(f'<dt>{label}</dt><dd>{value}</dd>' for label, value in metadata)
        source_groups[d['party_id']].append(
            f'<details class="source" id="source-{esc(p["id"])}">'
            f'<summary>{esc(d["title"])} <span class="source-type">{source_type}</span></summary>'
            f'<blockquote class="quote">“{esc(p["exact"])}”</blockquote><dl class="source-info">{details}</dl>'
            f'<div class="source-links"><a href="{original}">Özgün kaynak</a>'
            f'<a href="../../{esc(v["readable_path"])}">Arşiv kopyası</a>'
            f'<a download href="../../{esc(v["original_path"])}">Belgeyi indir</a></div></details>'
        )

    known_order = {pid: i for i, pid in enumerate(PRESENTATION_ORDER)}
    scoped = sorted(data.get('scope_party', []),
                    key=lambda row: (known_order.get(row['party_id'], len(known_order)), row['approved_order']))
    party_ids = [row['party_id'] for row in scoped] or [pid for pid in parties if pid == 'yeni-parti']
    methods = data.get('method', [])
    title = 'Türkiye siyasi partileri: kaynaklı pilot rapor'
    pieces = [
        '<!doctype html><html lang="tr"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f'<title>{title}</title><style>{STYLE}</style></head><body>',
        '<a class="skip" href="#main-content">İçeriğe geç</a><div class="shell"><aside class="sidebar">',
        '<p class="sidebar-title">Parti dosyaları</p><div role="tablist" aria-label="Partiler ve karşılaştırmalı özet">',
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
            cls, value = finding_text(f)
            passage_ids = tuple(dict.fromkeys(e['passage_id'] for e in evidence[f['id']]))
            kind = f['epistemic_type']
            shared_source = cls == 'quote' and previous == (kind, passage_ids)
            label = '' if shared_source else f'<strong>{esc(labels.get(kind, kind))}</strong> '
            links = '' if shared_source else ' '.join(citation(pid) for pid in passage_ids)
            pieces.append(f'<p id="finding-{esc(f["id"])}" class="{cls}" data-finding-id="{esc(f["id"])}" '
                          f'data-provenance="{esc(f["provenance"])}" data-epistemic-type="{esc(f["epistemic_type"])}">'
                          f'{label}{value} {links}</p>')
            previous = (kind, passage_ids)
        pieces.append('</div>')

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
                sc, sv = finding_text(statement)
                ac, av = finding_text(findings[action['finding_id']])
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
        pieces.append(f'<div role="tabpanel" id="{panel}" aria-labelledby="tab-{esc(pid)}"{hidden}>'
                      f'<h2 class="panel-title">{esc(parties[pid]["legal_name"])}</h2>')
        if party_findings or matches or finances or party_missing or reviewed:
            anchors = ''.join(f'<a href="#{panel}-{key}">{heading}</a>' for key, heading in HEADINGS)
            sources_anchor = f'<a href="#{panel}-kaynaklar">Kaynaklar</a>' if source_groups[pid] else ''
            pieces.append(f'<nav class="section-links" aria-label="Dosya başlıkları">{anchors}{sources_anchor}</nav>'
                          '<div class="reading-grid">')
            for key, heading in HEADINGS:
                rows = [f for f in party_findings if f['heading'] == heading]
                missing = party_missing.pop(heading, [])
                wide = ' card-wide' if key in ('kurulus', 'soylem-uygulama', 'finansman') else ''
                pieces.append(f'<section class="card{wide}" id="{panel}-{key}"><h3>{heading}</h3>')
                if rows and key == 'soylem-uygulama':
                    pieces.append('<details class="record"><summary>Belgelenmiş söylem ve olaylar</summary>')
                    add_findings(rows)
                    pieces.append('</details>')
                elif rows:
                    add_findings(rows)
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
        if source_groups[pid]:
            pieces.append(f'<section class="card sources" id="{panel}-kaynaklar"><h3>Kaynaklar</h3>'
                          + ''.join(source_groups[pid]) + '</section>')
        pieces.append('</div>')

    pieces.append('<div role="tabpanel" id="comparison-summary" aria-labelledby="tab-comparison" hidden>'
                  '<h2 class="panel-title">Karşılaştırmalı Özet</h2>'
                  '<div class="empty"><p>Partiler arası karşılaştırma henüz hazırlanmadı.</p></div></div>')

    if scoped or methods or attempts:
        pieces.append('<details id="scope-method"><summary>Kapsam ve yöntem</summary>')
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
    else if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (i + 1) % tabs.length;
    else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (i + tabs.length - 1) % tabs.length;
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
  try { return document.getElementById(decodeURIComponent(hash.slice(1))); }
  catch { return null; }
}
function openHash() {
  const target = hashTarget(location.hash);
  if (target) {
    reveal(target);
    target.scrollIntoView();
  }
  if (!target?.id.startsWith('source-')) restoreCitation();
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
