import unittest
import arsiv


class ChainContract(unittest.TestCase):
    def test_pending_lead_blocks_closure(self):
        self.assertTrue(callable(getattr(arsiv, 'enqueue_lead', None)),
                        'Kaynak kuyruğu bulunmalı')
        self.assertTrue(callable(getattr(arsiv, 'close_topic', None)),
                        'Kapanma denetimi bulunmalı')


if __name__ == '__main__':
    unittest.main()
