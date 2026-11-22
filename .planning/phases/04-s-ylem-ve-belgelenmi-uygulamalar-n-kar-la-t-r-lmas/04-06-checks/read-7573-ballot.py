"""Arşivdeki 7573 açık oylama cetvelini parti etiketi ve satır sonucuyla say."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

class Rows(HTMLParser):
    def __init__(self):
        super().__init__(); self.rows=[]; self.row=None; self.cell=None
    def handle_starttag(self, tag, attrs):
        if tag=='tr': self.row=[]
        if tag=='td' and self.row is not None: self.cell=[]
    def handle_data(self, data):
        if self.cell is not None: self.cell.append(data)
    def handle_endtag(self, tag):
        if tag=='td' and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split())); self.cell=None
        if tag=='tr' and self.row is not None: self.rows.append(self.row); self.row=None

p=Path('data/practices/sources/dem/objects/40054311417ad26e380935c60142c0a172e5adfc897e72111a9ff9c7ce4ea833/original.html.bin')
parser=Rows(); parser.feed(p.read_bytes().decode('cp1254'))
rows=[r for r in parser.rows if any('Halkların Eşitlik ve Demokrasi Partisi' in cell for cell in r)]
assert all(len(r)==9 for r in rows)
counts=Counter(r[6] for r in rows)
print('DEM satır',len(rows),'sonuçlar',dict(counts))
for row in rows:
    if row[6]=='RET': print(' | '.join(row))
print('Elektronik ve nihai sonucu farklı olanlar:')
for row in rows:
    if row[4]!=row[6]: print(' | '.join(row))
