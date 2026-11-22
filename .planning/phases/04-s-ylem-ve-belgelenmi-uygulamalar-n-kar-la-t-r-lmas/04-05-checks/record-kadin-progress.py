import json
from datetime import datetime,timezone
from pathlib import Path

path=Path('data/practices/04-tip-tranches.json'); data=json.loads(path.read_text())
row=next(x for x in data['tranches'] if x['topic_id']=='toplumsal-cinsiyet' and x['research_kind']=='event')
assert row['state']=='pending' and row['processed_at'] is None and not row['closure_refs']
row['research_progress']=dict(recorded_at=datetime.now(timezone.utc).isoformat(),note='11 Ekim 2022 2/4653 teklifi, 2023 hükümsüzlük listesi ve aynı konulu 7 Eylül 2023 28. dönem 2/1566 teklifinin beşer sayfası okundu. Yeni teklif güncel kayıtta komisyondadır; kesim anı ayrıca araştırılır. Öneri, gerçekleşmiş hizmet ve ülke geneli ayrı tutulur.',source_ids=['0405-tip-kadin-274653-pdf-v1','0405-tip-sendika-hukumsuz-v1','0405-tip-281566-v1'],urls=['https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y6/T2/WebOnergeMetni/14cbec28-d778-4864-a43c-f95f23c46699.pdf','https://www5.tbmm.gov.tr/tutanaklar/TUTANAK/TBMM/d28/c001/tbmm28001001.pdf','https://tbmm.gov.tr/Yasama/KanunTeklifi/5c026b7d-af8e-41c7-91ef-018a6feefb2b'],status='partial')
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('PARTIAL_EVENT_LINKS',1)
