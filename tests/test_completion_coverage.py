"""Substantive closure must survive omissions in the selected source inventory."""
import json
import unittest

import arsiv
import test_comparisons


class CompletionCoverageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reviewed = test_comparisons.ComparisonReleaseTest.reviewed_current()
        cls.taxonomy = cls.reviewed['comparison_contract'][0]['taxonomy_version']

    def altered(self, table, index, **changes):
        data = dict(self.reviewed)
        data[table] = list(data[table])
        data[table][index] = dict(data[table][index], **changes)
        return data

    def test_rejects_changed_applicable_level_and_organ(self):
        index = next(i for i, r in enumerate(self.reviewed['comparison_row'])
                     if r['taxonomy_version'] == self.taxonomy and r['state'] == 'evidence')
        row = self.reviewed['comparison_row'][index]
        for key in ('level', 'organ'):
            with self.subTest(key=key), self.assertRaises(ValueError):
                arsiv.validate_comparisons(self.altered('comparison_row', index, **{key: row[key] + ' değiştirilmiş'}))

    def test_rejects_missing_source_review(self):
        data = dict(self.reviewed)
        marker = dict(data['comparison_completion'][0])
        evidence = json.loads(marker['evidence'])
        evidence['source_review']['checks'] = []
        marker['evidence'] = json.dumps(evidence, ensure_ascii=False)
        data['comparison_completion'] = [marker]
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)

    def test_rejects_dropped_field_and_synthesis(self):
        for table, select in (
            ('comparison_field', lambda x: any(r['id'] == x['row_id'] and r['taxonomy_version'] == self.taxonomy for r in self.reviewed['comparison_row'])),
            ('comparison_synthesis', lambda x: x['taxonomy_version'] == self.taxonomy),
        ):
            data = dict(self.reviewed)
            target = next(x for x in data[table] if select(x))
            data[table] = [x for x in data[table] if x is not target]
            with self.subTest(table=table), self.assertRaises(ValueError):
                arsiv.validate_comparisons(data)

    def test_rejects_open_selected_states(self):
        index = next(i for i, r in enumerate(self.reviewed['comparison_row'])
                     if r['taxonomy_version'] == self.taxonomy and r['state'] == 'evidence')
        for state in ('not_researched', 'in_progress'):
            with self.subTest(state=state), self.assertRaises(ValueError):
                arsiv.validate_comparisons(self.altered('comparison_row', index, state=state))

    def test_rejects_missing_topic_party_and_unmatched_inventory(self):
        data = dict(self.reviewed)
        row = next(r for r in data['comparison_row'] if r['taxonomy_version'] == self.taxonomy)
        data['comparison_row'] = [r for r in data['comparison_row'] if not
                                  (r['taxonomy_version'] == self.taxonomy and r['topic_id'] == row['topic_id'] and r['party_id'] == row['party_id'])]
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(data)
        index = next(i for i, r in enumerate(self.reviewed['comparison_source_inventory'])
                     if r['taxonomy_version'] == self.taxonomy and r['full_text_available'])
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(self.altered('comparison_source_inventory', index, unmatched_headings='["eşleşmeyen bölüm"]'))

    def test_rejects_available_document_as_missing(self):
        index = next(i for i, r in enumerate(self.reviewed['comparison_source_inventory'])
                     if r['taxonomy_version'] == self.taxonomy and r['full_text_available'])
        with self.assertRaises(ValueError):
            arsiv.validate_comparisons(self.altered('comparison_source_inventory', index, full_text_available=0))

