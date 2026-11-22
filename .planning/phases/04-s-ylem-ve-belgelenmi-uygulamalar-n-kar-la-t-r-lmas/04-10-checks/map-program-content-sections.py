import datetime
import hashlib
import json
import re
from html.parser import HTMLParser
from pathlib import Path

class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip=0; self.parts=[]
    def handle_starttag(self, tag, attrs): self.skip += tag in ('script','style','nav','footer','header')
    def handle_endtag(self, tag): self.skip -= tag in ('script','style','nav','footer','header')
    def handle_data(self, data):
        if not self.skip and data.strip(): self.parts.append(data.strip())

source=Path('data/objects/16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329/original.html.bin')
assert hashlib.sha256(source.read_bytes()).hexdigest()=='16e8971e7cc015b0134f7836a9930200f04e9a298803f58801cf2261e3593329'
parser=Text();parser.feed(source.read_text());normalize=lambda s:re.sub(r'\s+',' ',s).strip();text=normalize(' '.join(parser.parts))
queue=Path('data/practices/04-emep-tranches.json');data=json.loads(queue.read_text());now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
receipts=['program-first-reading.json','program-second-reading.json','program-third-reading.json'];matches=[]
for row in data['source_queue']:
    section=row['section']
    if row['state']!='pending' or not section.startswith('G / '):continue
    content=re.sub(r'^[a-zA-Zı0-9]+\.\s*','',section.split(' — ',1)[1]);content=normalize(content)
    if len(content)<=30 or text.count(content)!=1:continue
    matches.append(dict(inventory_id=row['inventory_id'],normalized_offset=text.index(content),normalized_length=len(content),source_prefix_removed=section.split(' — ',1)[0],reading_receipts=receipts))
    row.update(state='read',processed_at=now,reading_receipts=receipts)
assert len(matches)==57
receipt=dict(source_version='0208-emep-program-charter-v1',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),method='Envanterin kaynakta bulunmayan G / bölüm etiketini ve numara işaretini çıkarıp önceden okunan içerik metnini boşluk normalleştirmesiyle tekil eşleştir.',matched_sections=matches,note='Bu, kaynak bölümünün okunmasıdır; konu, uygulama veya kapsam kapanışı değildir.',recorded_at=now)
out=Path(__file__).parent/'read-program-content-sections-receipt.json';assert not out.exists();out.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n');queue.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('PROGRAM_CONTENT_SECTIONS_READ',len(matches))
