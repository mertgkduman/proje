import json
from datetime import datetime, timezone
from pathlib import Path

path = Path('data/practices/04-tip-tranches.json')
data = json.loads(path.read_text())
count = 0
for tranche in data['tranches']:
    if tranche['topic_id'] != 'barinma-konut':
        continue
    assert tranche['state'] == 'pending' and tranche['processed_at'] is None and not tranche['closure_refs']
    tranche['research_progress'] = {
        'recorded_at': datetime.now(timezone.utc).isoformat(),
        'note': '10 Mayıs 2022 haberindeki Baş söylemi, TBMM 2/4462 teklifinin 11 sayfası, ayrıntı ve hükümsüzlük kaydı ile partinin teklifi izleyen 19 Mayıs 2022 duyurusu okundu. Haber ile teklifteki vergi koşulları farklıdır; kayıtların source-review ve preview işlemleri, diğer dönem ve olay uçları açıktır.',
        'source_ids': ['0405-tip-274462-v1', '0405-tip-barinma-teklifi-v1', '0405-tip-barinma-10mayis-v1'],
        'urls': ['https://www.tbmm.gov.tr/Yasama/KanunTeklifi/f72877c1-e581-037b-e050-007f01005610', 'https://tip.org.tr/partiden-haberler/konut-krizine-karsi-kanun-teklifi-sunduk', 'https://www.indyturk.com/node/507986'],
        'status': 'partial',
    }
    count += 1
assert count == 2
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
print('PARTIAL_SCOPE_LINKS', count)
