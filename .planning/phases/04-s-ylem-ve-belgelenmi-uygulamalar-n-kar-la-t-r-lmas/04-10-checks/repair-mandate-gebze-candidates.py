import copy, hashlib, json, sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
import uygulamalar as rules
D=Path(__file__).parent
base=json.loads(Path('data/releases/f67ca0a35e634035bf3aa83a46571f50/records.json').read_text())
raw=Path('data/practices/sources/emep/objects/4652802c6a033afbb51a35e4048f24d11f81cd482fbe778e2820123985e59dab/original.html.bin').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='4652802c6a033afbb51a35e4048f24d11f81cd482fbe778e2820123985e59dab'
text=html_source_text(raw)
pos=text.index('<td>BAYHAN</td>')
start=text.rfind('<td>',0,pos)
end=text.index('</td>',text.index('19:33:43',pos))+5
new_exact=text[start:end]
assert 'BAYHAN' in new_exact and 'RET' in new_exact and '19:33:43' in new_exact and '\ufffd' in new_exact
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
specs=[
 ('mandate-3761-union-draft.json','mandate-3761-union-review-draft.json','mandate-3761-corrected-draft.json'),
 ('gebze-congress-union-draft.json','gebze-congress-union-review-draft.json','gebze-congress-corrected-draft.json'),
 ('izmit-congress-union-draft.json','izmit-congress-union-review-draft.json','izmit-congress-corrected-draft.json'),
 ('kocaeli-congress-union-draft.json','kocaeli-congress-union-review-draft.json','kocaeli-congress-corrected-draft.json'),
 ('luleburgaz-congress-branch-draft.json','luleburgaz-congress-branch-review-draft.json','luleburgaz-congress-corrected-draft.json')]
receipt=[]
for package_name,review_name,outname in specs:
    package=json.loads((D/package_name).read_text())
    review=json.loads((D/review_name).read_text())
    changed=[]
    for entry in package['entries']:
        if entry['kind']=='passage' and entry['values']['id']=='0410-emep-tezkere-3761-ballot-emep-p':
            old=entry['values']['exact']; assert old!=new_exact and 'BAYHAN' in old
            entry['values']['exact']=new_exact
            changed.append('0410-emep-tezkere-3761-ballot-emep-p: validatorın HTML çözümlemesindeki özgün satır; U+FFFD kaynak görüntüsünde değil, doğrulayıcı çözümlemesindedir')
        if entry['kind']=='source_attribution' and entry['values']['version_id']=='0410-emep-gebze-2026-party-v1':
            assert entry['values']['kind']=='party'
            entry['values']['kind']='party_publication'
            changed.append('0410-emep-gebze-2026-party-v1: party → party_publication')
    assert changed and changed[0].startswith('0410-emep-tezkere')
    if package_name!='mandate-3761-union-draft.json': assert len(changed)==2
    data=copy.deepcopy(base)
    for entry in package['entries']:
        if entry['values'] not in data.setdefault(entry['kind'],[]): data[entry['kind']].append(entry['values'])
    for table,rows in package['practice_records'].items(): data.setdefault(table,[]).extend(row for row in rows if row not in data[table])
    rules.validate_practices(data)
    rules.validate_practice_source_review(data,review['practice_source_review'],require_coverage=False,party_id='emep')
    out=D/outname
    with out.open('x') as f:json.dump(package,f,ensure_ascii=False,indent=2);f.write('\n')
    receipt.append(dict(previous_package=package_name,previous_sha256=sha(D/package_name),corrected_package=outname,corrected_sha256=sha(out),unchanged_review=review_name,review_sha256=sha(D/review_name),changed_rows=changed,semantic_review_count=len(review['practice_source_review'])))
out=D/'mandate-gebze-correction-receipt.json'
with out.open('x') as f:json.dump(dict(failures=['62412226: Pasaj özgün belgede bulunamadı','62413216 ve 62413720: Kaynak türü ve atıf uyuşmuyor'],original_bytes_immutable=True,ballot_renderer_limitation='CP1254 özgün belge yerel pasif görünümde doğru; HTML pasaj doğrulayıcısının kendi metni U+FFFD içeriyor. Bu çözümleme karakteri özgün belgede bulunduğu iddia edilmez.',candidates=receipt),f,ensure_ascii=False,indent=2);f.write('\n')
print('REPAIR_SEMANTIC_PASS',len(receipt))
