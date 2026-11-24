import hashlib,importlib.util,json,os,sqlite3,subprocess,sys
from pathlib import Path
c=Path(__file__).resolve().parent; origin='62586033'; job=os.environ['SLURM_JOB_ID']; old=json.loads((c/f'agriculture-2020-{origin}.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=c/'agriculture-2020-draft.json'; r=c/'agriculture-2020-review-draft.json'
assert sha(p)==old['package_sha256']=='9ab640a732034bf893e2702e28edd897f1f28178bc3754c92962a0236dee404f'
assert sha(r)==old['review_sha256']=='2f2e58f00b788e7247f02d9b9a682fecf9ef7c7be01038fbd03a1fa79219a38d'
for part,marker in [('input','PRACTICE_INPUT_OK'),('source','PRACTICE_SOURCE_REVIEW_OK'),('preview','PRACTICE_PREVIEW_OK')]:
 assert (c/f'agriculture-2020-{origin}-{part}.exit').read_text().strip()=='0'
 assert marker in (c/f'agriculture-2020-{origin}-{part}.log').read_text()
spec=importlib.util.spec_from_file_location('validation',c.parent/'04-04-checks'/'samsun-reply-validation.py'); h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
assert h.canonical_identity()==old['canonical']
folder=Path(old['preview']); manifest=folder/'manifest.json'; assert sha(manifest)==old['preview_manifest_sha256']
for name,digest in json.loads(manifest.read_text())['files'].items(): assert sha(folder/name)==digest
report=(folder/'index.html').read_text()
for view in ('party','comparison'):
 anchor=view+'-practice-0410-agriculture-2020-relation'; start='id="'+anchor+'"'; assert report.count(start)==1 and 'href="#'+anchor+'"' in report
 card=report.split(start,1)[1].split('</article>',1)[0]
 for text in ('21 Nisan','22 Nisan','24 Nisan','8 ve 15 Mayıs','710','690'): assert text in card,(view,text)
log=c/f'agriculture-2020-{job}-independent.log'
with log.open('x') as out: subprocess.run([sys.executable,str(c/'agriculture-2020-independent.py'),origin],stdout=out,stderr=subprocess.STDOUT,check=True)
assert 'AGRICULTURE2020_INDEPENDENT_APPEND_ONLY_OK' in log.read_text()
assert h.canonical_identity()==old['canonical'] and sha(p)==old['package_sha256'] and sha(r)==old['review_sha256']
out=dict(old,job=job,origin_job=origin,wrapper_correction='Önceki wrapper 8 Mayıs aradı; gerçek iki kartta 8 ve 15 Mayıs ifadesi bulundu. Üç özgün CLI doğrulaması 0; bu wrapper exact hash, manifest, iki HTML ve bağımsız JSON/SQLite denetimini yeniden çalıştırdı.',independent=str(log))
with (c/f'agriculture-2020-{job}.json').open('x') as f:json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
print('AGRICULTURE2020_BOTH_VIEWS_AND_INDEPENDENT_OK',folder,flush=True)
