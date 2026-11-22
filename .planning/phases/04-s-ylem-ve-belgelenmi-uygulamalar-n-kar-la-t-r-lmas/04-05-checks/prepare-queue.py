import json
from pathlib import Path

inventory = json.loads(Path('data/practices/04-inventory.json').read_text())
cells = [c for c in inventory['cells'] if c['party_id'] == 'tip']
collections = [c for c in inventory['source_collections'] if c['party_id'] == 'tip']
tranches = []
for index, cell in enumerate(cells, 1):
    relevant = [c for c in collections if cell['topic_id'] in json.loads(c['topic_ids'])]
    tranches.append(dict(tranche_id=f'scope-{index:03d}', scope_ids=[cell['cell_id']], topic_id=cell['topic_id'], research_kind=cell['research_kind'], source_ids=sorted({c['version_id'] for c in relevant if c['version_id']}), source_section_ranges=[c['section'] for c in relevant], next_leads=[f"Envanter kaynak bölümü incelenecek: {c['id']}" for c in relevant] + ['Konu, parti, aktör ve dönemle kurum, TBMM, parti, haber ve bağımsız rapor araması yapılacak.'], processed_at=None, closure_refs=[], state='pending'))
out = dict(version=1, party_id='tip', base_release=inventory['base_release'], cutoff_at=inventory['cutoff_at'], period_start='2017-11-07', status='pending', note='Kuyruk oluşturuldu; kaynak bölümleri ve hücreler araştırılmış veya kapanmış değildir.', tranches=tranches)
Path('data/practices/04-tip-tranches.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n')
print('TİP kuyruğu:',len(cells),'hücre,',len(collections),'kaynak koleksiyonu')
