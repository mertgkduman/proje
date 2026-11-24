from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'leaders-2023-03-validation.py').read_text()
s=s.replace("case = 'leaders-2023-03'", "case = 'education-2023'").replace("stem = '0411-saadet-six-leaders-2023'", "stem = '0411-saadet-education-2023'")
s=s.replace('1ffba5e74656068953dd6157a87dd0d212a4ed7e471ac9b1bb9072aa8570d161','4dc52f051576cdc4f2eab0bec4361569eb3e172572757e655c5c852f86b6e74f').replace('6680c0291b2048552e28a9762d31b60bb10bdf1d31a2b51b978ed76b3566ef16','cd17be98c22acb24f1ed778e3d4869a31bd661c96524ef6a4718a80fbcb15f31')
s=s.replace('(36, 32, 0)','(37, 33, 0)').replace("('2023','toplantı','aday')", "('22 Şubat','30 Mart','3 Nisan','uzaktan')").replace('SAADET_SIX_LEADERS_2023_BOTH_VIEWS_OK','SAADET_EDUCATION_2023_BOTH_VIEWS_OK')
(p/'education-2023-validation.py').write_text(s)
