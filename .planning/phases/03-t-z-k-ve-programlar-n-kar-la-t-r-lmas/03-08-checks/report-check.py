import json,sys,re,html
from pathlib import Path
from html.parser import HTMLParser

release=sys.argv[1];payload=json.load(open(sys.argv[2]));folder=Path(release) if Path(release).is_absolute() else Path('data/releases',release);report=folder/'index.html';data=report.read_text()
class Scan(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.articles={};self.sources=set();self.sourcehref={};self.sourcetext={};self.srcid=None;self.srcdepth=0;self.current=None;self.depth=0
 def handle_starttag(self,tag,attrs):
  a=dict(attrs);id=a.get('id','')
  if id.startswith('source-'):
   self.sources.add(id)
   if tag=='details':self.srcid=id;self.srcdepth=1;self.sourcehref[id]=[];self.sourcetext[id]=[]
  elif self.srcid and tag=='details':self.srcdepth+=1
  if self.srcid and tag=='a':self.sourcehref[self.srcid].append(a.get('href',''))
  if tag=='article' and (id.startswith('comparison-') or id.startswith('dossier-comparison-')):self.current=id;self.depth=1;self.articles[id]={'text':[],'href':[]};return
  if self.current:
   if tag=='article':self.depth+=1
   if tag=='a':self.articles[self.current]['href'].append(a.get('href',''))
 def handle_endtag(self,tag):
  if self.srcid and tag=='details':
   self.srcdepth-=1
   if not self.srcdepth:self.srcid=None
  if self.current and tag=='article':
   self.depth-=1
   if not self.depth:self.current=None
 def handle_data(self,text):
  if self.srcid:self.sourcetext[self.srcid].append(text)
  if self.current:self.articles[self.current]['text'].append(text)
p=Scan();p.feed(data)
rec=payload['records'];rows=[x['values'] for x in rec if x['kind']=='comparison_row'];fields=[x['values'] for x in rec if x['kind']=='comparison_field'];findings={x['values']['id']:x['values'] for x in rec if x['kind']=='finding'};ev=[x['values'] for x in rec if x['kind']=='finding_evidence'];errors=[]
published=json.load(open(folder/'records.json'));passages={x['id']:x for x in published['passage']};versions={x['id']:x for x in published['document_version']};views={x['version_id']:x for x in published['archive_view']};attrs={x['version_id']:x for x in published['source_attribution']}
for row in rows:
 rid=row['id'];ff=[x for x in fields if x['row_id']==rid]
 for prefix,other in [('comparison-','dossier-comparison-'),('dossier-comparison-','comparison-')]:
  key=prefix+rid;a=p.articles.get(key)
  if a is None:errors.append('missing '+key);continue
  if '#'+other+rid not in a['href']:errors.append('cross-link '+key)
  text=' '.join(' '.join(a['text']).split())
  if row['state']=='no_explicit_statement' and 'İncelenen kapsamda açık ifade bulunmadı.' not in text:errors.append('scope '+key)
  if row['state']=='document_missing' and 'Bulunamadı' not in text:errors.append('missing-state '+key)
  for field in ff:
   for which in ('summary_finding_id','quote_finding_id'):
    f=findings[field[which]];needle=' '.join(html.unescape(re.sub('<[^>]*>','',f['text'])).split())
    if needle not in text:errors.append('text '+key+' '+f['id'])
    for e in [e for e in ev if e['finding_id']==f['id']]:
     anchor='source-'+e['passage_id']
     if '#'+anchor not in a['href'] or anchor not in p.sources:errors.append('source '+key+' '+anchor)
     version=versions[passages[e['passage_id']]['version_id']];target=views[version['id']]['index_path'] if version['id'] in views else version['readable_path'];href='../../'+target
     if href not in p.sourcehref.get(anchor,[]) or not Path('data',target).is_file():errors.append('archive '+key+' '+href)
     attr=attrs.get(version['id']);source_text=' '.join(' '.join(p.sourcetext.get(anchor,[])).split())
     if attr and attr.get('publisher') and attr['publisher'] not in source_text:errors.append('attribution '+key+' '+anchor)
if errors:
 print('REPORT_LINK_CHECK_FAILED',len(errors),*errors[:30],sep='\n');sys.exit(1)
print('REPORT_LINK_CHECK_OK',len(rows),'rows in both views; source anchors and findings checked')
