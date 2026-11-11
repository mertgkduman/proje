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
    shutil.copytree(source, target)
    (target / 'current.json').write_text(json.dumps({'release_id': '26de2a4efc584b5b9f81ea67dcb8d65c'}) + '\n')


def add_tip_tracer(work):
    reviewed_at = dt.datetime.now(dt.timezone.utc).isoformat()
    records = [
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
                self.assertEqual(manifest['renderer_version'], 9)
                data = json.loads((folder / 'records.json').read_text())
                self.assertEqual(data['schema_version'], 4)
                report = (folder / 'index.html').read_text()
                panel = report.split('id="party-tip"',1)[1].split('id="party-dem"',1)[0]
                self.assertIn('07.11.2017', panel)
                self.assertIn('href="#source-tip-foundation-passage"', panel)
                self.assertIn('id="source-tip-foundation-passage"', panel)
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
                arsiv.record(work, 'version_relation', rel)
                rel.update(id='tip-version-cycle', version_id='tip-registry-v1', previous_version_id='tip-registry-v2')
                with self.assertRaisesRegex(ValueError, 'döngü'): arsiv.record(work, 'version_relation', rel)
            finally: arsiv.DATA = old_data

    def test_official_site_requires_verified_ownership(self):
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
