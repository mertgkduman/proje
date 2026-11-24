from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'education-2023-validation.py').read_text()
s=s.replace("case = 'education-2023'","case = 'election-2023'").replace("stem = '0411-saadet-education-2023'","stem = '0411-saadet-election-2023'")
s=s.replace('4dc52f051576cdc4f2eab0bec4361569eb3e172572757e655c5c852f86b6e74f','5e2a0d33a3557d4bf07ff4b39fcfbd781f4d19ef3e0e7a4f1bb318506b03f53f').replace('cd17be98c22acb24f1ed778e3d4869a31bd661c96524ef6a4718a80fbcb15f31','8a50931788728638d7cdeec3ec39b87fbeedd291ec359d26aa351bfd3f02fd15')
s=s.replace('(37, 33, 0)','(38, 34, 0)').replace("('22 Şubat','30 Mart','3 Nisan','uzaktan')","('18 Ocak','10 Mart','14 Mayıs','116 gün')").replace('SAADET_EDUCATION_2023_BOTH_VIEWS_OK','SAADET_ELECTION_2023_BOTH_VIEWS_OK')
(p/'election-2023-validation.py').write_text(s)
