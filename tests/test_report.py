"""Raporun gerçek veride erişilebilir sekme sözleşmesi."""
import json
import re
import sys
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from rapor import render_report
from browser_probe import probe_tabs


class ReaderText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if self.depth:
            self.depth += 1
        elif tag == 'article' and 'data-match-id' in attrs or tag == 'p' and 'data-status' in attrs:
            self.depth = 1

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1

    def handle_data(self, data):
        if self.depth:
            self.parts.append(data)


class ReportTest(unittest.TestCase):
    def test_method_prioritizes_primary_sources_and_old_renderer_is_reproducible(self):
        from rapor_v14 import render_report as old_render
        root=Path(__file__).resolve().parents[1]
        release=root/'data/releases/1d6b49b307f04a258c1a11d90978fe7c'
        data=json.loads((release/'records.json').read_text())
        self.assertEqual(old_render(data),(release/'index.html').read_text())
        report=render_report(data)
        self.assertIn('<details id="scope-method"><summary>Kapsam ve yöntem</summary>',report)
        method=report.split('<details id="scope-method">',1)[1].split('</p>',1)[0]
        self.assertIn('Birincil kaynaklara',method)
        self.assertIn('öncelik verilir',method)
        self.assertIn('İkincil kaynaklar da kullanılır',method)

    def test_mobile_navigation_hint_and_readable_touch_targets(self):
        from browser_probe import browser
        executable=browser()
        if not executable: self.skipTest('Headless Chrome bulunamadı')
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca/records.json').read_text())
        report=render_report(data)
        marker='''<script>(()=>{
const tabs=document.querySelector('[role=tablist]'),hint=document.querySelector('.party-scroll-hint');
const citation=[...document.querySelectorAll('.citation')].find(x=>x.getClientRects().length);
const section=[...document.querySelectorAll('.section-links a')].find(x=>x.getClientRects().length);
const type=[...document.querySelectorAll('.source-type')].find(x=>x.getClientRects().length);
const checks=[getComputedStyle(hint).display!=='none',tabs.scrollWidth>tabs.clientWidth,citation.getBoundingClientRect().height>=44,section.getBoundingClientRect().height>=44,parseFloat(getComputedStyle(type).fontSize)>=14];
const first=tabs.querySelector('[role=tab]');first.focus();first.dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true}));checks.push(document.activeElement.id==='tab-comparison');
document.body.dataset.mobileChecks=checks.join(',');document.body.dataset.mobileProbe=checks.every(Boolean)?'PASS':'FAIL';
})()</script>'''
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/'report.html';path.write_text(report.replace('</html>',marker+'</html>'))
            result=subprocess.run([executable,'--headless','--no-sandbox','--disable-gpu','--window-size=360,800','--dump-dom',path.as_uri()],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr[-1000:])
        checks=re.findall(r'data-mobile-(?:checks|probe)="[^"]*"',result.stdout)
        self.assertIn('data-mobile-probe="PASS"',checks,str(checks))

    def test_attribution_is_never_copied_from_same_hash_sibling(self):
        import copy
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca/records.json').read_text())
        original=data['source_attribution'][0]
        version=next(v for v in data['document_version'] if v['id']==original['version_id'])
        passage=next(p for p in data['passage'] if p['version_id']==version['id'])
        sibling=copy.deepcopy(version);sibling['id']='test-sibling-version'
        data['document_version'].append(sibling)
        attribution=copy.deepcopy(original);attribution.update(version_id=sibling['id'],author='Farklı Yazar',publisher='Farklı Yayıncı',published_at='2000-01-01',basis='Farklı dayanak')
        data['source_attribution'].append(attribution)
        report=render_report(data)
        source=report.split('id="source-'+passage['id']+'"',1)[1].split('</dl>',1)[0]
        self.assertIn(original['publisher'],source)
        for value in ('Farklı Yazar','Farklı Yayıncı','Farklı dayanak','01.01.2000'):
            self.assertNotIn(value,source)
        history=report.split('id="version-history-'+version['id']+'"',1)[1].split('</details>',1)[0]
        self.assertIn('Bu sürümün yazarı: Farklı Yazar',history)
        self.assertIn('Farklı dayanak',history)

    def test_known_authors_remain_attached_to_their_source_versions(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca/records.json').read_text())
        report=render_report(data)
        versions={v['id']:v for v in data['document_version']}
        for donor in ('epm-national-author-v2','epm-provinces-author-v2','epm-finance-author-v2'):
            attribution=next(a for a in data['source_attribution'] if a['version_id']==donor)
            original=next(v for v in data['document_version'] if v['document_id']==versions[donor]['document_id'] and v['id']!=donor and v['sha256']==versions[donor]['sha256'])
            history=report.split('id="version-history-'+original['id']+'"',1)[1].split('</details>',1)[0]
            self.assertIn('Bu sürümün yazarı: '+attribution['author'],history)
            self.assertIn(attribution['basis'],history)

    def test_renderer_13_reproduces_existing_release(self):
        from rapor_v13 import render_report as old_render
        root=Path(__file__).resolve().parents[1]
        release=root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca'
        data=json.loads((release/'records.json').read_text())
        self.assertEqual(old_render(data),(release/'index.html').read_text())

    def test_pdf_quote_entities_are_literal_and_html_entities_decode(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca/records.json').read_text())
        finding=next(f for f in data['finding'] if f['provenance']=='quote')
        related=[e for e in data['finding_evidence'] if e['finding_id']==finding['id']]
        passage=next(p for p in data['passage'] if p['id']==related[0]['passage_id'])
        version=next(v for v in data['document_version'] if v['id']==passage['version_id'])
        raw='literal &copy; &amp; &#169;'
        finding['text']=passage['exact']=raw
        version['original_path']='objects/'+'0'*64+'/original.pdf'
        report=render_report(data)
        finding_html=report.split('data-finding-id="'+finding['id']+'"',1)[1].split('</p>',1)[0]
        citation_html=report.split('id="source-'+passage['id']+'"',1)[1].split('</blockquote>',1)[0]
        for section in (finding_html,citation_html):
            self.assertIn('literal &amp;copy; &amp;amp; &amp;#169;',section)
        version['original_path']='objects/'+'0'*64+'/original.html.bin'
        report=render_report(data)
        finding_html=report.split('data-finding-id="'+finding['id']+'"',1)[1].split('</p>',1)[0]
        self.assertIn('literal © &amp; ©',finding_html)

    def test_identity_note_uses_its_passage_origin_for_entities(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/bcc67d04d9d741e191589d0f5ac173ca/records.json').read_text())
        note=next(n for n in data['dossier_identity_note'] if n['provenance']=='quote')
        passage=next(p for p in data['passage'] if p['id']==note['own_passage_id'])
        version=next(v for v in data['document_version'] if v['id']==passage['version_id'])
        note['text']=passage['exact']='SAADET &amp; PARTİSİ'
        for suffix,expected in (('original.html.bin','SAADET &amp; PARTİSİ'),('original.pdf','SAADET &amp;amp; PARTİSİ')):
            version['original_path']='objects/'+'0'*64+'/'+suffix
            report=render_report(data)
            element=report.split('id="identity-note-'+note['id']+'"',1)[1].split('</p>',1)[0]
            self.assertIn(expected,element)

    def test_real_browser_reads_both_passive_archives(self):
        import arsiv
        from browser_probe import probe_archives
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases'/arsiv.current()/'records.json').read_text())
        views={v['version_id']:v for v in data['archive_view']}
        self.assertEqual(len(views),len(data['archive_view']),'Arşiv sürüm kimlikleri tekil kalmalı')
        self.assertTrue({'epm-charter-v1','epm-program-v1'}.issubset(views),
                        'Sonraki parti dosyaları eklenirken iki pilot arşivi korunmalı')
        result=probe_archives((root/'data/releases'/arsiv.current()/'index.html').as_uri(),(root/'data'/views['epm-charter-v1']['index_path']).as_uri(),(root/'data'/views['epm-program-v1']['index_path']).as_uri())
        self.assertEqual(result['status'],'BROWSER_ARCHIVES_OK')
    def test_reader_shows_party_content_and_faithful_archive_links(self):
        root=Path(__file__).resolve().parents[1]
        data=json.loads((root/'data/releases/b14c96c54e4b420686c46e5cfb1071a3/records.json').read_text())
        payload=json.loads((root/'data/dossiers/261111-epm-yeni-parti.json').read_text())
        data['source_policy']=[{'version':2,'legacy_findings':json.dumps([f['id'] for f in data['finding']])}]
        for row in payload['records']:
            target=data.setdefault(row['kind'],[])
            target.append(dict(dict.fromkeys(target[0],None) if target else {},**row['values']))
        report=render_report(data)
        self.assertIn('class="archive-view"',report,'Arşiv bağlantısı özgün görünümlü türeve gitmeli')
        self.assertIn('href="https://yenipartiyiz.biz"',report)
        self.assertIn('Neden kuruldu?',report)
        self.assertIn('Ne vaat ediyor?',report)
        self.assertIn('Ekonomim · Haber Merkezi',report)
        self.assertIn('Kocaeli TV · Bugün Kocaeli',report)
        self.assertIn('id="prior-yeni-parti-kurulus"',report)
        for row in (x['values'] for x in payload['records'] if x['kind']=='archive_view'):
            self.assertIn('href="../../'+row['index_path']+'"',report)

    def test_scoped_parties_and_summary_are_navigable(self):
        root = Path(__file__).resolve().parents[1]
        release = json.loads((root / 'data/current.json').read_text())['release_id']
        data = json.loads((root / 'data/releases' / release / 'records.json').read_text())
        report = render_report(data)
        self.assertIn('role="tablist"', report)
        self.assertEqual(re.findall(r'role="tab" id="tab-([^"]+)"', report),
                         ['yeni-parti', 'tip', 'dem', 'iyi', 'yeni-yol', 'dbp',
                          'emep', 'saadet', 'demokrat', 'comparison', 'phase-03-verification'])
        self.assertIn('id="comparison-summary"', report)
        for party in data['scope_party']:
            self.assertIn('id="party-' + party['party_id'] + '"', report)
        self.assertIn('data-finding-id="kurulus-summary"', report)
        self.assertIn('id="scope-method"', report)
        self.assertIn('<meta name="viewport" content="width=device-width, initial-scale=1">', report)
        self.assertIn('<h1>Türkiye siyasi partileri: kaynaklı araştırma raporu</h1>', report)
        for removed in ('Bu dokuz partilik ön liste', 'PROJECT.md kullanıcı kararı',
                        'Grup adından bireysel parti üyeliği çıkarılmaz.',
                        'Bu başlıklar beş parti dosyası başlığından ayrıdır.',
                        'TİP kaynağı yalnız sözlük dayanağıdır',
                        'Erişilen belgenin kesim günündeki sürümü ayrıca doğrulanmamıştır.',
                        'aday, dayanak doğrulanmadı', 'Doğrulanamadı:'):
            self.assertNotIn(removed, report)
        self.assertIn('id="attempt-0104-tuzuk-verify"',report)
        self.assertIn('class="status">Doğrulanamadı</span>', report)
        text = ReaderText()
        text.feed(report)
        visible = ' '.join(text.parts)
        self.assertIn('Aktör: kurumsal', visible)
        self.assertIn('uygun', visible)
        for raw in ('eligible', 'institution', 'unverified', 'excluded', 'candidate-0105'):
            self.assertNotIn(raw, visible)
        self.assertIn('data-status="eligible"', report)
        self.assertIn('aria-label="Kaynak:', report)
        passage = next(p for p in data['passage'] if p['id'] == 'kurulus')
        version = next(v for v in data['document_version'] if v['id'] == passage['version_id'])
        self.assertEqual(probe_tabs(report, 'kurulus', root / 'data', version['readable_path']), 'BROWSER_TABS_OK')

    def test_rejects_unsafe_archive_path_and_escapes_finding(self):
        root = Path(__file__).resolve().parents[1]
        release = json.loads((root / 'data/current.json').read_text())['release_id']
        data = json.loads((root / 'data/releases' / release / 'records.json').read_text())
        data['finding'][0]['text'] = '<script>alert(1)</script>'
        self.assertNotIn('<script>alert(1)</script>', render_report(data))
        data['lead'][0]['url'] = 'javascript:alert(1)'
        with self.assertRaises(ValueError):
            render_report(data)
        data['lead'][0]['url'] = 'https://example.org/'
        data['document_version'][0]['readable_path'] = '../outside'
        with self.assertRaises(ValueError):
            render_report(data)


if __name__ == '__main__':
    unittest.main()
