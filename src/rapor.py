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
    for f in data['finding']:
        evidence = [e for e in data['finding_evidence'] if e['finding_id'] == f['id']]
        if not evidence: raise ValueError('Kanıtsız bulgu')
        cls = 'quote' if f['provenance'] == 'quote' else 'summary'
        value = '“' + esc(f['text']) + '”' if cls == 'quote' else esc(f['text'])
        links = ' '.join('<a class="citation" href="#source-' + esc(e['passage_id']) + '">[Kaynak]</a>' for e in evidence)
        pieces.append('<p class="' + cls + '">' + value + ' ' + links + '</p>')
    pieces.append('<h2>Kaynaklar</h2>')
    for p in data['passage']:
        v = versions[p['version_id']]; d = documents[v['document_id']]
        if urlsplit(v['original_url']).scheme not in ('http', 'https'): raise ValueError('Geçersiz URL')
        pieces.append('<details id="source-' + esc(p['id']) + '"><summary>' + esc(d['title']) + '</summary>'
                      '<p>Pasaj: ' + esc(p['exact']) + '</p><p>Belge tarihi: ' + esc(v['document_date'] or 'Belirtilmemiş') +
                      ' | Sürüm: ' + esc(v['version_label'] or 'Belirtilmemiş') + ' | Erişim: ' + esc(v['accessed_at']) +
                      ' | Doğrulama: ' + esc(v['verified_at']) + '</p><p><a href="' + esc(v['original_url']) + '">Özgün kaynak</a> '
                      '<a href="../../' + esc(v['readable_path']) + '">Yerel arşiv</a> '
                      '<a download href="../../' + esc(v['original_path']) + '">Ham belgeyi indir</a></p></details>')
    pieces.append('<script>document.querySelectorAll(".citation").forEach(a=>a.addEventListener("click",()=>{const d=document.getElementById(a.hash.slice(1));if(d)d.open=true}));</script></html>')
    return '\n'.join(pieces) + '\n'
