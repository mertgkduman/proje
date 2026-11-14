import hashlib
import json
from pathlib import Path

root=Path('.planning/phases/03-t-z-k-ve-programlar-n-kar-la-t-r-lmas')
checks=root/'03-13-checks'
program1=Path('data/comparisons/03-demokrat-program-1.json')
semantic=Path('data/comparisons/03-demokrat-program-semantic.json')
snapshot=checks/'program1-semantic-snapshot.json'
if snapshot.exists(): raise RuntimeError('İlk semantik anlık görüntüsü zaten var; ikinci görevi yeniden yazmadan önce durumu uzlaştırın.')
snapshot.write_bytes(semantic.read_bytes())
(checks/'program1-semantic-snapshot.sha256').write_text(hashlib.sha256(snapshot.read_bytes()).hexdigest()+'  '+str(snapshot)+'\n')
first=json.loads(snapshot.read_text())
second=json.loads((root/'03-13-semantic-2-draft.json').read_text())
decisions=first['decisions']+second
by_id={(x['subject_kind'],x['subject_id']):x for x in decisions}
contexts=json.loads((root/'03-13-absence-context-draft.json').read_text())
for topic,pids in contexts.items():
    d=by_id['comparison_review_scope','0313-demokrat-scope-'+topic]
    for pid in pids:
        if pid not in d['passage_ids']: d['passage_ids'].append(pid)
    if 'Bağlam pasajı dar soruya olumlu yanıt değildir.' not in d['reason']:
        d['reason']+=' Bağlam pasajı dar soruya olumlu yanıt değildir.'
visuals=json.loads((root/'03-13-visual-evidence-draft.json').read_text())
for item in visuals:
    field=item['summary_finding_id'][:-2]+'-f'
    d=by_id['comparison_field',field]
    if item['passage_id'] not in d['passage_ids']: d['passage_ids'].append(item['passage_id'])
    d['reason']+=' Metin katmanı olmayan kapak veya önsöz sayfasındaki aynı ifade görsel olarak ayrıca incelendi.'
payload=dict(status='in_progress',note='Kaynak kapsamı, koşul ve öneri niteliği ajan incelemesidir; bağımsız insan kabulü değildir.',decisions=decisions,
             historical_pairs=json.loads((root/'03-13-history-pairs-draft.json').read_text()))
Path('data/comparisons/03-demokrat-program-2.json').write_bytes((root/'03-13-program-2-draft.json').read_bytes())
semantic.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print('MATERIALIZED',len(decisions),'decisions',len(visuals),'visual additions',len(contexts),'absence contexts')
