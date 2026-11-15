from pathlib import Path
import json, os, subprocess, sys
base = Path('/tmp/gsd-nav-percentzz-diag-20261115')
probe = base / 'tests/comparison_navigation.cjs'
text = probe.read_text()
needle = "let next=0,buffer='',session;const pending=new Map();"
insert = """const exitDone=new Promise(resolve=>chrome.once('exit',(code,signal)=>resolve({code,signal})));
const trace=(stage,extra={})=>fs.appendFileSync('/tmp/gsd-nav-shutdown-trace.jsonl',JSON.stringify({stage,pid:chrome.pid,exitCode:chrome.exitCode,signalCode:chrome.signalCode,killed:chrome.killed,now:Date.now(),...extra})+'\\n');
let next=0,buffer='',session;const pending=new Map();"""
assert needle in text
text = text.replace(needle, insert)
needle = ".finally(async()=>{try{await send('Browser.close',{},null)}catch{}chrome.kill();fs.rmSync(profile,{recursive:true,force:true})});"
insert = """.finally(async()=>{trace('before-close');try{await send('Browser.close',{},null);trace('after-close')}catch(e){trace('close-error',{message:e.message})}chrome.kill();trace('after-kill');const exited=await exitDone;trace('after-exit',exited);fs.rmSync(profile,{recursive:true,force:true});trace('after-rm')});"""
assert needle in text
probe.write_text(text.replace(needle, insert))
env = dict(os.environ, PYTHONPATH=str(base/'tests'))
for k in ('NAV_REPORT','NAV_RECORDS','NAV_EVIDENCE'): env.pop(k,None)
cmd=[sys.executable,'-m','unittest','-v','test_comparison_navigation.ComparisonNavigation.test_unicode_and_space_ids_in_real_source_preview']
with open('/tmp/gsd-nav-shutdown-test.log','w') as log:
    r=subprocess.run(cmd,cwd=base,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=700)
Path('/tmp/gsd-nav-shutdown-test.exit').write_text(str(r.returncode)+'\n')
