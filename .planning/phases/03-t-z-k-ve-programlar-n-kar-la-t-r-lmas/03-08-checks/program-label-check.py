import html,json,re,sys
from pathlib import Path
folder=Path(sys.argv[1]) if Path(sys.argv[1]).is_absolute() else Path('data/releases',sys.argv[1])
data=json.loads((folder/'records.json').read_text());report=(folder/'index.html').read_text();p=json.load(open('data/comparisons/03-dbp-program.json'))
versions={v['id']:v for v in data['document_version']};attrs={a['version_id']:a for a in data['source_attribution']};fields=[x['values'] for x in p['records'] if x['kind']=='comparison_field'];evidence=[x['values'] for x in p['records'] if x['kind']=='finding_evidence'];errors=[];count=0
def plain(s):return ' '.join(html.unescape(re.sub('<[^>]*>',' ',s)).split())
for item in p['records']:
 if item['kind']!='comparison_row':continue
 row=item['values'];version=row['version_id']
 if row['source_role']!='historical' or row['state']!='evidence':continue
 publisher=attrs[version]['publisher'];label=versions[version]['version_label'];other='WordPress' if version=='0207-dbp-bdp-program-v1' else 'Blogspot'
 for prefix in ('comparison-','dossier-comparison-'):
  try:article=report.split('id="'+prefix+row['id']+'"',1)[1].split('</article>',1)[0]
  except IndexError:errors.append('missing '+prefix+row['id']);continue
  text=plain(article)
  if publisher not in text or label not in text or other in text:errors.append('label '+prefix+row['id'])
  for f in [f for f in fields if f['row_id']==row['id']]:
   for ev in [e for e in evidence if e['finding_id']==f['quote_finding_id']]:
    pid=ev['passage_id']
    try:header=plain(report.split('id="source-'+pid+'"',1)[1].split('</summary>',1)[0])
    except IndexError:errors.append('source '+pid);continue
    if publisher not in header or label not in header or other in header:errors.append('source-label '+pid)
  count+=1
if errors:
 print('PROGRAM_LABEL_CHECK_FAILED',len(errors),*errors[:20],sep='\n');sys.exit(1)
print('PROGRAM_LABEL_CHECK_OK',count,'version-specific article labels checked')
