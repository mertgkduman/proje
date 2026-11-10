import json
import re
import shutil
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

import arsiv
from rapor import render_report


class MatchContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = arsiv.DATA
        arsiv.DATA = Path(self.tmp.name) / 'data'
        shutil.copytree(self.old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock'))
        self.work = arsiv.open_workspace(self.tmp.name)
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        # Purpose-made fixtures: neither source is asserted to be a real event.
        for doc, kind, date, content in [('statement', 'news', '2026-08-04', 'Yöneticileri üyeler seçecek.'), ('occurrence', 'news', '2026-10-19', 'Üyeler il ön seçiminde oy kullandı.'), ('authority', 'official', '2026-08-01', 'Ayşe Örnek parti temsilcisi olarak yetkilendirildi.')]:
            obj = arsiv.DATA / 'objects' / ('fixture-' + doc)
            obj.mkdir(); original = obj / 'original.html.bin'; original.write_text(content)
            (obj / 'readable.html').write_bytes(arsiv.readable_bytes(original.read_bytes(), 'html'))
            self.db.execute('INSERT INTO document VALUES (?,?,?,?)', (doc, 'yeni-parti', doc, kind))
            self.db.execute('INSERT INTO document_version (id,document_id,original_url,final_url,document_date,accessed_at,verified_at,mime,sha256,original_path,readable_path,date_precision) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', (doc, doc, 'https://example.org/'+doc, 'https://example.org/'+doc, date, '2026-11-10T15:00:00+00:00', '2026-11-10T15:00:00+00:00', 'text/html', arsiv.sha(original), str(original.relative_to(arsiv.DATA)), str((obj/'readable.html').relative_to(arsiv.DATA)), 'day'))
            self.db.execute('INSERT INTO passage (id,version_id,exact) VALUES (?,?,?)', (doc, doc, content))
        self.db.execute("INSERT INTO person VALUES ('person-test','Ayşe Örnek')")
        self.db.execute("INSERT INTO actor VALUES ('actor-test','institution','yeni-parti',NULL,NULL)")
        for fid, text, kind, pid, role in [('statement-test','Yöneticileri üyeler seçecek.','claim','statement','statement'),('action-test','Üyeler il ön seçiminde oy kullandı.','fact','occurrence','occurrence')]:
            self.db.execute('INSERT INTO finding VALUES (?,?,?,?,?,?,?)', (fid,'yeni-parti','Söylem ve uygulama',fid,text,'summary',kind))
            self.db.execute('INSERT INTO finding_evidence VALUES (?,?,?)', (fid,pid,role))
            self.db.execute('INSERT INTO verification VALUES (?,?,?,?,?)', (fid,pid,'2026-11-10T15:00:00+00:00','confirmed','Test pasajı, olay ve konunun elle kontrolünü temsil eder.'))
            self.db.execute('INSERT INTO finding_topic VALUES (?,?,?)', (fid,'organ-secimi',1))
        self.db.execute("INSERT INTO action VALUES ('action-test','actor-test','2026-10-18','day','occurrence','İl ön seçimi; nihai kongre seçimi değil')")
        self.db.commit()
        self.match = dict(id='m1',topic_id='organ-secimi',statement_finding_id='statement-test',action_finding_id='action-test',relation='benzerlik',rationale='Üye oylaması var; nihai seçim hakkında sonuç yok.',eligibility='eligible',exclusion_reason=None,reviewed_at='2026-11-10T15:00:00+00:00')

    def tearDown(self):
        self.db.close()
        arsiv.DATA = self.old
        self.tmp.cleanup()

    def rejected(self, sql, parameters=()):
        self.db.execute('SAVEPOINT mutation')
        self.db.execute(sql, parameters)
        with self.assertRaises(ValueError): arsiv.check_match(self.db, self.match)
        self.db.execute('ROLLBACK TO mutation')
        self.db.execute('RELEASE mutation')

    def test_separate_reviewed_evidence_event_party_and_topic(self):
        arsiv.check_match(self.db, self.match)
        self.rejected("DELETE FROM finding_evidence WHERE finding_id='statement-test'")
        self.rejected("UPDATE action SET occurrence_passage_id='statement'")
        self.rejected("DELETE FROM verification WHERE finding_id='action-test'")
        self.rejected("UPDATE document SET source_kind='party' WHERE id='occurrence'")
        self.rejected("UPDATE document SET party_id='tip' WHERE id='occurrence'")
        self.rejected("UPDATE document_version SET document_date='2026-08-01' WHERE id='occurrence'")
        self.rejected("UPDATE action SET event_date='2026-11-11'")
        self.rejected("DELETE FROM finding_topic WHERE finding_id='action-test'")
        self.rejected("UPDATE finding SET party_id='tip' WHERE id='statement-test'")
        with self.assertRaises(ValueError): arsiv.check_match(self.db, dict(self.match, reviewed_at='2026-11-10'))

    def test_actor_authorization_and_individual_are_distinct(self):
        self.rejected("UPDATE actor SET kind='individual_mp', person_id='person-test' WHERE id='actor-test'")
        self.rejected("UPDATE actor SET kind='authorized_representative', person_id='person-test' WHERE id='actor-test'")
        self.db.execute("UPDATE actor SET kind='authorized_representative', person_id='person-test', authorization_passage_id='authority' WHERE id='actor-test'")
        arsiv.check_match(self.db, self.match)
        self.rejected("UPDATE actor SET authorization_passage_id='occurrence' WHERE id='actor-test'")

    def test_all_eligible_ids_reach_db_json_and_html(self):
        self.db.commit(); self.db.close()
        for name in ('m1', 'm2', 'm3'):
            arsiv.record_match(self.work, dict(self.match, id=name))
            arsiv.record(self.work, 'match_candidate', dict(id='candidate-'+name,party_id='yeni-parti',topic_id='organ-secimi',passage_id='statement',status='eligible',match_id=name,rationale='Test',reviewed_at='2026-11-10T15:00:00+00:00'))
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        ids = {r[0] for r in self.db.execute("SELECT id FROM match WHERE eligibility='eligible'")}
        payload = arsiv.export_db(self.work / 'records.sqlite3', 'fixture')
        exported = {m['id'] for m in json.loads(json.dumps(payload))['match'] if m['eligibility']=='eligible'}
        html = render_report(payload)
        rendered = set(re.findall(r'id="match-(m[123])"', html))
        self.assertTrue({'m1','m2','m3'} <= ids)
        self.assertEqual(ids, exported)
        self.assertEqual({'m1','m2','m3'}, rendered)

    def test_match_respects_each_findings_provenance(self):
        self.db.execute("UPDATE finding SET provenance='quote' WHERE id='statement-test'")
        self.db.commit(); self.db.close()
        arsiv.record_match(self.work, self.match)
        arsiv.record(self.work, 'match_candidate', dict(id='candidate-test-render',party_id='yeni-parti',topic_id='organ-secimi',passage_id='statement',status='eligible',match_id='m1',rationale='Test',reviewed_at='2026-11-10T15:00:00+00:00'))
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        payload = arsiv.export_db(self.work / 'records.sqlite3', 'fixture')
        page = render_report(payload)
        article = page.split('id="match-m1"', 1)[1].split('</article>', 1)[0]
        self.assertIn('<p class="quote">“Yöneticileri üyeler seçecek.”', article)
        self.assertIn('<p class="summary">Üyeler il ön seçiminde oy kullandı.', article)

    def test_invalid_input_is_rejected(self):
        with self.assertRaises(ValueError): arsiv.record_match(self.work, {})
        with self.assertRaises(ValueError): arsiv.check_match(self.db, dict(self.match, eligibility='excluded', exclusion_reason=None))

    def test_candidate_resolution_preserves_history_and_rejects_wrong_evidence(self):
        self.db.commit(); self.db.close()
        arsiv.record_attempt(self.work, dict(id='test-attempt',party_id='yeni-parti',heading='Söylem ve uygulama',topic_id='organ-secimi',type='verification',query='Ön seçim',attempted_at='2026-11-10T14:00:00+00:00',result='inconclusive',reason='Oluş kanıtı bekleniyor.'))
        arsiv.record_missing(self.work, dict(id='test-missing',party_id='yeni-parti',heading='Söylem ve uygulama',topic_id='organ-secimi',status='Doğrulanamadı',attempt_id='test-attempt',reason='Oluş kanıtı bekleniyor.'))
        arsiv.record(self.work, 'match_candidate', dict(id='test-candidate',party_id='yeni-parti',topic_id='organ-secimi',passage_id='statement',status='unverified',missing_id='test-missing',rationale='Kanıt bekleniyor',reviewed_at='2026-11-10T15:00:00+00:00'))
        arsiv.record_match(self.work, dict(self.match,id='resolved-match'))
        resolution=dict(missing_id='test-missing',resolved_at='2026-11-10T16:00:00+00:00',passage_id='occurrence',reason='Olay pasajı incelendi.')
        import sys
        import io
        args=['arsiv.py','resolve-candidate','--workspace',str(self.work),'--candidate','test-candidate','--match','resolved-match']
        with patch.object(sys, 'argv', args), patch.object(sys, 'stdin', io.StringIO(json.dumps(dict(resolution,passage_id='authority')))), self.assertRaises(ValueError): arsiv.main()
        with self.assertRaises(ValueError): arsiv.resolve_candidate(self.work,'test-candidate','resolved-match',dict(resolution,resolved_at='2026-11-09T16:00:00+00:00'))
        with patch.object(sys, 'argv', args), patch.object(sys, 'stdin', io.StringIO(json.dumps(resolution))): arsiv.main()
        self.db = arsiv.connect(self.work / 'records.sqlite3')
        self.assertEqual(self.db.execute("SELECT status FROM match_candidate WHERE id='test-candidate'").fetchone()[0], 'eligible')
        self.assertEqual(self.db.execute("SELECT count(*) FROM missing WHERE id='test-missing'").fetchone()[0], 1)
        payload=arsiv.export_db(self.work/'records.sqlite3','fixture')
        page=render_report(payload)
        self.assertIn('Çözümlenen geçmiş eksikler', page)
        self.assertIn('test-missing', page)
        self.assertEqual(sum(r['missing_id']=='test-missing' for r in payload['missing_resolution']),1)


class PublishedMatches(unittest.TestCase):
    def test_current_release_preserves_every_eligible_id(self):
        release = arsiv.current()
        folder = arsiv.DATA / 'releases' / release
        db = arsiv.connect(folder / 'records.sqlite3')
        try:
            if not db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='match'").fetchone():
                self.fail('Güncel sürümde eşleşme tablosu bulunmuyor')
            eligible = {r[0] for r in db.execute("SELECT id FROM match WHERE eligibility='eligible'")}
            candidate_ids = {r[0] for r in db.execute('SELECT id FROM match_candidate')}
        finally:
            db.close()
        data = json.loads((folder / 'records.json').read_text())
        exported = {m['id'] for m in data['match'] if m['eligibility'] == 'eligible'}
        html = (folder / 'index.html').read_text()
        rendered = set(re.findall(r'id="match-([^"]+)"', html))
        self.assertEqual(eligible, exported)
        self.assertEqual(eligible, rendered)
        candidates = {c['match_id'] for c in data['match_candidate'] if c['status']=='eligible'}
        html_candidates = set(re.findall(r'id="candidate-ledger-([^"]+)" data-status="eligible"',html))
        self.assertEqual(eligible,candidates)
        self.assertEqual({c['id'] for c in data['match_candidate'] if c['status']=='eligible'},html_candidates)
        self.assertEqual(candidate_ids,{c['id'] for c in data['match_candidate']})
        self.assertEqual(candidate_ids,set(re.findall(r'id="candidate-ledger-([^"]+)"',html)))
        self.assertTrue(eligible, 'Gerçek veri örneğinde uygun kimlikler bekleniyor')
