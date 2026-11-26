from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'six-leaders-nov-2022-validation.py').read_text()
s=s.replace("case='six-leaders-nov-2022'","case='six-leaders-nov-2022-v2'")
s=s.replace('29efd316a1a23aeef483bae5c8fdec9a45046e3fa2823c58730f1c790dac499d','6fe02492e12793cdd5b5373016e2ad914fb0fb960bba4779a99f290c2e2f0dc4')
s=s.replace('5119b532e55b461fdd995ef824614a4bba6d44d78b345303a13c5d14835dfe76','dfa1384c1d84bf86706aa5d15390dcddda0012649f28c20e8ee0c4f541bccbbb')
(p/'six-leaders-nov-2022-v2-validation.py').write_text(s)
