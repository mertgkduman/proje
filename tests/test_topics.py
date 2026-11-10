import unittest
import arsiv


class TopicContract(unittest.TestCase):
    def test_real_dictionary_contains_a_sourced_verified_topic(self):
        release = arsiv.current()
        data = arsiv.export_db(arsiv.DATA / 'releases' / release / 'records.sqlite3', release)
        verified = [t for t in data.get('topic', []) if t['status'] == 'verified']
        self.assertTrue(verified, 'En az bir gerçek belge dayanağı bulunan konu gerekli')
        self.assertTrue(all(any(b['topic_id'] == t['id'] and b['taxonomy_version'] == t['taxonomy_version'] for b in data['topic_basis']) for t in verified))
