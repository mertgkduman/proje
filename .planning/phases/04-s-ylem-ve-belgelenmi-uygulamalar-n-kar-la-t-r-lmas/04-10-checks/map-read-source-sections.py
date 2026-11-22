import datetime
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.skip = 0
        self.parts = []
    def handle_starttag(self, tag, attrs):
        self.skip += tag in ('script', 'style', 'nav', 'footer', 'header')
    def handle_endtag(self, tag):
        self.skip -= tag in ('script', 'style', 'nav', 'footer', 'header')
    def handle_data(self, data):
        if not self.skip and data.strip():
            self.parts.append(data.strip())

source = Path('data/objects/16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329/original.html.bin')
assert hashlib.sha256(source.read_bytes()).hexdigest() == '16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329'
parser = Text()
parser.feed(source.read_text())
normalize = lambda value: re.sub(r'\s+', ' ', value).strip()
text = normalize(' '.join(parser.parts))
queue = Path('data/practices/04-emep-tranches.json')
data = json.loads(queue.read_text())
assert all(row['processed_at'] is None for row in data['source_queue'])
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
matches = []
for row in data['source_queue']:
    section = normalize(row['section'])
    position = text.find(section)
    if position < 0 or len(section) < 3:
        continue
    receipts = ['charter-full-reading.json'] if row['source_role']=='charter' else ['program-first-reading.json','program-second-reading.json','program-third-reading.json']
    matches.append(dict(inventory_id=row['inventory_id'],source_role=row['source_role'],normalized_offset=position,normalized_length=len(section),reading_receipts=receipts))
    row.update(state='read',processed_at=now,reading_receipts=receipts)
assert len(matches)==66
receipt = dict(source_version='0208-emep-program-charter-v1',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),method='Önceden gerçekten okunan tam kaynak metninde envanter bölümünü boşluk normalleştirmesiyle tam eşleştir; bölüm bulunmadığında durumunu değiştirme.',matched_sections=matches,unmatched_count=len(data['source_queue'])-len(matches),note='Bu yalnız kaynak bölümünün okunmasıdır; araştırma hücresi veya kaynak ailesi kapanışı değildir.',recorded_at=now)
output=Path(__file__).parent/'read-source-sections-receipt.json'
assert not output.exists()
output.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
queue.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('SOURCE_SECTIONS_READ',len(matches),'PENDING',receipt['unmatched_count'])
