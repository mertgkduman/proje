from pathlib import Path
p = Path(__file__).resolve().parent
s = (p/'six-leaders-2022-validation.py').read_text()
s = s.replace('six-leaders-2022', 'leaders-2023-03').replace('0411-saadet-leaders-2023-03', '0411-saadet-six-leaders-2023')
s = s.replace('e273528bd5104b6556ea60bb028ccc95d61ac7d3a7376907eaf7334d31f580c2','1ffba5e74656068953dd6157a87dd0d212a4ed7e471ac9b1bb9072aa8570d161')
s = s.replace('d37c4bd2ecbaf6c82c856adcb9e9b20f706ff4d87d0be384ef463ea08d649d23','6680c0291b2048552e28a9762d31b60bb10bdf1d31a2b51b978ed76b3566ef16')
s = s.replace('(34, 30, 0)', '(36, 32, 0)').replace("('2022','lider','toplantı')", "('2023','toplantı','aday')").replace('SAADET_SIX_LEADERS_2022_BOTH_VIEWS_OK','SAADET_SIX_LEADERS_2023_BOTH_VIEWS_OK')
(p/'leaders-2023-03-validation.py').write_text(s)
