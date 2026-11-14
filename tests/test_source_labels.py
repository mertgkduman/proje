"""Per-version publisher labels for two real copies of the same BDP program."""
import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'src'))
from rapor import render_report, RENDERER_VERSION, version_source_label

class SourceLabelsTest(unittest.TestCase):
 def test_frozen_17_reproduces_actual_17_release_byte_for_byte(self):
  from rapor_v17 import render_report as frozen_render
  release=ROOT/'data/releases/b27a1387425c40889313e92dfc91739e'
  manifest=json.loads((release/'manifest.json').read_text())
  self.assertEqual(manifest['renderer_version'],17)
  data=json.loads((release/'records.json').read_text())
  self.assertEqual(frozen_render(data).encode(),(release/'index.html').read_bytes())

 def test_missing_version_label_does_not_copy_a_sibling_publisher(self):
  actual=version_source_label({'version_label':None},{'publisher':'BDP adlı Blogspot yayını'},'Başka WordPress yayını')
  self.assertEqual(actual,'BDP adlı Blogspot yayını · Sürüm belirtilmemiş')
  self.assertEqual(version_source_label({'version_label':'Eski sürüm'},None,'Belge başlığı'),'Belge başlığı · Eski sürüm')

 def test_untrusted_version_label_and_publisher_are_html_escaped(self):
  data=json.loads((ROOT/'data/releases/b27a1387425c40889313e92dfc91739e/records.json').read_text())
  v=next(v for v in data['document_version'] if v['id']=='0207-dbp-bdp-program-v1')
  a=next(a for a in data['source_attribution'] if a['version_id']==v['id'])
  a['publisher']='<img src=x onerror=alert(1)>';v['version_label']='<script>alert(2)</script>'
  report=render_report(data)
  self.assertNotIn('<img src=x onerror=alert(1)>',report)
  self.assertNotIn('<script>alert(2)</script>',report)
  self.assertIn('&lt;img src=x onerror=alert(1)&gt;',report)
  self.assertIn('&lt;script&gt;alert(2)&lt;/script&gt;',report)

 def test_same_document_two_publishers_keep_source_and_archive_in_both_views(self):
  data=json.loads((ROOT/'data/releases/b27a1387425c40889313e92dfc91739e/records.json').read_text())
  cases=[('blog','0207-dbp-bdp-program-v1','0207-dbp-bdp-program-copy','BDP adlı Blogspot yayını','views/588a2816176e57c77c90f752f6742dec/index.html'),('wordpress','0207-dbp-bdp-program-wordpress-v1','0207-dbp-bdp-program','Barış ve Demokrasi Partisi adlı WordPress yayını','views/b10cb215176d523b8d52cf98f4a05a99/index.html')]
  versions={v['id']:v for v in data['document_version']};passages={p['id']:p for p in data['passage']}
  self.assertEqual(versions[cases[0][1]]['document_id'],versions[cases[1][1]]['document_id'])
  for name,version,pid,publisher,path in cases:
   rid='test-publisher-'+name;pair=rid+'-pair';sf=rid+'-summary';qf=rid+'-quote'
   data['comparison_row'].append(dict(id=rid,topic_id='demokrasi-katilim',taxonomy_version=2,party_id='dbp',level='ulusal',organ='Sınama',version_id=version,alternative_group=None,source_role='historical',state='evidence',scope_id=None,missing_id=None,selection_reason='Kaynak sürümü bağımsızdır.'))
   for fid,text,provenance,role in [(sf,'Tarihsel programdan kaynaklı içerik.','summary','support'),(qf,passages[pid]['exact'],'quote','quotation')]:
    data['finding'].append(dict(id=fid,party_id='dbp',heading='Program',pair_id=pair,text=text,provenance=provenance,epistemic_type='claim'))
    data['finding_evidence'].append(dict(finding_id=fid,passage_id=pid,role=role))
   data['comparison_field'].append(dict(id=rid+'-field',row_id=rid,field='principle',summary_finding_id=sf,quote_finding_id=qf,condition_key=None))
  report=render_report(data)
  self.assertEqual(RENDERER_VERSION,18)
  for name,version,pid,publisher,path in cases:
   label=versions[version]['version_label'] if name=='blog' else publisher+' · '+versions[version]['version_label']
   for prefix in ('comparison-','dossier-comparison-'):
    section=report.split('id="'+prefix+'test-publisher-'+name+'"',1)[1].split('</article>',1)[0]
    self.assertIn('Tarihsel belge: '+label,section)
    self.assertIn('href="#source-'+pid+'"',section)
    self.assertIn('>['+label+']</a>',section)
    other=cases[1 if name=='blog' else 0][3]
    self.assertNotIn(other,section)
   details=report.split('id="source-'+pid+'"',1)[1]
   header=details.split('</summary>',1)[0]
   links=details.split('<div class="source-links">',1)[1].split('</div>',1)[0]
   self.assertIn(publisher,header)
   self.assertIn(versions[version]['version_label'],header)
   self.assertIn('href="../../'+path+'"',links)
   self.assertTrue((ROOT/'data'/path).is_file())

if __name__=='__main__':unittest.main()
