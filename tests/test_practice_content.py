"""Regression checks for the open practice timeline."""
import json
import hashlib
import shutil
import tempfile
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path

from test_practice_tracer import tracer_input
from uygulamalar import _load_practice_copy, validate_practice_descent, validate_practices

import arsiv


class PracticeContent(unittest.TestCase):
    def test_unmatched_statement_search_survives_load_export_and_views(self):
        base = '9003e475ee5d49b29a1310c0bfe2007d'
        package = tracer_input(base)
        records = package['practice_records']
        records['practice_scope'] = [dict(id='speech-scope', party_id='yeni-parti', topic_id='organ-secim-yontemi', taxonomy_version=4, period_start='2026-07-24', cutoff_at='2026-11-10T14:38:46.154751+00:00', research_kind='statement', state='not_researched', boundary_reason='Bu kapsam henüz taranmadı.')]
        records['practice_scope'].append(dict(id='attempted-scope', party_id='demokrat', topic_id='temel-yurttaslik-geliri', taxonomy_version=4, period_start='1983-06-23', cutoff_at='2026-11-10T14:38:46.154751+00:00', research_kind='statement', state='open', boundary_reason='Teknik kapsam örneği.'))
        for scope in records['practice_scope']:
            package['scope_inventory'].append(dict(scope_id=scope['id'], **{k: scope[k] for k in ('party_id', 'topic_id', 'taxonomy_version', 'period_start', 'cutoff_at', 'research_kind')}))
        inventory_json = json.dumps(package['scope_inventory'], sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        records['practice_contract'][0]['inventory_digest'] = hashlib.sha256(inventory_json.encode()).hexdigest()
        records['practice_variant_contract'] = [dict(version=1, inventory_json=inventory_json)]
        base_data = json.loads((arsiv.DATA / 'releases' / base / 'records.json').read_text(encoding='utf-8'))
        existing_attempt = next(a for a in base_data['attempt'] if a['id'] == '0314-dyp-1985-income-page-check')
        records['practice_attempt'] = [dict(scope_id='attempted-scope', url=None, **{k: existing_attempt[k] for k in ('id', 'attempted_at', 'query', 'result', 'reason', 'source_version_id')})]
        records['practice_event'].append(dict(records['practice_event'][0], id='unmatched-event', title='Teknik söylemsiz olay'))
        records['practice_event_evidence'].append(dict(records['practice_event_evidence'][0], event_id='unmatched-event'))
        records['practice_unmatched'] = [dict(id='unmatched-1', event_id='unmatched-event', party_id='yeni-parti', topic_id='organ-secim-yontemi', statement_scope_id='speech-scope', statement_search_state='not_researched', reason='Söylem taranmadı.')]
        records['practice_unmatched'].append(dict(id='unmatched-missing', event_id='unmatched-event', party_id='demokrat', topic_id='temel-yurttaslik-geliri', statement_scope_id='attempted-scope', statement_search_state='missing', reason='Teknik kapsam örneği.'))
        for suffix, day in [('first', '2026-09-25'), ('second', '2026-09-26')]:
            records['practice_event'].append(dict(records['practice_event'][0], id=suffix, event_at=day, title='Teknik olay ' + suffix))
            records['practice_event_evidence'].append(dict(records['practice_event_evidence'][0], event_id=suffix))
            records['practice_relation'].append(dict(records['practice_relation'][0], id=suffix, event_id=suffix))
        tip_statement = dict(records['practice_statement'][0], id='tip-statement', party_id='tip', topic_id='demokrasi-katilim', summary_finding_id='03-v2-tip-instrument-summary', quote_finding_id='03-v2-tip-instrument-quote', statement_at=None, date_precision='unknown', uncertainty_reason='Teknik örnekte tarih bilinmiyor.', version_id='0203-tip-program-v1', comparison_row_id='04-03-v3-03-v2-tip-demokrasi')
        records['practice_statement'].append(tip_statement)
        records['practice_relation'].append(dict(records['practice_relation'][0], id='tip-shared', statement_id='tip-statement', party_id='tip', topic_id='demokrasi-katilim', target_finding_id=tip_statement['summary_finding_id'], explanation_finding_id='tip-explanation'))
        records['practice_source_party'].append(dict(records['practice_source_party'][0], party_id='tip', scope_reason='Teknik ortak kapsam örneği.'))
        records['practice_source_party'].append(dict(records['practice_source_party'][0], party_id='demokrat', scope_reason='Teknik ortak kapsam örneği.'))
        for kind, values in [
            ('finding', dict(id='tip-explanation', party_id='tip', heading='Söylem ve uygulama', pair_id='tip-explanation', text='Teknik ilişki örneği.', provenance='summary', epistemic_type='claim')),
            ('review', dict(id='review-tip-explanation', kind='finding', subject_id='tip-explanation', reviewer_kind='agent', reviewed_at='2026-11-17T19:26:00+00:00', result='reviewed', reason='Teknik örnek.')),
        ]:
            package['entries'].append(dict(kind=kind, values=values))
        for passage in ('03-v2-tip-instrument-passage', '0105-cesme-p'):
            package['entries'].append(dict(kind='finding_evidence', values=dict(finding_id='tip-explanation', passage_id=passage, role='support')))
            package['entries'].append(dict(kind='verification', values=dict(finding_id='tip-explanation', passage_id=passage, checked_at='2026-11-17T19:26:00+00:00', result='confirmed', reason='Teknik örnek.')))
        for fid in ('03-v2-tip-instrument-summary', '03-v2-tip-instrument-quote', '0304-tip-program-context-genel-oy-summary', '0304-tip-program-context-senato-summary'):
            package['entries'].append(dict(kind='verification', values=dict(finding_id=fid, passage_id='03-v2-tip-instrument-passage', checked_at='2026-11-17T19:26:00+00:00', result='confirmed', reason='Teknik örnek.')))
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            shutil.copyfile(arsiv.DATA / 'releases' / base / 'records.sqlite3', work / 'records.sqlite3')
            try:
                _load_practice_copy(work, package, base)
            except (ValueError, arsiv.sqlite3.Error) as exc:
                self.fail('Versioned unmatched records must load through the real adapter: ' + str(exc))
            exported = arsiv.export_db(work / 'records.sqlite3', 'fixture')
            self.assertEqual(exported['practice_unmatched'], records['practice_unmatched'])
            html = arsiv.render_comparison_snapshot(exported, arsiv.render_report)
            class IDs(HTMLParser):
                def __init__(self):
                    super().__init__(); self.ids = []; self.links = []; self.articles = []; self.article_links = {}
                def handle_starttag(self, tag, attrs):
                    attrs = dict(attrs)
                    if 'id' in attrs: self.ids.append(attrs['id'])
                    if tag == 'article': self.articles.append(attrs.get('id'))
                    if tag == 'a' and attrs.get('href', '').startswith('#'):
                        link = attrs['href'][1:]; self.links.append(link)
                        if self.articles and self.articles[-1]: self.article_links.setdefault(self.articles[-1], []).append(link)
                def handle_endtag(self, tag):
                    if tag == 'article': self.articles.pop()
            dom = IDs(); dom.feed(html)
            duplicates = [key for key, count in Counter(dom.ids).items() if count > 1]
            self.assertEqual(duplicates, [])
            for prefix in ('party', 'comparison'):
                self.assertIn('id="' + prefix + '-unmatched-unmatched-1"', html)
                for rid in ('first', 'second', 'tracer-relation-id', 'tip-shared'):
                    self.assertIn(prefix + '-practice-' + rid, dom.ids)
                self.assertLess(dom.ids.index(prefix + '-practice-first'), dom.ids.index(prefix + '-practice-second'))
                self.assertLess(dom.ids.index(prefix + '-practice-second'), dom.ids.index(prefix + '-practice-tracer-relation-id'))
                self.assertIn(prefix + '-practice-tip-shared', dom.links)
                self.assertIn(prefix + '-practice-tracer-relation-id', dom.links)
                for rid, row, passage, other in [('tracer-relation-id', records['practice_statement'][0]['comparison_row_id'], '0105-speech-p', 'tip-shared'), ('tip-shared', tip_statement['comparison_row_id'], '03-v2-tip-instrument-passage', 'tracer-relation-id')]:
                    links = dom.article_links[prefix + '-practice-' + rid]
                    self.assertIn('comparison-' + row, links)
                    self.assertIn('source-' + passage, links)
                    self.assertIn(prefix + '-practice-' + other, links)
            self.assertIn('comparison-' + tip_statement['comparison_row_id'], dom.links)
            self.assertIn('source-03-v2-tip-instrument-passage', dom.links)
            self.assertIn('Henüz incelenmedi', html)
            self.assertIn('Doğrulanamadı', html)
            for prefix in ('party', 'comparison'):
                self.assertIn(prefix + '-unmatched-unmatched-missing', dom.ids)
            import copy
            for mutation in ('scope', 'attempt', 'marker', 'contradiction'):
                bad = copy.deepcopy(exported)
                if mutation == 'scope': bad['practice_unmatched'][0]['statement_scope_id'] = 'missing-scope'
                if mutation == 'attempt': bad['practice_unmatched'][0]['statement_search_state'] = 'missing'
                if mutation == 'marker': bad.pop('practice_variant_contract')
                if mutation == 'contradiction': bad['practice_unmatched'][0]['event_id'] = 'tracer-cesme'
                with self.assertRaises(ValueError): validate_practices(bad)
            old_shape = {k: v for k, v in exported.items() if k not in ('practice_variant_contract', 'practice_scope', 'practice_attempt', 'practice_unmatched')}
            with self.assertRaises(ValueError): validate_practice_descent(exported, old_shape)
            tampered = work / 'tampered.sqlite3'
            shutil.copyfile(work / 'records.sqlite3', tampered)
            with arsiv.sqlite3.connect(tampered) as db:
                db.execute('DROP TABLE practice_variant_contract')
            with self.assertRaises(ValueError): arsiv.export_db(tampered, 'tampered')

    def test_renderer_26_reproduces_current_archive(self):
        folder = arsiv.DATA / 'releases' / 'f67ca0a35e634035bf3aa83a46571f50'
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        self.assertEqual(arsiv.render_comparison_snapshot(data, arsiv.render_v26_report).encode('utf-8'),
                         (folder / 'index.html').read_bytes())

    def test_statement_once_and_events_in_date_order_in_both_views(self):
        folder = arsiv.DATA / 'releases' / 'f67ca0a35e634035bf3aa83a46571f50'
        data = json.loads((folder / 'records.json').read_text(encoding='utf-8'))
        event = data['practice_event'][0]
        relation = data['practice_relation'][0]
        evidence = data['practice_event_evidence'][0]
        for suffix, date in [('later', '2026-10-01'), ('earlier', '2026-09-01')]:
            data['practice_event'].append(dict(event, id=suffix, title='Olay ' + suffix, event_at=date))
            data['practice_relation'].append(dict(relation, id=suffix, event_id=suffix))
            data['practice_event_evidence'].append(dict(evidence, event_id=suffix))
        html = arsiv.render_comparison_snapshot(data, arsiv.render_report)
        for prefix in ('party', 'comparison'):
            self.assertLess(html.index('id="' + prefix + '-practice-earlier"'),
                            html.index('id="' + prefix + '-practice-later"'))
        self.assertEqual(html.count('data-finding-id="tracer-speech-quote"'), 2)


if __name__ == '__main__':
    unittest.main()
