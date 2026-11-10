import unittest
import arsiv


class ScopeContract(unittest.TestCase):
    def test_scope_writer_exists(self):
        self.assertTrue(callable(getattr(arsiv, 'record_scope', None)))
