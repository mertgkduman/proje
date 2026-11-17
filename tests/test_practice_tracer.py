"""The tracer must traverse the real archived release, never a fabricated event."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import arsiv


def tracer_input(base):
    """Describe the archived source's bounded claim, without treating it as fact."""
    evidence = '0105-cesme-p'
    findings = [
        ('tracer-event', 'summary', 'Alaçatı İnternet Gazetesi, üyelerin Çeşme ilçe başkanlığı ön seçiminde oy kullandığını bildirdi.'),
        ('tracer-quote', 'quote', 'Yeni Parti Çeşme İlçe Başkanlığı ön seçiminde 1.113 üyeden 630’ı oy kullandı.'),
        ('tracer-relation', 'summary', 'Tüzükte ilçe yönetim kurulunun kongrede seçimi düzenlenir; haberde ilçe başkanlığı için üye ön seçimi anlatılır. Ön seçim nihai kongre seçimi değildir.'),
    ]
    entries = []
    for fid, provenance, value in findings:
        entries.extend([
            {'kind': 'finding', 'values': dict(id=fid, party_id='yeni-parti', heading='Söylem ve uygulama', pair_id=fid, text=value, provenance=provenance, epistemic_type='claim')},
            {'kind': 'finding_evidence', 'values': dict(finding_id=fid, passage_id=evidence, role='support')},
            {'kind': 'verification', 'values': dict(finding_id=fid, passage_id=evidence, checked_at='2026-11-17T17:00:00+00:00', result='confirmed', reason='Haberin aktardığı ön seçim incelendi; yöntem ve nihai kongre sonucu doğrulanmadı.')},
        ])
    entries.extend([
        {'kind': 'finding', 'values': dict(id='tracer-speech-quote', party_id='yeni-parti', heading='Söylem ve uygulama', pair_id='tracer-speech-quote', text='Yeni Parti Genel Başkanı Özgür Özel, partisinin salı günü düzenlenen ilk Türkiye Büyük Millet Meclisi (TBMM) grup toplantısında, ilçe ve il başkanları ile genel başkanın bütün üyeler tarafından doğrudan seçileceğini açıkladı.', provenance='quote', epistemic_type='claim')},
        {'kind': 'finding_evidence', 'values': dict(finding_id='tracer-speech-quote', passage_id='0105-speech-p', role='statement')},
        {'kind': 'verification', 'values': dict(finding_id='tracer-speech-quote', passage_id='0105-speech-p', checked_at='2026-11-17T17:00:00+00:00', result='confirmed', reason='Euronews haberinde beyan aktarılıyor.')},
    ])
    records = {
        'practice_contract': [dict(version=1, taxonomy_version=4, stage='tracer', method_version=1, inventory_digest='tracer-cesme-only')],
        'practice_event': [dict(id='tracer-cesme', common_event_key='cesme-2026-09-27', event_at='2026-09-27', date_precision='day', date_unknown_reason=None, scope_context='Çeşme ilçe başkanlığı ön seçimi', title='Çeşme ön seçimi', occurrence_basis='Haber, gün, yer ve oy veren üye sayısını bildirir; yöntemi açıklamaz.')],
        'practice_event_evidence': [dict(event_id='tracer-cesme', passage_id=evidence, supported_point='Üyelerin ön seçimde oy kullanması', stage='action', concrete_basis='Haber 27 Eylül, Atatürk Kültür ve Spor Merkezi ve 630 oy kullanan üye bilgisini bildirir.', limitation='Haber tespit yöntemini açıklamıyor; tutanak veya gözlem doğrulanmadı. 630/1113 ile haberin yüzde 86 ifadesi tutarsız.', epistemic_type='claim')],
        'practice_contribution': [dict(id='tracer-contribution', event_id='tracer-cesme', party_id='yeni-parti', actor_id='0105-party-institution', contribution_kind='task', finding_id='tracer-event', authority_passage_id=None, membership_passage_id=None, responsibility_limit='İlçe başkanlığı ön seçimi; nihai kongre sonucu bu kayıtta yok.')],
        'practice_statement': [dict(id='tracer-statement', party_id='yeni-parti', topic_id='organ-secim-yontemi', taxonomy_version=4, summary_finding_id='0105-statement', quote_finding_id='tracer-speech-quote', statement_at='2026-08-04', date_precision='day', version_id='0105-speech-v1', period_basis='4 Ağustos tarihli haber, ön seçimden önceki beyanı aktarır.', uncertainty_reason='Beyanın tam anı kaynakta ayrıntılı belirtilmez.', comparison_row_id='04-03-v3-0303-epm-detail2-organ-secim-yontemi-ilce-yonetim-kurulu-secimi-row')],
        'practice_relation': [dict(id='tracer-relation-id', statement_id='tracer-statement', event_id='tracer-cesme', party_id='yeni-parti', topic_id='organ-secim-yontemi', scope_id=None, comparability_reason='İkisi yerel örgütte seçim usulüyle ilgilidir; seçim aşamaları farklıdır.', target_finding_id='0105-statement', result_finding_id='tracer-event', explanation_finding_id='tracer-relation', temporal_context='Beyan 4 Ağustos haberinde, ön seçim 27 Eylül haberinde aktarılır.', authority_context='Üyelerin ön seçimi ile kongrenin yetkisi ayrıdır.', uncertainty_reason='Kaynağın tespit yöntemi ve nihai sonuç doğrulanmadı.')],
        'practice_legacy_link': [dict(legacy_kind='action', legacy_id='0105-action-cesme', event_id='tracer-cesme', relation_id='tracer-relation-id', overlap_reason='Aynı arşivlenmiş Çeşme ön seçimi.'), dict(legacy_kind='match', legacy_id='0105-match-cesme', event_id='tracer-cesme', relation_id='tracer-relation-id', overlap_reason='Aynı ön seçim; eski kayıt korunur.')],
        'practice_source_party': [dict(version_id='0105-cesme-v1', party_id='yeni-parti', passage_id=evidence, scope_reason='Haber Yeni Parti Çeşme ön seçimini anlatır.')],
    }
    return dict(contract_version=1, base_release=base, party_id='yeni-parti', taxonomy_version=4,
                stage='tracer', entries=entries, practice_records=records, scope_inventory=[],
                tranches=[], source_review_refs=[])


class PracticeTracer(unittest.TestCase):
    def test_real_archived_event_reaches_both_views(self):
        base = arsiv.current()
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

        # The rest of this test exercises the real package through the write,
        # export and render path once the production adapter exists.
        from uygulamalar import load_practice, validate_practice_input
        package = tracer_input(base)
        with tempfile.TemporaryDirectory() as tmp:
            work = arsiv.open_workspace(tmp)
            try:
                validate_practice_input(package, base_release=base)
                load_practice(work, package)
                output = arsiv.export_db(work / 'records.sqlite3', 'practice-test')
                self.assertEqual(output['schema_version'], 7)
                self.assertEqual(output['practice_contract'][0]['stage'], 'tracer')
                html = arsiv.render_comparison_snapshot(output, arsiv.render_report)
                self.assertIn('party-practice-', html)
                self.assertIn('comparison-practice-', html)
                self.assertIn('0105-cesme-p', html)
                self.assertIn('nihai kongre', html.lower())
                self.assertNotIn('yüzde 86 katılım gerçekleşti', html.lower())
            finally:
                (arsiv.DATA / '.write.lock').unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
