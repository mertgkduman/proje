"""The tracer must traverse the real archived release, never a fabricated event."""
import json
import hashlib
import copy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import arsiv


def tracer_input(base):
    """Describe the archived source's bounded claim, without treating it as fact."""
    evidence = '0105-cesme-p'
    scope_inventory = [dict(party_id='yeni-parti', topic_id='organ-secim-yontemi', event_id='tracer-cesme', stage='tracer', boundary='Yalnız Çeşme ön seçim kaydı; parti veya konu araştırması tamamlanmış değildir.')]
    inventory_digest = hashlib.sha256(json.dumps(scope_inventory, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    findings = [
        ('tracer-event', 'summary', 'Alaçatı İnternet Gazetesi, üyelerin Çeşme ilçe başkanlığı ön seçiminde oy kullandığını bildirdi.'),
        ('tracer-quote', 'quote', 'Yeni Parti Çeşme İlçe Başkanlığı ön seçiminde 1.113 üyeden 630’ı oy kullandı.'),
        ('tracer-relation', 'summary', 'Bütün üyelerin ilçe başkanını doğrudan seçmesi beyanıyla, haberde anlatılan üye ön oylaması aynı konudadır. Ön seçim nihai kongre seçimi değildir.'),
    ]
    entries = []
    entries.extend([
        {'kind': 'source_attribution', 'values': dict(version_id='0105-cesme-v1', kind='journalism', publisher='Alaçatı İnternet Gazetesi', author=None, social_handle=None, published_at='2026-09-27', date_precision='day', public_url='https://gundemalacati.com/yeni-parti-cesme-de-on-secim-uyeler-av-s-dolunay-onur-u-secti-onur-guven-tazeledi/2902/', basis='Arşivlenmiş haberin künye ve tarih bilgileri.')},
        {'kind': 'source_attribution', 'values': dict(version_id='0105-speech-v1', kind='journalism', publisher='Euronews Türkçe', author='Sait Burak Utucu', social_handle=None, published_at='2026-08-04', date_precision='day', public_url='https://tr.euronews.com/2026/08/04/yeni-partide-yeni-orgutlenme-modeli-genel-baskani-dogrudan-uyeler-sececek', basis='Arşivlenmiş haberin yayıncı, yazar ve tarih bilgileri.')},
    ])
    for fid, provenance, value in findings:
        entries.extend([
            {'kind': 'finding', 'values': dict(id=fid, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id='tracer-event' if fid == 'tracer-quote' else fid, text=value, provenance=provenance, epistemic_type='claim')},
            {'kind': 'finding_evidence', 'values': dict(finding_id=fid, passage_id=evidence, role='support')},
            {'kind': 'verification', 'values': dict(finding_id=fid, passage_id=evidence, checked_at='2026-11-17T19:26:00+00:00', result='confirmed', reason='Haberin aktardığı ön seçim incelendi; yöntem ve nihai kongre sonucu doğrulanmadı.')},
            {'kind': 'review', 'values': dict(id='review-'+fid, kind='finding', subject_id=fid, reviewer_kind='agent', reviewed_at='2026-11-17T19:26:00+00:00', result='reviewed', reason=('Euronews beyanı ve Çeşme ön seçim haberinin anlatısı birlikte okundu; konu bağı niyet veya nihai kongre sonucu göstermez.' if fid == 'tracer-relation' else 'Arşivlenmiş Çeşme haberinin başlığı, olay anlatısı ve Onur sözleri okundu; haberin tespit yöntemi açıklanmıyor ve oy sayıları ile yüzde 86 ifadesi uyuşmuyor. Nihai kongre sonucu bu kaynakla doğrulanmaz.'))},
        ])
    entries.extend([
        {'kind': 'finding', 'values': dict(id='tracer-speech-quote', party_id='yeni-parti', heading='Söylem ve uygulama', pair_id='0105-statement', text='Yeni Parti Genel Başkanı Özgür Özel, partisinin salı günü düzenlenen ilk Türkiye Büyük Millet Meclisi (TBMM) grup toplantısında, ilçe ve il başkanları ile genel başkanın bütün üyeler tarafından doğrudan seçileceğini açıkladı.', provenance='quote', epistemic_type='claim')},
        {'kind': 'finding_evidence', 'values': dict(finding_id='tracer-speech-quote', passage_id='0105-speech-p', role='statement')},
        {'kind': 'verification', 'values': dict(finding_id='tracer-speech-quote', passage_id='0105-speech-p', checked_at='2026-11-17T19:26:00+00:00', result='confirmed', reason='Euronews haberinde beyan aktarılıyor.')},
        {'kind': 'review', 'values': dict(id='review-tracer-speech-quote', kind='finding', subject_id='tracer-speech-quote', reviewer_kind='agent', reviewed_at='2026-11-17T19:26:00+00:00', result='reviewed', reason='Euronews haberinin yazar ve tarih bilgileri ile beyan ve çevresi arşivden okundu; bu kaynak sözü aktarır, gerçekleşme kanıtı değildir.')},
        {'kind': 'finding_evidence', 'values': dict(finding_id='tracer-relation', passage_id='0105-speech-p', role='support')},
        {'kind': 'verification', 'values': dict(finding_id='tracer-relation', passage_id='0105-speech-p', checked_at='2026-11-17T19:26:00+00:00', result='confirmed', reason='Söylem ve olay kaynakları karşılaştırıldı; amaç veya niyet atfedilmedi.')},
    ])
    records = {
        'practice_contract': [dict(version=1, taxonomy_version=4, stage='tracer', method_version=1, inventory_digest=inventory_digest)],
        'practice_event': [dict(id='tracer-cesme', common_event_key='cesme-2026-09-27', event_at='2026-09-27', date_precision='day', date_unknown_reason=None, scope_context='Çeşme ilçe başkanlığı ön seçimi', title='Çeşme ön seçimi', occurrence_basis='Haber, gün, yer ve oy veren üye sayısını bildirir; yöntemi açıklamaz.')],
        'practice_event_evidence': [dict(event_id='tracer-cesme', passage_id=evidence, supported_point='Üyelerin ön seçimde oy kullanması', stage='action', concrete_basis='Haber 27 Eylül, Atatürk Kültür ve Spor Merkezi ve 630 oy kullanan üye bilgisini bildirir.', limitation='Haber tespit yöntemini açıklamıyor; tutanak veya gözlem doğrulanmadı. 630/1113 ile haberin yüzde 86 ifadesi tutarsız.', epistemic_type='claim')],
        'practice_contribution': [dict(id='tracer-contribution', event_id='tracer-cesme', party_id='yeni-parti', actor_id='0105-party-institution', contribution_kind='task', finding_id='tracer-event', authority_passage_id=None, membership_passage_id=None, responsibility_limit='İlçe başkanlığı ön seçimi; nihai kongre sonucu bu kayıtta yok.')],
        'practice_statement': [dict(id='tracer-statement', party_id='yeni-parti', topic_id='organ-secim-yontemi', taxonomy_version=4, summary_finding_id='0105-statement', quote_finding_id='tracer-speech-quote', statement_at='2026-08-04', date_precision='day', version_id='0105-speech-v1', period_basis='4 Ağustos tarihli haber, ön seçimden önceki beyanı aktarır.', uncertainty_reason='Beyanın tam anı kaynakta ayrıntılı belirtilmez.', comparison_row_id='04-03-v3-0303-epm-detail2-organ-secim-yontemi-ilce-yonetim-kurulu-secimi-row')],
        'practice_relation': [dict(id='tracer-relation-id', statement_id='tracer-statement', event_id='tracer-cesme', party_id='yeni-parti', topic_id='organ-secim-yontemi', scope_id=None, comparability_reason='İkisi yerel örgütte seçim usulüyle ilgilidir; seçim aşamaları farklıdır.', target_finding_id='0105-statement', result_finding_id=None, explanation_finding_id='tracer-relation', temporal_context='Beyan 4 Ağustos haberinde, ön seçim 27 Eylül haberinde aktarılır.', authority_context='İlçe başkanlığı ön seçimi ile kongrenin yetkisi ayrıdır; bağlantılı tüzük satırı ilçe yönetim kurulu seçimini düzenler.', uncertainty_reason='Kaynağın tespit yöntemi ve nihai sonuç doğrulanmadı.')],
        'practice_legacy_link': [dict(legacy_kind='action', legacy_id='0105-action-cesme', event_id='tracer-cesme', relation_id='tracer-relation-id', overlap_reason='Aynı arşivlenmiş Çeşme ön seçimi.'), dict(legacy_kind='match', legacy_id='0105-match-cesme', event_id='tracer-cesme', relation_id='tracer-relation-id', overlap_reason='Aynı ön seçim; eski kayıt korunur.')],
        'practice_source_party': [dict(version_id='0105-cesme-v1', party_id='yeni-parti', passage_id=evidence, scope_reason='Haber Yeni Parti Çeşme ön seçimini anlatır.')],
    }
    return dict(contract_version=1, base_release=base, party_id='yeni-parti', taxonomy_version=4,
                stage='tracer', entries=entries, practice_records=records, scope_inventory=scope_inventory,
                tranches=[], source_review_refs=[])


class PracticeTracer(unittest.TestCase):
    def test_cross_party_evidence_requires_explicit_practice_scope(self):
        db = arsiv.sqlite3.connect(':memory:')
        db.row_factory = arsiv.sqlite3.Row
        try:
            db.executescript('''
                CREATE TABLE document(id TEXT, party_id TEXT, source_kind TEXT);
                CREATE TABLE document_version(id TEXT, document_id TEXT);
                CREATE TABLE passage(id TEXT, version_id TEXT, exact TEXT);
                CREATE TABLE practice_source_party(version_id TEXT, party_id TEXT, passage_id TEXT, scope_reason TEXT);
                CREATE TABLE practice_contribution(finding_id TEXT);
                CREATE TABLE practice_statement(summary_finding_id TEXT, quote_finding_id TEXT);
                CREATE TABLE practice_relation(target_finding_id TEXT, result_finding_id TEXT, explanation_finding_id TEXT);
                INSERT INTO document VALUES ('doc','tip','news');
                INSERT INTO document_version VALUES ('version','doc');
                INSERT INTO passage VALUES ('passage','version','Kaynak metni');
            ''')
            finding = dict(id='finding', party_id='dem', provenance='summary', heading='Söylem ve uygulama', epistemic_type='claim')
            passage = dict(id='passage', exact='Kaynak metni')
            with self.assertRaises(ValueError):
                arsiv.validate_evidence(db, finding, passage)
            db.execute("INSERT INTO practice_source_party VALUES ('version','dem','passage','İki partiyi açıkça kapsayan kaynak')")
            with self.assertRaises(ValueError):
                arsiv.validate_evidence(db, finding, passage)
            db.execute("INSERT INTO practice_contribution VALUES ('finding')")
            arsiv.validate_evidence(db, finding, passage)
        finally:
            db.close()

    def test_renderer_24_reproduces_archived_bytes(self):
        folder = arsiv.DATA / 'releases' / arsiv.current()
        manifest = json.loads((folder / 'manifest.json').read_text(encoding='utf-8'))
        if manifest['renderer_version'] != 24:
            folder = arsiv.DATA / 'releases' / '9003e475ee5d49b29a1310c0bfe2007d'
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        actual = arsiv.render_comparison_snapshot(data, arsiv.render_v24_report).encode('utf-8')
        self.assertEqual(actual, (folder / 'index.html').read_bytes())

    def test_historical_taxonomies_do_not_duplicate_practice_cards(self):
        folder = arsiv.DATA / 'releases' / '53b24e6740104cb5be5d3419491bd735'
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        versions = {row['taxonomy_version'] for row in data['comparison_topic']
                    if row['topic_id'] == 'organ-secim-yontemi'}
        self.assertGreaterEqual(len(versions), 3)
        report = arsiv.render_report(data)
        for view in ('party', 'comparison'):
            self.assertEqual(report.count(f'id="{view}-practice-tracer-relation-id"'), 1)

    def test_renderer_25_reproduces_archived_bytes(self):
        folder = arsiv.DATA / 'releases' / '53b24e6740104cb5be5d3419491bd735'
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        from rapor_v25 import render_report
        actual = arsiv.render_comparison_snapshot(data, render_report).encode('utf-8')
        self.assertEqual(actual, (folder / 'index.html').read_bytes())

    def test_real_archived_event_reaches_both_views(self):
        base = '9003e475ee5d49b29a1310c0bfe2007d'
        folder = arsiv.DATA / 'releases' / base
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        action = next(x for x in data['action'] if x['finding_id'] == '0105-action-cesme')
        passage = next(x for x in data['passage'] if x['id'] == action['occurrence_passage_id'])
        self.assertEqual(passage['id'], '0105-cesme-p')
        self.assertEqual(action['event_date'], '2026-09-27')
        self.assertIn('ön seçim', passage['exact'])

        # The public command must expose the new validator before a workspace can
        # be loaded; a parser rejection is a failing assertion, not RED by crash.
        result = subprocess.run([sys.executable, str(arsiv.ROOT / 'src/arsiv.py'),
                                 'practice-check', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('--input', result.stdout)
        self.assertIn('--base-release', result.stdout)
        self.assertIn('--inventory', result.stdout)

        # The rest of this test exercises the real package through the write,
        # export and render path once the production adapter exists.
        from uygulamalar import load_practice, validate_practice_input
        package = tracer_input(base)
        with tempfile.TemporaryDirectory() as tmp:
            # Full release-chain audits run as separate plan gates. Avoid
            # repeating that expensive audit on each temporary workspace.
            with patch.object(arsiv, 'audit_release', return_value=base), patch.object(arsiv, 'current', return_value=base):
                work = arsiv.open_workspace(tmp)
            try:
                initial = arsiv.sha(work / 'records.sqlite3')
                bad = copy.deepcopy(package)
                bad['practice_records']['practice_event_evidence'][0]['passage_id'] = 'missing-passage'
                with self.assertRaises((ValueError, arsiv.sqlite3.IntegrityError)):
                    load_practice(work, bad)
                self.assertEqual(initial, arsiv.sha(work / 'records.sqlite3'))
                bad = copy.deepcopy(package)
                bad['practice_records']['practice_contribution'][0]['party_id'] = 'tip'
                with self.assertRaises((ValueError, arsiv.sqlite3.IntegrityError)):
                    load_practice(work, bad)
                self.assertEqual(initial, arsiv.sha(work / 'records.sqlite3'))
                bad = copy.deepcopy(package)
                bad['entries'] = [entry for entry in bad['entries'] if entry['kind'] != 'review']
                with self.assertRaisesRegex(ValueError, 'kaynak incelemesi eksik'):
                    load_practice(work, bad)
                self.assertEqual(initial, arsiv.sha(work / 'records.sqlite3'))
                validate_practice_input(package, base_release=base)
                load_practice(work, package)
                output = arsiv.export_db(work / 'records.sqlite3', 'practice-test')
                self.assertEqual(output['schema_version'], 7)
                self.assertEqual(output['practice_contract'][0]['stage'], 'tracer')
                self.assertIsNone(output['practice_relation'][0]['result_finding_id'])
                self.assertEqual(output['practice_event_evidence'][0]['epistemic_type'], 'claim')
                html = arsiv.render_comparison_snapshot(output, arsiv.render_report)
                self.assertIn('party-practice-', html)
                self.assertIn('comparison-practice-', html)
                self.assertIn('0105-cesme-p', html)
                self.assertIn('nihai kongre', html.lower())
                self.assertIn('Euronews Türkçe', html)
                self.assertIn('Alaçatı İnternet Gazetesi', html)
                self.assertIn('Sait Burak Utucu', html)
                self.assertNotIn('yüzde 86 katılım gerçekleşti', html.lower())
                hostile = dict(output)
                hostile['practice_event'] = [dict(row, title='<script>alert(1)</script>') for row in output['practice_event']]
                escaped = arsiv.render_comparison_snapshot(hostile, arsiv.render_report)
                self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', escaped)
                self.assertNotIn('<script>alert(1)</script>', escaped)
            finally:
                arsiv.assert_lock(work)
                (arsiv.DATA / '.write.lock').unlink()


if __name__ == '__main__':
    unittest.main()
