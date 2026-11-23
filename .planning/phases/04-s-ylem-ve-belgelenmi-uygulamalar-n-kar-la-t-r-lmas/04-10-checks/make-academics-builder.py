from pathlib import Path

D = Path(__file__).parent
s = (D / 'prepare-mesem-35768.py').read_text()
s = s.replace('sik-makas-union-draft.json', 'BASE_PACKAGE').replace('sik-makas-union-review-draft.json', 'BASE_REVIEW')
s = s.replace('mesem-35768', 'academics-37207').replace('35768', '37207')
s = s.replace('BASE_PACKAGE', 'mesem-35768-union-draft.json').replace('BASE_REVIEW', 'mesem-35768-union-review-draft.json')
for a, b in [
    ('2025-10-10', '2025-12-01'), ('10 Ekim 2025te', '1 Aralık 2025te'), ('27 Kasım 2025te', '9 Şubat 2026da'),
    ('is-sagligi', 'sendika-grev'), ('0410-safety-statement-finding', '0410-labor-statement-finding'),
    ('0410-safety-statement', '0410-labor-statement'), ('0410-emep-safety-program-p', '0309-emep-program-006-1-passage'),
    ('TBMM MESEM öğrencileri ve iş kazaları yazılı soru ve yanıt kaydı', 'TBMM vakıf üniversitelerinde akademisyenlerin çalışma ve sendikal hakları soru ve yanıt kaydı'),
    ('MESEM öğrencileri ve iş kazaları hakkında yazılı soru', 'Vakıf üniversitelerinde akademisyenlerin hakları hakkında yazılı soru'),
    ('tbmm-28-4-7-37207-mesem-is-kazalari', 'tbmm-28-4-7-37207-akademisyen-haklari'),
    ('Program işyerlerinde iş kazalarına karşı önlem alınmasını savunur. İskender Bayhan MESEM öğrencileri ve iş kazalarına ilişkin yazılı soru verdi; TBMM kaydı bakanlığın süre dışı yanıtını bildirir.', 'Program işçilerin sendikal örgütlenme hakkını savunur. İskender Bayhan vakıf üniversitelerinde akademisyenlerin iş ve sendikal hakları hakkında soru verdi; TBMM kaydı bakanlığın süre dışı yanıtını bildirir.'),
    ('Program iş kazalarına karşı önlem ister; soru mesleki eğitimde öğrencilerin iş kazaları ve denetimleri hakkında bilgi ister.', 'Program sendikal örgütlenme hakkını savunur; soru vakıf üniversitelerinde çalışan akademisyenlerin iş güvencesi ve sendikal haklarına ilişkin bilgi ister.'),
    ('MESEM_37207_SEMANTIC_PASS', 'ACADEMICS_37207_SEMANTIC_PASS'),
]:
    assert a in s, a
    s = s.replace(a, b)
needle = "entries.extend(read(D / 'academics-37207-source-draft.json')['entries'])"
assert needle in s
s = s.replace(needle, needle + "\nentries.extend(read(D / 'academics-37207-party-source-draft.json')['entries'])")
needle = "pids = ['0309-emep-program-006-1-passage',"
assert needle in s
s = s.replace(needle, "pids = ['0309-emep-program-006-1-passage', '0410-emep-academics-37207-party-union-p',")
s = s.replace("for role in ('detail', 'question', 'reply'):", "for role in ('detail', 'question', 'reply', 'party'):")
s = s.replace("else 'Bakanlık yanıtı'", "else 'Bakanlık yanıtı' if role == 'reply' else 'Bayhan yazılı soru içeriği'")
(D / 'prepare-academics-37207.py').write_text(s)
