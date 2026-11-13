import sqlite3
import shutil
import tempfile
import unittest
import json
import hashlib
import datetime as dt
import subprocess
import sys
from pathlib import Path

import arsiv
import dosyalar


def copy_phase_one_data(source, target):
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('.write.lock', '.staging'))
    (target / 'current.json').write_text(json.dumps({'release_id': '26de2a4efc584b5b9f81ea67dcb8d65c'}) + '\n')


def add_tip_tracer(work):
    reviewed_at = dt.datetime.now(dt.timezone.utc).isoformat()
    db=arsiv.connect_readonly(work/'records.sqlite3')
    version=dict(db.execute("SELECT * FROM document_version WHERE id='tip-registry-v1'").fetchone());db.close()
    records = [
        ('source_attribution', dict(version_id='tip-registry-v1',kind='registry',publisher='Yargıtay Cumhuriyet Başsavcılığı',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=version['final_url'],basis='Arşivlenmiş sicil kaydı.')),
        ('passage', dict(id='tip-foundation-passage', version_id='tip-registry-v1', exact='07.11.2017', section='Kuruluş Tarihi')),
        ('finding', dict(id='tip-foundation-summary', party_id='tip', heading='Kuruluş', pair_id='tip-foundation', text='Yargıtay sicilinde Türkiye İşçi Partisinin kuruluş tarihi 07.11.2017 olarak yer alır.', provenance='summary', epistemic_type='registry')),
        ('finding', dict(id='tip-foundation-quote', party_id='tip', heading='Kuruluş', pair_id='tip-foundation', text='07.11.2017', provenance='quote', epistemic_type='registry')),
        ('finding_evidence', dict(finding_id='tip-foundation-summary', passage_id='tip-foundation-passage', role='support')),
        ('finding_evidence', dict(finding_id='tip-foundation-quote', passage_id='tip-foundation-passage', role='support')),
        ('review', dict(id='tip-foundation-summary-review', kind='finding', subject_id='tip-foundation-summary', reviewer_kind='agent', reviewed_at=reviewed_at, result='reviewed', reason='Arşivlenmiş Yargıtay sicilindeki kuruluş tarihi satırı incelendi.')),
        ('review', dict(id='tip-foundation-quote-review', kind='finding', subject_id='tip-foundation-quote', reviewer_kind='agent', reviewed_at=reviewed_at, result='reviewed', reason='Alıntı arşivlenmiş sicildeki tarih ile karşılaştırıldı.')),
        ('event_date', dict(id='tip-foundation-date', party_id='tip', passage_id='tip-foundation-passage', event_at='2017-11-07', date_precision='day', date_unknown_reason=None, scope_status='inside')),
        ('dossier_field', dict(id='tip-foundation-field', party_id='tip', field='foundation_date', value='07.11.2017', finding_id='tip-foundation-summary', missing_id=None, as_of='2017-11-07', date_precision='day', date_unknown_reason=None)),
        ('dossier_event', dict(id='tip-foundation-event', party_id='tip', kind='foundation', event_date_id='tip-foundation-date', summary_finding_id='tip-foundation-summary')),
        ('dossier_source', dict(party_id='tip', heading='Kuruluş', version_id='tip-registry-v1', reason='Kuruluş tarihi için Yargıtay sicili.')),
    ]
    for kind, values in records: arsiv.record(work, kind, values)
    return [{'kind':kind, 'values':values} for kind,values in records]


