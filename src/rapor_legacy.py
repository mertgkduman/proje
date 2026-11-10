"""Kapalı kayıt snapshot'ından güvenli HTML üretir."""
from html import escape
from urllib.parse import urlsplit


def render_report(data):
    esc = lambda value: escape(str(value or ''), quote=True)
    versions = {v['id']: v for v in data['document_version']}
    documents = {d['id']: d for d in data['document']}
    passages = {p['id']: p for p in data['passage']}
    pieces = ['<!doctype html><html lang="tr"><meta charset="utf-8"><title>Kaynaklı pilot rapor</title>',
              '<style>.summary{color:#003366}.quote{color:#000}body{max-width:70em;margin:auto;font-family:sans-serif}</style>',
              '<h1>Yeni Parti: kuruluş bilgisi</h1>']
    if data.get('scope_party'):
        parties = {p['id']: p for p in data['party']}
        pieces.append('<p><a href="#kapsam-yontem">Kapsam ve yöntem</a></p><section id="kapsam-yontem"><h2>Kapsam ve yöntem</h2>')
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
                pieces.append('<li>' + esc(lead['topic_id']) + ': <a href="' + esc(lead['url']) + '">' + esc(lead['url']) + '</a> — ' + esc(lead['status']) + ' — ' + esc(lead['relevance_reason']) + '</li>')
            for edge in data.get('edge', []):
                if {'name': 'chain_links', 'value': '1'} in data.get('report_option', []):
                    source = next((p['id'] for p in data['passage'] if p['version_id'] == edge['from_version_id']), None)
                    target = next(l for l in data['lead'] if l['id'] == edge['to_lead_id'])
                    document = documents[versions[edge['from_version_id']]['document_id']]
                    ref = '<a class="citation" href="#source-' + esc(source) + '">' + esc(document['title']) + '</a>' if source else esc(document['title'])
                    pieces.append('<li>' + ref + ' (' + esc(document['source_kind']) + ') → <a href="' + esc(target['url']) + '">' + esc(target['url']) + '</a>: ' + esc(edge['relation']) + ' — ' + esc(edge['relevance_reason']) + '</li>')
                else:
                    pieces.append('<li>İlişki: ' + esc(edge['relation']) + ' — ' + esc(edge['relevance_reason']) + '</li>')
            for closure in data.get('closure', []):
                pieces.append('<li>Kapanma: ' + esc(closure['closed_at']) + ' — ' + esc(closure['reason']) + ' — ' + esc(closure['residual_leads']) + '</li>')
            for reopen in data.get('reopen', []):
                pieces.append('<li>Yeniden açılma: ' + esc(reopen['opened_at']) + ' — ' + esc(reopen['reason']) + '</li>')
            pieces.append('</ul>')
        pieces.append('</section>')
    if data.get('match'):
        findings = {f['id']: f for f in data['finding']}
        actions = {a['finding_id']: a for a in data['action']}
        actors = {a['id']: a for a in data['actor']}
        pieces.append('<section><h2>Söylem ve uygulama eşleşmeleri</h2>')
        for m in data['match']:
            action = actions[m['action_finding_id']]; actor = actors[action['actor_id']]
            statement_refs = ' '.join('<a class="citation" href="#source-' + esc(e['passage_id']) + '">[Kaynak]</a>' for e in data['finding_evidence'] if e['finding_id'] == m['statement_finding_id'] and e['role'] == 'statement')
            occurrence_ref = '<a class="citation" href="#source-' + esc(action['occurrence_passage_id']) + '">[Oluş kaynağı]</a>'
            authority_ref = (' <a class="citation" href="#source-' + esc(actor['authorization_passage_id']) + '">[Yetki kaynağı]</a>') if actor['authorization_passage_id'] else ''
            prefix = 'match-' if m['eligibility'] == 'eligible' else 'candidate-'
            pieces.append('<article id="' + prefix + esc(m['id']) + '"><h3>' + esc(m['topic_id']) + '</h3><p class="summary">' + esc(findings[m['statement_finding_id']]['text']) + ' ' + statement_refs + '</p><p class="summary">' + esc(findings[m['action_finding_id']]['text']) + ' ' + occurrence_ref + '</p><p>Aktör: ' + esc(actor['kind']) + authority_ref + ' — olay: ' + esc(action['event_date']) + ' — ' + esc(action['context']) + '</p><p>Yorum: ' + esc(m['relation']) + ' — ' + esc(m['rationale']) + ' — ' + esc(m['eligibility']) + ' ' + esc(m['exclusion_reason']) + '</p></article>')
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
    for f in data['finding']:
        evidence = [e for e in data['finding_evidence'] if e['finding_id'] == f['id']]
        if not evidence: raise ValueError('Kanıtsız bulgu')
        cls = 'quote' if f['provenance'] == 'quote' else 'summary'
        value = '“' + esc(f['text']) + '”' if cls == 'quote' else esc(f['text'])
        links = ' '.join('<a class="citation" href="#source-' + esc(e['passage_id']) + '">[Kaynak]</a>' for e in evidence)
        pieces.append('<p class="' + cls + '">' + value + ' ' + links + '</p>')
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
    pieces.append('<h2>Kaynaklar</h2>')
    for p in data['passage']:
        v = versions[p['version_id']]; d = documents[v['document_id']]
        manual = next((m for m in data.get('manual_passage', []) if m['passage_id'] == p['id']), None)
        if urlsplit(v['original_url']).scheme not in ('http', 'https'): raise ValueError('Geçersiz URL')
        pieces.append('<details id="source-' + esc(p['id']) + '"><summary>' + esc(d['title']) + '</summary>'
                      '<p>Pasaj: ' + esc(p['exact']) + ((' | PDF sayfası: ' + esc(p['pdf_page_index'] + 1) + ' | Basılı sayfa: ' + esc(p['printed_page'])) if p['pdf_page_index'] is not None else '') + ((' | Elle sayfa kontrolü: ' + esc(manual['checked_at']) + ' — ' + esc(manual['reason'])) if manual else '') + '</p><p>Belge tarihi: ' + esc(v['document_date'] or 'Belirtilmemiş') +
                      ' | Sürüm: ' + esc(v['version_label'] or 'Belirtilmemiş') + ' | Erişim: ' + esc(v['accessed_at']) +
                      ' | Doğrulama: ' + esc(v['verified_at']) + ((' | Tarih kesinliği: ' + esc(v.get('date_precision')) + ' | Gerekçe: ' + esc(v.get('date_unknown_reason'))) if data.get('schema_version') == 3 else '') + '</p><p><a href="' + esc(v['original_url']) + '">Özgün kaynak</a> '
                      '<a href="../../' + esc(v['readable_path']) + '">Yerel arşiv</a> '
                      '<a download href="../../' + esc(v['original_path']) + '">Ham belgeyi indir</a></p></details>')
    pieces.append('<script>document.querySelectorAll(".citation").forEach(a=>a.addEventListener("click",()=>{const d=document.getElementById(a.hash.slice(1));if(d)d.open=true}));</script></html>')
    return '\n'.join(pieces) + '\n'
