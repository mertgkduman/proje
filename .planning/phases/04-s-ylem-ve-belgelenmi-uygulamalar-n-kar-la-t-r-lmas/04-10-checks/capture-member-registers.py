import datetime,hashlib,json,re
from html.parser import HTMLParser
from pathlib import Path

class Table(HTMLParser):
 def __init__(self):super().__init__();self.in_table=False;self.in_row=False;self.in_cell=False;self.row=[];self.part=[];self.link=None;self.rows=[]
 def handle_starttag(self,tag,attrs):
  attrs=dict(attrs)
  if tag=='table' and attrs.get('id')=='mecTable':self.in_table=True
  elif self.in_table and tag=='tr':self.in_row=True;self.row=[];self.link=None
  elif self.in_row and tag=='td':self.in_cell=True;self.part=[]
  elif self.in_row and tag=='a' and '/Denetim/' in attrs.get('href',''):self.link=attrs['href']
 def handle_endtag(self,tag):
  if self.in_cell and tag=='td':self.row.append(' '.join(' '.join(self.part).split()));self.in_cell=False
  elif self.in_row and tag=='tr':
   if self.link and len(self.row)>=4:self.rows.append((self.row,self.link))
   self.in_row=False
  elif self.in_table and tag=='table':self.in_table=False
 def handle_data(self,data):
  if self.in_cell:self.part.append(data)

D=Path(__file__).parent;now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');captures=[];candidates={}
for member,guid in [('karaca','ec0ebeba-857c-4035-87fe-018876608a68'),('bayhan','5e7ef1d5-5b54-4c2b-8e2a-0188765ec27e')]:
 for family,route in [('question','UyeninSahibiOlduguYaziliSoruOnergeleri'),('research','UyeMeclisArastirmaOnergeleri')]:
  tmp=Path('/tmp/gsd0410-'+member+'-'+family+'.html');raw=tmp.read_bytes();path=D/('tbmm-'+member+'-'+family+'-register.html');assert not path.exists();path.write_bytes(raw)
  parser=Table();parser.feed(raw.decode('utf-8'));assert parser.rows,(member,family)
  url='https://tbmm.gov.tr/Milletvekili/'+route+'?ortakDonemId=134155f0-c3d6-4d24-893b-f3a2ef695ae7&Id='+guid
  captures.append(dict(member=member,family=family,url=url,raw=path.name,sha256=hashlib.sha256(raw).hexdigest(),row_count=len(parser.rows)))
  for cells,href in parser.rows:
   if not re.fullmatch(r'\d{2}\.\d{2}\.\d{4}',cells[2]):raise ValueError((member,family,cells[:3]))
   day=datetime.datetime.strptime(cells[2],'%d.%m.%Y').date().isoformat();state='pre_cutoff_day' if day<'2026-11-10' else ('cutoff_day_time_unknown' if day=='2026-11-10' else 'post_cutoff_day')
   key='https://tbmm.gov.tr'+href;entry=candidates.setdefault(key,dict(url=key,number=cells[1],date=day,title=cells[3],family=family,seen_in=[],cutoff_class=state,reading_state='pending_detail'));entry['seen_in'].append(member)
items=list(candidates.values());tranches=[]
for family in ('question','research'):
 eligible=[x for x in items if x['family']==family and x['cutoff_class']!='post_cutoff_day'];chunk=[];size=0
 for item in eligible:
  n=len(json.dumps(item,ensure_ascii=False))
  if chunk and size+n>40000:tranches.append(dict(id=f'emep-{family}-{1+sum(t["family"]==family for t in tranches):03}',family=family,urls=[x['url'] for x in chunk],state='pending',processed_at=None));chunk=[];size=0
  chunk.append(item);size+=n
 if chunk:tranches.append(dict(id=f'emep-{family}-{1+sum(t["family"]==family for t in tranches):03}',family=family,urls=[x['url'] for x in chunk],state='pending',processed_at=None))
catalog=dict(captured_at=now,cutoff='2026-11-10T14:38:46.154751+00:00',captures=captures,candidates=items,tranches=tranches,note='TBMM üye listesi satırları indekslendi; hiçbir ayrıntı gövdesi bu işlemle okunmuş veya kapsam kapatılmış sayılmaz. Kesim gününde saat ayrıca incelenir; erişim sonrası sayfa durumu kesim anına taşınmaz.')
out=D/'tbmm-member-research-catalog.json';assert not out.exists();out.write_text(json.dumps(catalog,ensure_ascii=False,indent=2)+'\n');print('REGISTER_CATALOG',len(items),'TRANCHES',len(tranches),[(x['member'],x['family'],x['row_count']) for x in captures])
