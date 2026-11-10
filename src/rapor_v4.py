"""Kapalı kayıt snapshot'ından güvenli HTML üretir."""
from html import escape
from urllib.parse import urlsplit


def render_report(data):
    esc = lambda value: escape(str(value or ''), quote=True)
    def web_url(value):
        parsed = urlsplit(value)
        if parsed.scheme not in ('http', 'https') or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Geçersiz URL')
        return esc(value)
    versions = {v['id']: v for v in data['document_version']}
    documents = {d['id']: d for d in data['document']}
    passages = {p['id']: p for p in data['passage']}
    pieces = ['<!doctype html><html lang="tr"><meta charset="utf-8"><title>Kaynaklı pilot rapor</title>',
              '<style>.summary{color:#003366}.quote{color:#000}body{max-width:70em;margin:auto;padding:1em;font-family:sans-serif;overflow-wrap:anywhere}[role=tablist]{display:flex;flex-wrap:wrap;gap:.3em}[role=tabpanel][hidden]{display:none}table{display:block;overflow-x:auto}a:focus,button:focus,summary:focus{outline:3px solid #005a9c}</style>',
              '<h1>Yeni Parti: kuruluş bilgisi</h1>']
    if data.get('scope_party'):
        parties = {p['id']: p for p in data['party']}
        pieces.append('<p><a href="#scope-method">Kapsam ve yöntem</a></p><details id="scope-method"><summary>Kapsam ve yöntem</summary>')
        pieces.append('<p>Bu dokuz partilik ön liste kullanıcının kapsam seçimidir; siyasi değerlendirme değildir.</p><ol>')
        for s in sorted(data['scope_party'], key=lambda s: s['approved_order']):
            obs = [o for o in data['scope_observation'] if o['party_id'] == s['party_id']]
            refs = ' '.join('<a class="citation" href="#source-' + esc(o['source_passage_id']) + '">[Kaynak]</a>' for o in obs)
            notes = ' '.join(esc(o['discrepancy_reason']) for o in obs if o['discrepancy_reason'])
            pieces.append('<li>' + esc(parties[s['party_id']]['legal_name']) + ' ' + refs + ' ' + notes + '</li>')
        pieces.append('</ol><h3>Başlangıç kapsamı dışında tutulanlar</h3><ul>')
        for e in data['scope_exclusion']:
            pieces.append('<li>' + esc(e['name']) + ': ' + esc(e['reason']) + ' (' + esc(e['decision_origin']) + ')</li>')
        pieces.append('</ul><p>Parti tüzel kimliği, milletvekili parti üyeliği ve Meclis grubu ayrı ilişkilerdir. Grup adından bireysel parti üyeliği çıkarılmaz.</p>')
        for i in data.get('identity_observation', []):
            pieces.append('<p>' + esc(parties[i['entity_id']]['legal_name']) + ' — sicil anahtarı: ' + esc(i['registry_key']) + ' <a class="citation" href="#source-' + esc(i['passage_id']) + '">[Kaynak]</a></p>')
        for g in data.get('parliamentary_group', []):
            pieces.append('<p>Meclis grubu: ' + esc(g['name']) + ' <a class="citation" href="#source-' + esc(g['passage_id']) + '">[Kaynak]</a></p>')
        persons = {p['id']: p for p in data.get('person', [])}
        for m in data.get('membership', []):
            pieces.append('<p>' + esc(persons[m['person_id']]['name']) + ': ' + esc(parties[m['party_id']]['legal_name']) + ' (' + esc(m['valid_from']) + ' tarihli kayıt) <a class="citation" href="#source-' + esc(m['passage_id']) + '">[Kaynak]</a></p>')
        for m in data.get('group_membership', []):
            pieces.append('<p>' + esc(persons[m['person_id']]['name']) + ': grup kaydı <a class="citation" href="#source-' + esc(m['passage_id']) + '">[Kaynak]</a></p>')
        if 'aa-2023-passage' in passages:
            pieces.append('<p>TBMM sayfasının kendi güncelleme tarihi bilinmiyor. 2023 seçimindeki resmî ittifak ortaklığı ile ortak listeden aday gösterilmesi ayrı ilişkilerdir. Bu tarihsel kaynak güncel üyeliği göstermez. <a class="citation" href="#source-aa-2023-passage">[Kaynak]</a></p>')
        for m in data.get('method', []):
            cited = next((p['id'] for p in data['passage'] if p['version_id'] == m['cutoff_capture_version_id']), None)
            if not cited: raise ValueError('Kesim pasajı bulunamadı')
            pieces.append('<p>Kesim: ' + esc(m['cutoff_at']) + ' — ' + esc(m['cutoff_reason']) + ' <a class="citation" href="#source-' + esc(cited) + '">[Kaynak]</a></p><p>' + esc(m['period_rule']) + ' ' + esc(m['pilot_reason']) + '</p><p>Belge tarihi, olay tarihi, hesap dönemi, erişim ve doğrulama anı ayrı kayıtlardır. Kesim günü yalnız gün biliniyorsa olayın kapsamı belirsizdir. Daha sonra edinilen belge, kesim içindeki geçmiş bir olayı destekleyebilir.</p>')
        if data.get('topic'):
            pieces.append('<h3>Ortak konu sözlüğü</h3><p>Bu başlıklar beş parti dosyası başlığından ayrıdır. TİP kaynağı yalnız sözlük dayanağıdır; TİP dosyası henüz incelenmedi. Erişilen belgenin kesim günündeki sürümü ayrıca doğrulanmamıştır.</p><ul>')
            for topic in data['topic']:
                bases = [b for b in data.get('topic_basis', []) if b['topic_id'] == topic['id'] and b['taxonomy_version'] == topic['taxonomy_version']]
                refs = ' '.join('<a class="citation" href="#source-' + esc(b['passage_id']) + '">[Dayanak]</a> ' + esc(b['rationale']) for b in bases)
                pieces.append('<li>' + esc(topic['label']) + ' — sürüm ' + esc(topic['taxonomy_version']) + ': ' + ('dayanak doğrulandı' if topic['status'] == 'verified' else 'aday, dayanak doğrulanmadı') + ' ' + refs + '</li>')
                for q in data.get('topic_query', []):
                    if q['topic_id'] == topic['id'] and q['taxonomy_version'] == topic['taxonomy_version']:
                        label = {'institutional':'kurumsal', 'authorized':'yetkili temsilci', 'individual':'bireysel'}[q['actor_kind']]
                        pieces.append('<li>Planlanan başlangıç sorgusu (' + label + '): ' + esc(q['query']) + '</li>')
            pieces.append('</ul><p>Tarama kaynakları: resmî kayıtlar ve kararlar, yetkili parti açıklamaları ve güvenilir bağımsız kaynaklar. Yeterli kanıtlı bütün uygun eşleşmeler alınır; sayısal kota veya sonucun yönüyle eleme yapılmaz. Kurumsal eylem, yetkili temsilci ve bireysel kayıt ayrı değerlendirilir. İlgili bağlantılar ve çelişkiler izlenir; bekleyen uç kalmayınca gerekçeyle kapanır, yeni kanıtla yeniden açılır. Erişim engelleri görünür kalır.</p>')
        if data.get('lead') or data.get('attempt'):
            pieces.append('<h3>Tarama zinciri</h3><ul>')
            for a in data.get('attempt', []):
                linked = next((p['id'] for p in data['passage'] if p['version_id'] == a['source_version_id']), None)
                ref = ' <a class="citation" href="#source-' + esc(linked) + '">[Kaynak]</a>' if linked else ''
                pieces.append('<li id="attempt-' + esc(a['id']) + '">' + esc(a['topic_id']) + ' — ' + esc(a['query']) + ' — ' + esc(a['attempted_at']) + ': ' + esc(a['result']) + ' — ' + esc(a['reason']) + ref + '</li>')
            for lead in data.get('lead', []):
                pieces.append('<li>' + esc(lead['topic_id']) + ': <a href="' + web_url(lead['url']) + '">' + esc(lead['url']) + '</a> — ' + esc(lead['status']) + ' — ' + esc(lead['relevance_reason']) + '</li>')
            for edge in data.get('edge', []):
                if {'name': 'chain_links', 'value': '1'} in data.get('report_option', []):
                    source = next((p['id'] for p in data['passage'] if p['version_id'] == edge['from_version_id']), None)
                    target = next(l for l in data['lead'] if l['id'] == edge['to_lead_id'])
                    document = documents[versions[edge['from_version_id']]['document_id']]
                    ref = '<a class="citation" href="#source-' + esc(source) + '">' + esc(document['title']) + '</a>' if source else esc(document['title'])
                    pieces.append('<li>' + ref + ' (' + esc(document['source_kind']) + ') → <a href="' + web_url(target['url']) + '">' + esc(target['url']) + '</a>: ' + esc(edge['relation']) + ' — ' + esc(edge['relevance_reason']) + '</li>')
                else:
                    pieces.append('<li>İlişki: ' + esc(edge['relation']) + ' — ' + esc(edge['relevance_reason']) + '</li>')
            for closure in data.get('closure', []):
                pieces.append('<li>Kapanma: ' + esc(closure['closed_at']) + ' — ' + esc(closure['reason']) + ' — ' + esc(closure['residual_leads']) + '</li>')
            for reopen in data.get('reopen', []):
                pieces.append('<li>Yeniden açılma: ' + esc(reopen['opened_at']) + ' — ' + esc(reopen['reason']) + '</li>')
            pieces.append('</ul>')
        pieces.append('</details>')
    headings = ('Kuruluş', 'Tüzük', 'Program', 'Söylem ve uygulama', 'Finansman ve harcamalar')
    scoped = sorted(data.get('scope_party', []), key=lambda s: s['approved_order'])
    parties = {p['id']: p for p in data['party']}
    pieces.append('<div role="tablist" aria-label="Partiler ve karşılaştırmalı özet">')
    for i, scope in enumerate(scoped):
        pid = scope['party_id']
        pieces.append('<button type="button" role="tab" id="tab-' + esc(pid) + '" aria-controls="party-' + esc(pid) + '" aria-selected="' + ('true' if i == 0 else 'false') + '" tabindex="' + ('0' if i == 0 else '-1') + '">' + esc(parties[pid]['legal_name']) + '</button>')
    pieces.append('<button type="button" role="tab" id="tab-comparison" aria-controls="comparison-summary" aria-selected="false" tabindex="-1">Karşılaştırmalı Özet</button></div>')
    pieces.append('<div role="tabpanel" id="party-yeni-parti" aria-labelledby="tab-yeni-parti">')
    for heading in headings:
        pieces.append('<section><h2>' + esc(heading) + '</h2>')
        for f in (f for f in data['finding'] if f['party_id'] == 'yeni-parti' and f['heading'] == heading):
            evidence = [e for e in data['finding_evidence'] if e['finding_id'] == f['id']]
            if not evidence: raise ValueError('Kanıtsız bulgu')
            cls = 'quote' if f['provenance'] == 'quote' else 'summary'
            value = '“' + esc(f['text']) + '”' if cls == 'quote' else esc(f['text'])
            links = ' '.join('<a class="citation" href="#source-' + esc(e['passage_id']) + '">[Kaynak]</a>' for e in evidence)
            labels = {'registry':'Sicil kaydı', 'fact':'Olgu', 'claim':'Beyan', 'comment':'Yorum'}
            pieces.append('<p class="' + cls + '" data-finding-id="' + esc(f['id']) + '" data-provenance="' + esc(f['provenance']) + '" data-epistemic-type="' + esc(f['epistemic_type']) + '">' + esc(labels.get(f['epistemic_type'], f['epistemic_type'])) + ': ' + value + ' ' + links + '</p>')
            if cls == 'summary':
                for e in evidence:
                    pieces.append('<p class="quote">“' + esc(passages[e['passage_id']]['exact']) + '” <a class="citation" href="#source-' + esc(e['passage_id']) + '">[Kaynak]</a></p>')
        resolved_ids = {r['missing_id'] for r in data.get('missing_resolution', [])}
        for m in (m for m in data.get('missing', []) if m['party_id'] == 'yeni-parti' and m['heading'] == heading and m['id'] not in resolved_ids):
            pieces.append('<p>' + esc(m['status']) + ': ' + esc(m['reason']) + ' <a href="#attempt-' + esc(m['attempt_id']) + '">Girişim</a></p>')
        pieces.append('</section>')
    if data.get('match'):
        findings = {f['id']: f for f in data['finding']}
        actions = {a['finding_id']: a for a in data['action']}
        actors = {a['id']: a for a in data['actor']}
        pieces.append('<section><h2>Söylem ve uygulama eşleşmeleri</h2><p>Toplu ve yerel kayıtlar örtüşebilir; eşleşme sayısı bağımsız olay toplamı değildir. Ön seçim ile kongredeki nihai seçim ayrı olaylardır.</p>')
        for m in data['match']:
            action = actions[m['action_finding_id']]; actor = actors[action['actor_id']]
            statement_refs = ' '.join('<a class="citation" href="#source-' + esc(e['passage_id']) + '">[Kaynak]</a>' for e in data['finding_evidence'] if e['finding_id'] == m['statement_finding_id'] and e['role'] == 'statement')
            occurrence_ref = '<a class="citation" href="#source-' + esc(action['occurrence_passage_id']) + '">[Oluş kaynağı]</a>'
            authority_ref = (' <a class="citation" href="#source-' + esc(actor['authorization_passage_id']) + '">[Yetki kaynağı]</a>') if actor['authorization_passage_id'] else ''
            prefix = 'match-' if m['eligibility'] == 'eligible' else 'candidate-'
            pieces.append('<article id="' + prefix + esc(m['id']) + '" data-match-id="' + esc(m['id']) + '"><h3>' + esc(m['topic_id']) + '</h3><p class="summary">' + esc(findings[m['statement_finding_id']]['text']) + ' ' + statement_refs + '</p><p class="summary">' + esc(findings[m['action_finding_id']]['text']) + ' ' + occurrence_ref + '</p><p>Aktör: ' + esc(actor['kind']) + authority_ref + ' — olay: ' + esc(action['event_date']) + ' — ' + esc(action['context']) + '</p><p>Yorum: ' + esc(m['relation']) + ' — ' + esc(m['rationale']) + ' — ' + esc(m['eligibility']) + ' ' + esc(m['exclusion_reason']) + '</p></article>')
        pieces.append('</section>')
    if 'match_candidate' in data:
        pieces.append('<section><h2>Eşleşme adayları</h2>')
        for c in data['match_candidate']:
            ref = (' <a href="#match-' + esc(c['match_id']) + '">Eşleşme</a>') if c['match_id'] else ''
            pieces.append('<p id="candidate-ledger-' + esc(c['id']) + '" data-status="' + esc(c['status']) + '">' + esc(c['id']) + ': ' + esc(c['status']) + ' — ' + esc(c['rationale']) + ref + '</p>')
        pieces.append('</section>')
    if data.get('financial'):
        pieces.append('<section><h2>Finansman ve harcamalar</h2>')
        for f in data['financial']:
            amount = 'Bilinmiyor' if f['amount'] is None else esc(f['amount'])
            ref = (' <a class="citation" href="#source-' + esc(f['passage_id']) + '">[Kaynak]</a>') if f['passage_id'] else ''
            pieces.append('<p id="financial-' + esc(f['id']) + '">' + esc(f['category']) + ': ' + amount + ' ' + esc(f['currency']) + ' — ' + esc(f['period_start']) + ' / ' + esc(f['period_end']) + ' — ' + esc(f['organization_scope']) + ' — yayın: ' + esc(f['published_at']) + ref + '</p>')
        pieces.append('</section>')
    resolved = {r['missing_id']: r for r in data.get('missing_resolution', [])}
    unresolved = [m for m in data.get('missing', []) if m['id'] not in resolved]
    if unresolved:
        attempts = {a['id']: a for a in data['attempt']}
        for heading in dict.fromkeys(m['heading'] for m in unresolved):
            pieces.append('<section><h2>' + esc(heading) + '</h2>')
            for m in (m for m in unresolved if m['heading'] == heading):
                a = attempts[m['attempt_id']]
                pieces.append('<p>' + esc(m['topic_id']) + ': ' + esc(m['status']) + ' — ' + esc(m['reason']) + ' (' + esc(a['attempted_at']) + ') <a href="#attempt-' + esc(a['id']) + '">Girişim</a></p>')
            pieces.append('</section>')
    for state in data.get('research_state', []):
        if state['state'] == 'not_researched':
            pieces.append('<section><h2>' + esc(state['heading']) + '</h2><p>Henüz incelenmedi</p></section>')
    if unresolved:
        attempts = {a['id']: a for a in data['attempt']}
        pieces.append('<h2>Eksik bilgiler</h2><ul>')
        for m in unresolved:
            a = attempts[m['attempt_id']]
            pieces.append('<li>' + esc(m['party_id']) + ' / ' + esc(m['heading']) + ' / ' + esc(m['topic_id']) + ': ' + esc(m['status']) + ' — ' + esc(m['reason']) + ' (' + esc(a['attempted_at']) + ') <a href="#attempt-' + esc(a['id']) + '">Girişim</a></li>')
        pieces.append('</ul>')
    if resolved:
        pieces.append('<h2>Çözümlenen geçmiş eksikler</h2><ul>')
        for m in data['missing']:
            if m['id'] in resolved:
                r = resolved[m['id']]
                pieces.append('<li>' + esc(m['id']) + ': ' + esc(m['status']) + ' — ' + esc(m['reason']) + '; çözüm ' + esc(r['resolved_at']) + ': ' + esc(r['reason']) + ' <a class="citation" href="#source-' + esc(r['passage_id']) + '">[Yeni kanıt]</a></li>')
        pieces.append('</ul>')
    source_groups = {}
    for p in data['passage']:
        v = versions[p['version_id']]; d = documents[v['document_id']]
        manual = next((m for m in data.get('manual_passage', []) if m['passage_id'] == p['id']), None)
        web_url(v['original_url'])
        for path in (v['readable_path'], v['original_path']):
            if path.startswith('/') or '..' in path.split('/') or not path.startswith('objects/'):
                raise ValueError('Geçersiz arşiv yolu')
        kind = {'registry':'sicil', 'official':'resmî kayıt', 'journalism':'haber', 'unknown':'türü doğrulanmadı', 'party':'parti kaynağı'}.get(d['source_kind'], d['source_kind'])
        source_groups.setdefault(d['party_id'], []).append('<details id="source-' + esc(p['id']) + '"><summary>' + esc(d['title']) + ' — ' + esc(kind) + '</summary>'
                      '<p>Pasaj: ' + esc(p['exact']) + ((' | Konum: ' + esc(p['article'] or p['section'] or p['prefix'] or p['suffix'])) if (p['article'] or p['section'] or p['prefix'] or p['suffix']) else '') + ((' | PDF sayfası: ' + esc(p['pdf_page_index'] + 1) + ' | Basılı sayfa: ' + esc(p['printed_page'])) if p['pdf_page_index'] is not None else '') + ((' | Elle sayfa kontrolü: ' + esc(manual['checked_at']) + ' — ' + esc(manual['reason'])) if manual else '') + '</p><p>Belge tarihi: ' + esc(v['document_date'] or 'Belirtilmemiş') +
                      ' | Sürüm: ' + esc(v['version_label'] or 'Belirtilmemiş') + ' | Erişim: ' + esc(v['accessed_at']) +
                      ' | Doğrulama: ' + esc(v['verified_at']) + ((' | Tarih kesinliği: ' + esc(v.get('date_precision')) + ' | Gerekçe: ' + esc(v.get('date_unknown_reason'))) if data.get('schema_version') == 3 else '') + '</p><p><a href="' + esc(v['original_url']) + '">Özgün kaynak</a> '
                      '<a href="../../' + esc(v['readable_path']) + '">Yerel arşiv</a> '
                      '<a download href="../../' + esc(v['original_path']) + '">Ham belgeyi indir</a></p></details>')
    pieces.append('<h2>Kaynaklar</h2>' + ''.join(source_groups.get('yeni-parti', [])))
    pieces.append('</div>')
    for scope in scoped:
        pid = scope['party_id']
        if pid == 'yeni-parti': continue
        pieces.append('<div role="tabpanel" id="party-' + esc(pid) + '" aria-labelledby="tab-' + esc(pid) + '" hidden>')
        for heading in headings:
            pieces.append('<section><h2>' + esc(heading) + '</h2><p>Henüz incelenmedi</p></section>')
        pieces.append('<h2>Kaynaklar</h2>' + ''.join(source_groups.get(pid, [])))
        pieces.append('</div>')
    pieces.append('<div role="tabpanel" id="comparison-summary" aria-labelledby="tab-comparison" hidden>')
    for heading in headings:
        pieces.append('<section><h2>' + esc(heading) + '</h2><p>Yeni Parti pilotu: kaynaklar ve araştırma sınırları parti sekmesinde. Partiler arası karşılaştırma henüz hazırlanmadı.</p></section>')
    pieces.append('</div>')
    pieces.append('''<script>
const tabs=[...document.querySelectorAll('[role=tab]')]; let previousCitation=null;
function selectTab(tab,focus=false){tabs.forEach(t=>{const on=t===tab;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!on});if(focus)tab.focus()}
tabs.forEach((tab,i)=>{tab.addEventListener('click',()=>selectTab(tab));tab.addEventListener('keydown',e=>{let n;if(e.key==='Home')n=0;else if(e.key==='End')n=tabs.length-1;else if(e.key==='ArrowRight'||e.key==='ArrowDown')n=(i+1)%tabs.length;else if(e.key==='ArrowLeft'||e.key==='ArrowUp')n=(i+tabs.length-1)%tabs.length;else return;e.preventDefault();selectTab(tabs[n],true)})});
function restoreCitation(){if(!previousCitation)return;const p=previousCitation.closest('[role=tabpanel]');if(p)selectTab(document.getElementById(p.getAttribute('aria-labelledby')));const scope=previousCitation.closest('details');if(scope)scope.open=true;previousCitation.focus();previousCitation=null}
function openHash(){const id=decodeURIComponent(location.hash.slice(1));if(!id.startsWith('source-')){restoreCitation();return}const d=document.getElementById(id);if(!d)return;const panel=d.closest('[role=tabpanel]');if(panel)selectTab(document.getElementById(panel.getAttribute('aria-labelledby')));d.open=true;d.scrollIntoView()}
document.querySelectorAll('.citation').forEach(a=>a.addEventListener('click',()=>{previousCitation=a;const d=document.getElementById(a.hash.slice(1));if(d){const p=d.closest('[role=tabpanel]');if(p)selectTab(document.getElementById(p.getAttribute('aria-labelledby')));d.open=true}}));
document.querySelectorAll('details[id^=source-]').forEach(d=>d.addEventListener('toggle',()=>{if(!d.open)restoreCitation()}));window.addEventListener('hashchange',openHash);openHash();
</script></html>''')
    return '\n'.join(pieces) + '\n'
