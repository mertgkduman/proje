"""Atıflı kaynakların gerçek kayıt → export → yayın → audit sözleşmesi."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import arsiv
import dosyalar


BASE = 'b14c96c54e4b420686c46e5cfb1071a3'


class SourcePolicy(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.old = arsiv.DATA
        arsiv.DATA = Path(self.tmp.name) / 'data'
        shutil.copytree(self.old, arsiv.DATA, ignore=shutil.ignore_patterns('.write.lock', '.staging'))
        (arsiv.DATA / 'current.json').write_text(json.dumps({'release_id': BASE}))
        self.work = arsiv.open_workspace(self.tmp.name)

    def tearDown(self):
        arsiv.DATA = self.old
        self.tmp.cleanup()

    def charter(self):
        db = arsiv.connect(self.work / 'records.sqlite3')
        v = dict(db.execute("SELECT * FROM document_version WHERE sha256 LIKE 'b3709f%' LIMIT 1").fetchone())
        db.close()
        v.update(id='policy-charter-v1', document_id='policy-charter')
        arsiv.record(self.work, 'document', dict(id='policy-charter', party_id='yeni-parti', title='Yeni Parti — Parti Tüzüğü', source_kind='party'))
        arsiv.record(self.work, 'document_version', v)
        arsiv.record(self.work, 'passage', dict(id='policy-charter-p', version_id=v['id'], exact='Yeni Parti, Türkiye’nin demokrasi ittifakını kuran ve temsil eden çağdaş sosyal demokrat bir partidir.', article='Madde 2'))
        arsiv.record(self.work, 'finding', dict(id='policy-charter-f', party_id='yeni-parti', heading='Tüzük', pair_id='policy-charter', text='Yeni Parti tüzüğünde kendisini çağdaş sosyal demokrat bir parti olarak tanımlar.', provenance='summary', epistemic_type='claim'))
        arsiv.record(self.work, 'finding_evidence', dict(finding_id='policy-charter-f', passage_id='policy-charter-p', role='support'))
        arsiv.record(self.work, 'review', dict(id='policy-review', kind='finding', subject_id='policy-charter-f', reviewer_kind='agent', reviewed_at=v['verified_at'], result='reviewed', reason='Pasaj özgün kaynakta karşılaştırıldı; beyanın doğruluğu hakkında karar verilmedi.'))
        return v

    def attribution(self, version, **changes):
        value = dict(version_id=version['id'], kind='party_publication', publisher='Yeni Parti', author=None, social_handle=None, published_at=None, date_precision='unknown', public_url=version['final_url'], basis='Parti adı ve tüzük başlığı özgün arşiv sayfasında; resmî site kullanıcının 11.11.2026 kararıyla belirtildi.')
        value.update(changes)
        return value

    def test_party_charter_passes_real_publication_without_registry_domain_authority(self):
        v = self.charter()
        try:
            arsiv.record(self.work, 'source_attribution', self.attribution(v))
            exported = arsiv.export_db(self.work / 'records.sqlite3', 'workspace', strict_identity=True)
            self.assertEqual(exported['schema_version'], 5)
            release = arsiv.publish_release(self.work, party='tip', stage='tracer')
            self.assertEqual(arsiv.audit_release(release), release)
        except ValueError as exc:
            self.fail('Atıflı parti tüzüğü sicil alan adı/otorite kapısı olmadan yayımlanmalı: ' + str(exc))
        manifest = json.loads((arsiv.DATA / 'releases' / release / 'manifest.json').read_text())
        self.assertEqual(manifest['source_policy_version'], 2)
        self.assertEqual(manifest['phase2_delivery'], dict(party_id='tip', stage='tracer', completed_prefix=[]))
        self.assertIn('Yeni Parti', (arsiv.DATA / 'releases' / release / 'index.html').read_text())

    def test_social_requires_account_date_and_permalink_and_claim_stays_claim(self):
        self.assertIn('source_attribution', arsiv.TABLES, 'Sürümlü atıf sözleşmesi eksik')
        v = self.charter()
        for changes in (dict(kind='social_publication'), dict(public_url='javascript:alert(1)'), dict(published_at='2026-11-01', date_precision='unknown')):
            with self.assertRaises(ValueError):
                arsiv.record(self.work, 'source_attribution', self.attribution(v, **changes))
        db = arsiv.connect(self.work / 'records.sqlite3')
        db.execute("UPDATE document SET source_kind='social' WHERE id='policy-charter'")
        db.commit(); db.close()
        valid = self.attribution(v, kind='social_publication', author='Bir kullanıcı', social_handle='@hesap', published_at='2026-11-01', date_precision='day')
        arsiv.record(self.work, 'source_attribution', valid)
        from kaynaklar import attribution_text
        self.assertIn('Sosyal medya kullanıcısı @hesap bunu 2026-11-01 paylaştı.', attribution_text(valid))
        data = arsiv.export_db(self.work / 'records.sqlite3', 'workspace')
        self.assertEqual(next(f for f in data['finding'] if f['id']=='policy-charter-f')['epistemic_type'], 'claim')

    def test_missing_attribution_and_cross_party_evidence_fail_export(self):
        self.assertIn('source_attribution', arsiv.TABLES, 'Atıf kontrolü eksik')
        v = self.charter()
        with self.assertRaisesRegex(ValueError, 'atıf|Atıf'):
            arsiv.export_db(self.work / 'records.sqlite3', 'workspace')
        arsiv.record(self.work, 'source_attribution', self.attribution(v))
        db = arsiv.connect(self.work / 'records.sqlite3')
        db.execute("UPDATE finding SET party_id='tip' WHERE id='policy-charter-f'")
        db.commit(); db.close()
        with self.assertRaises(ValueError):
            arsiv.export_db(self.work / 'records.sqlite3', 'workspace')

    def test_historical_renderer_and_policy_still_audit(self):
        self.assertEqual(arsiv.audit_release(BASE), BASE)

    def test_journalism_allows_unknown_author_date_but_requires_attributed_claim(self):
        v = self.charter()
        db = arsiv.connect(self.work / 'records.sqlite3')
        db.execute("UPDATE document SET source_kind='news' WHERE id='policy-charter'")
        db.commit(); db.close()
        arsiv.record(self.work, 'source_attribution', self.attribution(v, kind='journalism', publisher='Haber yayını'))
        data = arsiv.export_db(self.work / 'records.sqlite3', 'workspace')
        self.assertIsNone(data['source_attribution'][0]['author'])
        db = arsiv.connect(self.work / 'records.sqlite3')
        db.execute("UPDATE finding SET epistemic_type='fact' WHERE id='policy-charter-f'")
        db.commit(); db.close()
        with self.assertRaisesRegex(ValueError, 'atıflı'):
            arsiv.export_db(self.work / 'records.sqlite3', 'workspace')

    def test_policy_cannot_be_removed_or_exemptions_widened(self):
        from kaynaklar import validate_policy_descent
        base = arsiv.export_db(self.work / 'records.sqlite3', 'workspace')
        for change in ('remove','widen'):
            candidate = copy.deepcopy(base)
            if change == 'remove': candidate['source_policy']=[]
            else: candidate['source_policy'][0]['legacy_findings']='["invented"]'
            with self.assertRaises(ValueError): validate_policy_descent(base,candidate)

    def test_removing_policy_cannot_bypass_real_publish(self):
        db=arsiv.connect(self.work/'records.sqlite3')
        db.execute('DELETE FROM source_policy');db.commit();db.close()
        with self.assertRaises(ValueError):arsiv.publish_release(self.work,party='tip',stage='tracer')
        self.assertEqual(arsiv.current(),BASE)

    def test_official_site_needs_party_publication_evidence_for_same_host(self):
        from kaynaklar import official_site_supported
        v = self.charter()
        arsiv.record(self.work, 'source_attribution', self.attribution(v))
        data = arsiv.export_db(self.work / 'records.sqlite3', 'workspace')
        field = dict(value='https://yenipartiyiz.biz',finding_id='policy-charter-f')
        self.assertTrue(official_site_supported(data,field,data['finding_evidence']))
        self.assertFalse(official_site_supported(data,dict(field,value='https://unsupported.example'),data['finding_evidence']))

