"""Sonraki zincirdeki yeni TBMM sürümlerine kaynak politikası atfı ekler."""
import hashlib,json
from pathlib import Path
c=Path(__file__).resolve().parent
names=['sivas-two-dem-draft.json','iklim-103-motions-dem-draft.json','sap-dem-draft.json','iklim-101-motions-dem-draft.json','textile-dem-draft.json','iklim-102-motions-dem-draft.json']
prefixes=('0406-sivas-2880-','0406-sivas-2883-','0406-iklim-103-printed-v1','0406-sap-2882-','0406-iklim-101-printed-v1','0406-textile-2881-','0406-iklim-102-printed-v1')
mapping={}
for name in names:
 p=c/name;old=hashlib.sha256(p.read_bytes()).hexdigest();obj=json.loads(p.read_text());attributed={e['values']['version_id'] for e in obj['entries'] if e['kind']=='source_attribution'};added=[]
 for e in obj['entries']:
  if e['kind']!='document_version':continue
  v=e['values'];vid=v['id']
  if not vid.startswith(prefixes) or vid in attributed:continue
  added.append(dict(kind='source_attribution',values=dict(version_id=vid,publisher='TBMM',author=None,kind='official',published_at=None,date_precision='unknown',social_handle=None,public_url=v['original_url'],basis='TBMM tutanak arşivi veya imzalı evrakın TBMM esas dosyası.')))
 obj['entries']+=added;p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');new=hashlib.sha256(p.read_bytes()).hexdigest();mapping[old]=new;print(name,len(added),old,new)
scripts=['build-sivas-dem-draft.py','build-iklim-103-motions-dem.py','build-sap-dem-draft.py','build-iklim-101-motions-dem.py','build-textile-dem-draft.py','build-iklim-102-motions-dem.py',
 'validate-sivas-two-dem.py','validate-iklim-103-dem.py','validate-sap-dem.py','validate-iklim-101-dem.py','validate-textile-dem.py','validate-iklim-102-dem.py',
 'independent-sivas-two-dem-qa.py','independent-iklim-103-dem-qa.py','independent-sap-dem-qa.py','independent-iklim-101-dem-qa.py','independent-textile-dem-qa.py','independent-iklim-102-dem-qa.py',
 'check-sivas-two-semantic.py','check-iklim-103-semantic.py','check-sap-semantic.py','check-iklim-101-semantic.py','check-textile-semantic.py','check-iklim-102-semantic.py']
for name in scripts:
 p=c/name;text=p.read_text();updated=text
 for old,new in mapping.items():updated=updated.replace(old,new)
 if text!=updated:p.write_text(updated)
