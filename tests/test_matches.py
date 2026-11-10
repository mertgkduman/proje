import unittest
import arsiv


class MatchContract(unittest.TestCase):
    def test_match_api_enforces_evidence_contract(self):
        self.assertTrue(callable(getattr(arsiv, 'record_match', None)),
                        'Söylem ve oluş kanıtını ayrı doğrulayan kayıt arayüzü gerekli')
