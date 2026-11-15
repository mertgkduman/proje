/* Test-only CDP client: opens the immutable report and its archive unchanged. */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{spawn}=require('node:child_process');
const [bin,url,widthArg,configArg]=process.argv.slice(2),width=Number(widthArg),cfg=JSON.parse(configArg);
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'proje-nav-'));
const chrome=spawn(bin,['--headless','--no-sandbox','--disable-gpu','--remote-debugging-pipe','--user-data-dir='+profile],{stdio:['ignore','ignore','pipe','pipe','pipe']});
let next=0,buffer='',session;const pending=new Map();
chrome.stdio[4].on('data',chunk=>{buffer+=chunk.toString();let end;while((end=buffer.indexOf('\0'))>=0){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!line)continue;const msg=JSON.parse(line);if(pending.has(msg.id)){const [ok,no]=pending.get(msg.id);pending.delete(msg.id);msg.error?no(Error(JSON.stringify(msg.error))):ok(msg.result)}}});
function send(method,params={},sid=session){const id=++next;return new Promise((ok,no)=>{pending.set(id,[ok,no]);chrome.stdio[3].write(JSON.stringify({id,method,params,...(sid?{sessionId:sid}:{})})+'\0')})}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
async function load(target){const n=await send('Page.navigate',{url:target});if(n.errorText)throw Error(n.errorText);for(let i=0;i<600;i++){await new Promise(r=>setTimeout(r,100));const s=await evaluate('({ready:document.readyState,url:location.href})');if(s.ready==='complete' && s.url.split('#')[0]===target.split('#')[0])return s}throw Error('document load timeout: '+target)}
function assert(v,m){if(!v)throw Error(m)}
(async()=>{
 const t=await send('Target.createTarget',{url:'about:blank'},null);session=(await send('Target.attachToTarget',{targetId:t.targetId,flatten:true},null)).sessionId;
 await send('Page.enable');await send('Runtime.enable');await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});
 const initial=await load(url);assert(initial.url.split('#')[0]===url.split('#')[0],'wrong report URL');
 if(cfg.direct){const s=await evaluate(`(()=>{const a=document.getElementById('comparison-'+${JSON.stringify(cfg.row)});return {width:innerWidth,exists:!!a,focused:!!a&&document.activeElement===a,visible:!!a&&a.checkVisibility()}})()`);assert(s.width===width&&s.exists&&s.focused&&s.visible,'direct hash: '+JSON.stringify(s));console.log(JSON.stringify({requested:url,actual:initial.url,...s}));return}
 const expression=`(async()=>{
 const cfg=${JSON.stringify(cfg)},checks=[],pause=()=>new Promise(r=>setTimeout(r,150));
 const linkTo=(container,id)=>[...container.querySelectorAll('a[href^="#"]')].find(link=>{try{return decodeURIComponent(link.hash.slice(1))===id}catch{return false}});
 const a=document.getElementById('comparison-'+cfg.row);
 checks.push(!!a && document.activeElement===a && a.checkVisibility());
 checks.push(!!a.querySelector('.summary') && !!a.querySelector('.quote') && !!a.querySelector('.citation'));
 checks.push(getComputedStyle(a.querySelector('.quote')).color==='rgb(0, 0, 0)' && getComputedStyle(a.querySelector('.summary')).color==='rgb(0, 51, 102)');
 linkTo(a,'dossier-comparison-'+cfg.row).click();await pause();
 const d=document.getElementById('dossier-comparison-'+cfg.row);
 checks.push(d.checkVisibility() && document.activeElement===d && d.closest('[role=tabpanel]').id==='party-iyi' && d.closest('section.card').id==='party-iyi-program');
 linkTo(d,'comparison-'+cfg.row).click();await pause();
 checks.push(a.checkVisibility() && document.activeElement===a && a.closest('[role=tabpanel]').id==='comparison-summary');
 history.back();await pause();checks.push(document.activeElement===d && d.checkVisibility());
 history.forward();await pause();checks.push(document.activeElement===a && a.checkVisibility());
 const cite=a.querySelector('.citation');cite.click();await pause();const s=document.getElementById(decodeURIComponent(cite.hash.slice(1)));
 const archive=s.querySelector('a.archive-view');const archiveUrl=archive&&archive.href;
 checks.push(s.id==='source-'+cfg.passage && s.open && s.checkVisibility() && document.activeElement===s && s.innerText.includes(cfg.version) && s.innerText.includes(cfg.locator) && !!archive && new URL(archive.href).pathname.endsWith('/'+cfg.archive));
 history.back();await pause();checks.push(document.activeElement===cite && cite.checkVisibility());
 history.forward();await pause();checks.push(document.activeElement===s && s.open && s.checkVisibility());
 history.back();await pause();cite.click();await pause();checks.push(document.documentElement.scrollWidth<=innerWidth);
 const old=document.activeElement;location.hash='#%ZZ';await pause();const malformedInert=document.activeElement===old;location.hash='#unknown-target';await pause();checks.push(malformedInert && document.activeElement===old);
 const proof=linkTo(document,'comparison-'+cfg.scope),scopeRow=document.getElementById('comparison-'+cfg.scope);
 checks.push(!!proof && !!scopeRow && scopeRow.innerText.includes('İncelenen kapsam:'));
 document.getElementById('tab-comparison').click();proof.click();await pause();const scopeOk=document.activeElement===scopeRow && scopeRow.checkVisibility() && !!scopeRow.querySelector('a[href^="../../"]');
 linkTo(scopeRow,'dossier-comparison-'+cfg.scope).click();await pause();const ds=document.getElementById('dossier-comparison-'+cfg.scope);
 checks.push(scopeOk && document.activeElement===ds && ds.checkVisibility() && ds.closest('section.card').id==='party-iyi-tuzuk');
 const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);checks.push(ids.length===new Set(ids).size);
 const tab=document.getElementById('tab-comparison'),event=new KeyboardEvent('keydown',{key:'ArrowUp',bubbles:true,cancelable:true});tab.dispatchEvent(event);checks.push(!event.defaultPrevented);
 const names=[...new Set([...a.closest('.comparison-topic').querySelectorAll(':scope > article.comparison-row > h4')].map(x=>x.textContent))];
 checks.push(JSON.stringify(names)===JSON.stringify(cfg.names));
 checks.push(!document.getElementById('scope-method').open && !!a.closest('.comparison-topic').querySelector(':scope > p.summary'));
 tab.focus();tab.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true,cancelable:true}));
 checks.push(document.activeElement.id==='tab-demokrat' && document.activeElement.getAttribute('aria-selected')==='true' && document.activeElement.tabIndex===0 && document.getElementById('party-demokrat').hidden===false);
 return {width:innerWidth,checks:checks.map(Number).join(''),archiveUrl};})()`;
 const state=await evaluate(expression);assert(state.width===width&&state.checks==='1'.repeat(19),'checks: '+JSON.stringify(state));
 const expectedArchive=new URL('../../'+cfg.archive,url).href;assert(state.archiveUrl===expectedArchive,'wrong archive link');
 const archive=await load(expectedArchive);const content=await evaluate(`({url:location.href,title:document.title,text:document.body.innerText.replace(/\\s+/g,' ').includes(${JSON.stringify(cfg.excerpt)})})`);
 assert(content.url===expectedArchive&&content.text&&content.title,'archive content mismatch: '+JSON.stringify(content));
 console.log(JSON.stringify({requested:url,actual:initial.url,...state,archiveRequested:expectedArchive,archiveActual:content.url,archiveTitle:content.title,archiveExcerptFound:content.text}));
})().catch(e=>{console.error(e.stack);process.exitCode=1}).finally(async()=>{try{await send('Browser.close',{},null)}catch{}chrome.kill();fs.rmSync(profile,{recursive:true,force:true})});
setTimeout(()=>{console.error('browser probe timeout');chrome.kill();process.exit(1)},150000).unref();