class DossierTracer(unittest.TestCase):
    def test_refresh_requires_unchanged_completed_delivery(self):
        import copy
        delivery={'party_id':'demokrat','stage':'complete','completed_prefix':list(dosyalar.DELIVERY_ORDER)}
        base={'phase2_delivery':delivery}
        candidate={'phase2_delivery':copy.deepcopy(delivery),'phase2_refresh':True}
        self.assertIsNone(dosyalar.validate_delivery_prefix(base,candidate))
        for replacement in (
            dict(delivery,completed_prefix=delivery['completed_prefix'][:-1]),
            dict(delivery,completed_prefix=list(reversed(delivery['completed_prefix']))),
            dict(delivery,completed_prefix=delivery['completed_prefix']+['extra']),
            dict(delivery,party_id='saadet'),dict(delivery,stage='tracer'),
        ):
            with self.subTest(delivery=replacement),self.assertRaises(ValueError):
                dosyalar.validate_delivery_prefix(base,{'phase2_delivery':replacement,'phase2_refresh':True})
        with self.assertRaises(ValueError):dosyalar.validate_delivery_prefix({'phase2_delivery':dict(delivery,completed_prefix=delivery['completed_prefix'][:-1])},candidate)
        with self.assertRaises(ValueError):dosyalar.validate_delivery_prefix(base,{'phase2_delivery':delivery})
        with self.assertRaises(ValueError):dosyalar.validate_delivery_prefix(base,{'phase2_delivery':delivery,'phase2_refresh':False})
        with self.assertRaises(ValueError):dosyalar.validate_delivery_prefix({}, {'phase2_refresh':True})

    def test_publish_refresh_and_party_are_exclusive(self):
        result=subprocess.run([sys.executable,'src/arsiv.py','publish','--workspace','unused','--party','tip','--refresh'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('not allowed with argument',result.stderr)

    def test_replaying_dossier_keeps_attempt_derived_lead_status_and_rejects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            old=arsiv.DATA
            try:
                arsiv.DATA=Path(tmp)/'data';copy_phase_one_data(old,arsiv.DATA)
                work=arsiv.open_workspace(tmp)
                db=arsiv.connect_readonly(work/'records.sqlite3')
                v=dict(db.execute("SELECT * FROM document_version WHERE id='tip-registry-v1'").fetchone())
                method=dict(db.execute('SELECT * FROM method ORDER BY version DESC LIMIT 1').fetchone());db.close()
                lead=dict(id='replay-lead',party_id='tip',heading='Kuruluş',topic_id='tip-replay',url=v['original_url'],normalized_url=arsiv.normalize_url(v['original_url']),relevance_reason='Arşivli gerçek sicil.',status='pending')
                attempt=dict(id='replay-attempt',lead_id=lead['id'],party_id='tip',heading='Kuruluş',topic_id=lead['topic_id'],type='access',query=lead['url'],attempted_at=v['accessed_at'],result='examined',reason='Gerçek arşivli sicil okundu.',source_version_id=v['id'])
                payload=dict(schema_version=1,party_id='tip',method_version=method['version'],cutoff_at=method['cutoff_at'],records=[dict(kind='lead',values=lead),dict(kind='attempt',values=attempt)])
                dosyalar.load_dossier(work,payload);dosyalar.load_dossier(work,payload)
                db=arsiv.connect(work/'records.sqlite3')
                self.assertEqual(db.execute("SELECT status FROM lead WHERE id='replay-lead'").fetchone()[0],'examined')
                db.execute("DELETE FROM attempt WHERE id='replay-attempt'");db.commit();db.close()
                with self.assertRaisesRegex(ValueError,'çelişen'):dosyalar.load_dossier(work,payload)
            finally:arsiv.DATA=old

    def test_complete_collection_keeps_later_research_explicitly_unexamined(self):
        # Faz 2 kapsamı: ilk üç başlıkta girişimli belge sonucu; diğer iki
        # başlıkta henüz çalışılmadı. Tam teslim araştırma yapılmış gibi görünmez.
        data = {k:[] for k in ('finding','passage','document_version','document','event_date','finding_evidence','review','dossier_field','dossier_event','dossier_source','version_context','version_relation','dossier_identity_note','party_identity_revision','research_state','missing')}
        for i, heading in enumerate(dosyalar.HEADINGS):
            data['research_state'].append(dict(party_id='tip',heading=heading,state='reviewed' if i<3 else 'not_researched'))
            if i<3:data['missing'].append(dict(id='gap-'+str(i),party_id='tip',heading=heading))
        for field in dosyalar.FIELDS[:5]:
            data['dossier_field'].append(dict(party_id='tip',field=field,value=None,finding_id=None,missing_id='gap-0',as_of=None,date_precision='unknown',date_unknown_reason='Testte alanın araştırma sonucu eksik.'))
        self.assertTrue(dosyalar.validate_dossier(data,'tip','complete'))
        data['research_state'][1]['state']='not_researched'
        with self.assertRaises(ValueError):dosyalar.validate_dossier(data,'tip','complete')
        data['research_state'][1]['state']='reviewed'
        data['missing'].append(dict(id='fake-unexamined-gap',party_id='tip',heading=dosyalar.HEADINGS[3]))
        with self.assertRaises(ValueError):dosyalar.validate_dossier(data,'tip','complete')

    def test_tip_report_exposes_identity_and_grouped_sources(self):
        data = json.loads((arsiv.DATA / 'releases' / arsiv.current() / 'records.json').read_text())
        from rapor import render_report
        report = render_report(data)
        self.assertIn('id="identity-tip"', report)
        self.assertIn('id="chronology-tip"', report)
        for key in ('kurulus', 'tuzuk', 'program', 'soylem-uygulama', 'finansman'):
            self.assertIn(f'id="sources-tip-{key}"', report)
        self.assertIn('id="version-history-tip-registry-v1"', report)

    def test_each_finding_keeps_its_own_version_in_history(self):
        from rapor import render_report
        data = json.loads((arsiv.DATA / 'releases' / arsiv.current() / 'records.json').read_text())
        old = next(v for v in data['document_version'] if v['id'] == 'tip-registry-v1')
        old['version_label'] = 'Eski sürüm'
        new = dict(old, id='test-version-two', version_label='Yeni sürüm')
        data['document_version'].append(new)
        passage = next(p for p in data['passage'] if p['id'] == 'tip-foundation-passage')
        data['passage'].append(dict(passage, id='test-passage-two', version_id=new['id']))
        f = next(f for f in data['finding'] if f['id'] == 'tip-foundation-summary')
        data['finding'].append(dict(f, id='test-finding-two', pair_id='test-pair'))
        data['finding_evidence'].append(dict(finding_id='test-finding-two', passage_id='test-passage-two', role='support'))
        data['dossier_source'].append(dict(party_id='tip', heading='Tüzük', version_id=new['id'], reason='Test kaynağı'))
        report = render_report(data)
        self.assertIn('href="#source-tip-foundation-passage"', report)
        self.assertIn('href="#source-test-passage-two"', report)
        self.assertIn('id="version-history-test-version-two"', report)
        self.assertIn('Eski sürüm', report)
        self.assertIn('Yeni sürüm', report)
        import re
        ids = re.findall(r'\bid="([^"]+)"', report)
        self.assertEqual(len(ids), len(set(ids)))

    def test_archived_tip_registry_foundation_has_party_contract(self):
        release = arsiv.DATA / 'releases' / arsiv.current() / 'records.sqlite3'
        db = sqlite3.connect(release)
        db.row_factory = sqlite3.Row
        try:
            identity = db.execute("SELECT * FROM identity_observation WHERE entity_id='tip'").fetchone()
            passage = db.execute('SELECT v.original_path FROM passage p JOIN document_version v ON v.id=p.version_id WHERE p.id=?', (identity['passage_id'],)).fetchone()
            source = (arsiv.DATA / passage['original_path']).read_text(encoding='utf-8')
            self.assertIn('07.11.2017', source)
            self.assertTrue(hasattr(arsiv, 'foundation_for_party'), 'Partiye özgü kuruluş sözleşmesi eksik')
            self.assertEqual(arsiv.foundation_for_party(db, 'tip'), identity['valid_from'])
        finally:
            db.close()

    def test_event_dates_respect_party_and_foundation(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_data = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                copy_phase_one_data(old_data, arsiv.DATA)
                work = arsiv.open_workspace(tmp)
                event = dict(id='tip-foundation', party_id='tip', passage_id='tip-registry-name',
                             event_at='2017-11-07', date_precision='day',
                             date_unknown_reason=None, scope_status='inside')
                arsiv.record(work, 'event_date', event)
                for changes in (dict(id='before', event_at='2017-11-06'),
                                dict(id='wrong-owner', passage_id='kurulus'),
                                dict(id='after', event_at='2026-11-11')):
                    with self.assertRaises(ValueError):
                        arsiv.record(work, 'event_date', dict(event, **changes))
            finally:
                arsiv.DATA = old_data

    def test_real_tip_publish_audit_html_and_receipt_in_isolated_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_data = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'
                copy_phase_one_data(old_data, arsiv.DATA)
                old = arsiv.current()
                old_folder = arsiv.DATA / 'releases' / old
                hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in old_folder.iterdir() if p.is_file()}
                work = arsiv.open_workspace(tmp)
                records = add_tip_tracer(work)
                db = arsiv.connect_readonly(work / 'records.sqlite3')
                try: method = db.execute('SELECT version,cutoff_at FROM method ORDER BY version DESC LIMIT 1').fetchone()
                finally: db.close()
                payload = {'schema_version':1, 'party_id':'tip', 'method_version':method['version'], 'cutoff_at':method['cutoff_at'], 'records':records, 'research_log':[], 'important_gaps':[]}
                dosyalar.load_dossier(work, payload)
                conflict = json.loads(json.dumps(payload)); conflict['records'][1]['values']['text'] = 'Çelişkili kayıt'
                with self.assertRaises(ValueError): dosyalar.load_dossier(work, conflict)
                release = arsiv.publish_release(work, party='tip', stage='tracer')
                self.assertNotEqual(old, release)
                self.assertEqual(dosyalar.validate_phase_two(release, 'tip', 'tracer'), release)
                self.assertEqual(arsiv.validate_phase_one(release), release)
                folder = arsiv.DATA / 'releases' / release
                manifest = json.loads((folder / 'manifest.json').read_text())
                self.assertEqual(manifest['phase2_delivery'], {'party_id':'tip','stage':'tracer','completed_prefix':[]})
                # Schema 5 keeps its frozen renderer as later schemas advance.
                self.assertEqual(manifest['renderer_version'], 15)
                self.assertEqual(manifest['source_policy_version'],2)
                data = json.loads((folder / 'records.json').read_text())
                self.assertEqual(data['schema_version'], 5)
                report = (folder / 'index.html').read_text()
                panel = report.split('id="party-tip"',1)[1].split('id="party-dem"',1)[0]
                self.assertIn('07.11.2017', panel)
                self.assertIn('href="#source-tip-foundation-passage"', panel)
                self.assertIn('id="source-tip-foundation-passage"', panel)
                self.assertEqual(report.count('id="source-tip-foundation-passage"'), 1)
                self.assertIn('Arşivde tek sürüm var.', panel)
                from browser_probe import probe_tabs
                source = next(v for v in data['document_version'] if v['id'] == 'tip-registry-v1')
                self.assertEqual(probe_tabs(report, 'tip-foundation-passage', arsiv.DATA, source['readable_path']), 'BROWSER_TABS_OK')
                receipt = dosyalar.make_delivery_receipt(release, 'tip')
                path = Path(tmp) / 'receipt.json'; path.write_text(json.dumps(receipt), encoding='utf-8')
                self.assertEqual(dosyalar.check_delivery_receipt(path)['release_id'], release)
                self.assertTrue(receipt['important_gaps'])
                self.assertIn('Kuruluş: araştırma tamamlanmadı', receipt['important_gaps'])
                self.assertIn('Kuruluş tarihi: 07.11.2017', receipt['added_content'])
                cli = 'import sys; from pathlib import Path; sys.path.insert(0, "src"); import arsiv; arsiv.DATA=Path(sys.argv[1]); sys.argv=["arsiv.py", "audit", "--release", "current", "--phase", "2", "--party", "tip", "--stage", "tracer"]; arsiv.main()'
                result = subprocess.run([sys.executable, '-c', cli, str(arsiv.DATA)], text=True, capture_output=True, check=True)
                self.assertIn('PHASE2_TRACER_OK', result.stdout)
                self.assertEqual(arsiv.audit_release(old), old)
                self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in old_folder.iterdir() if p.is_file()})
                work = arsiv.open_workspace(tmp)
                with self.assertRaises(ValueError): arsiv.publish_release(work)
            finally:
                arsiv.DATA = old_data

    def test_migration_rollback_and_invalid_records_leave_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_data = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'; copy_phase_one_data(old_data, arsiv.DATA)
                before = arsiv.current()
                with self.assertRaises(RuntimeError): arsiv.open_workspace(tmp, fail_at='migration')
                self.assertEqual(arsiv.current(), before)
                self.assertFalse((arsiv.DATA / '.write.lock').exists())
                work = arsiv.open_workspace(tmp); add_tip_tracer(work)
                with sqlite3.connect(work / 'records.sqlite3') as db:
                    db.execute("UPDATE dossier_field SET value='uydurma' WHERE id='tip-foundation-field'")
                with self.assertRaises(ValueError): arsiv.publish_release(work, party='tip', stage='tracer')
                self.assertEqual(arsiv.current(), before)
                with self.assertRaises(ValueError): dosyalar.validate_delivery_prefix({}, {'phase2_delivery': {'party_id':'dem','stage':'complete','completed_prefix':['dem']}})
            finally: arsiv.DATA = old_data

    def test_registry_confirmation_and_version_cycle_are_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_data = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'; copy_phase_one_data(old_data, arsiv.DATA)
                work = arsiv.open_workspace(tmp)
                db = arsiv.connect(work / 'records.sqlite3')
                try:
                    count = db.execute("SELECT count(*) FROM scope_observation WHERE party_id='tip'").fetchone()[0]
                    with db:
                        db.execute("DELETE FROM identity_observation WHERE entity_id='tip'")
                        db.execute("UPDATE party SET registry_key='tbmm-tip', legal_name='TBMM geçici kaydı' WHERE id='tip'")
                        dosyalar.identity_confirmation(db, 'tip', dict(registry_key='yargitay-208', legal_name='TÜRKİYE İŞÇİ PARTİSİ', valid_from='2017-11-07', passage_id='tip-registry-name', changed_at='2026-11-11T15:00:00+00:00', reason='Sicil ile karşılaştırıldı'))
                    revision = db.execute("SELECT * FROM party_identity_revision WHERE party_id='tip'").fetchone()
                    self.assertEqual(revision['previous_registry_key'], 'tbmm-tip')
                    self.assertEqual(db.execute("SELECT count(*) FROM scope_observation WHERE party_id='tip'").fetchone()[0], count)
                    with self.assertRaises(ValueError):
                        with db:
                            dosyalar.identity_confirmation(db, 'tip', dict(registry_key='yargitay-999', legal_name='TÜRKİYE İŞÇİ PARTİSİ', valid_from='2017-11-07', passage_id='tip-registry-name', changed_at='2026-11-11T15:00:00+00:00', reason='Yanlış sicil'))
                    self.assertEqual(db.execute("SELECT registry_key FROM party WHERE id='tip'").fetchone()[0], 'yargitay-208')
                finally: db.close()
                add_tip_tracer(work)
                db = arsiv.connect_readonly(work / 'records.sqlite3')
                try: version = dict(db.execute("SELECT * FROM document_version WHERE id='tip-registry-v1'").fetchone())
                finally: db.close()
                version['id'] = 'tip-registry-v2'
                arsiv.record(work, 'document_version', version)
                rel = dict(id='tip-version-forward', version_id='tip-registry-v2', previous_version_id='tip-registry-v1', relation='related', passage_id='tip-foundation-passage', explanation_finding_id='tip-foundation-summary')
                for invalid in (dict(id='self', previous_version_id='tip-registry-v2'),
                                dict(id='other-document', previous_version_id='tip-charter-v1'),
                                dict(id='wrong-owner', passage_id='kurulus')):
                    with self.assertRaises(ValueError):
                        arsiv.record(work, 'version_relation', dict(rel, **invalid))
                arsiv.record(work, 'version_relation', rel)
                rel.update(id='tip-version-cycle', version_id='tip-registry-v1', previous_version_id='tip-registry-v2')
                with self.assertRaisesRegex(ValueError, 'döngü'): arsiv.record(work, 'version_relation', rel)
            finally: arsiv.DATA = old_data

    def test_official_site_rejects_unsupported_domain(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_data = arsiv.DATA
            try:
                arsiv.DATA = Path(tmp) / 'data'; copy_phase_one_data(old_data, arsiv.DATA)
                work = arsiv.open_workspace(tmp)
                for suffix, text, provenance in (('summary','https://unverified.example','summary'), ('quote','tip.org.tr','quote')):
                    fid = 'site-test-' + suffix
                    arsiv.record(work, 'finding', dict(id=fid,party_id='tip',heading='Kuruluş',pair_id='site-test',text=text,provenance=provenance,epistemic_type='registry'))
                    arsiv.record(work, 'finding_evidence', dict(finding_id=fid,passage_id='tip-tbmm-domain',role='support'))
                    arsiv.record(work, 'review', dict(id=fid+'-review',kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at='2026-11-11T15:00:00+00:00',result='reviewed',reason='Test'))
                with self.assertRaisesRegex(ValueError, 'sahipliği'):
                    arsiv.record(work, 'dossier_field', dict(id='site-test-field',party_id='tip',field='official_site',value='https://unverified.example',finding_id='site-test-summary',missing_id=None,as_of='2017-11-07',date_precision='day',date_unknown_reason=None))
            finally: arsiv.DATA = old_data
