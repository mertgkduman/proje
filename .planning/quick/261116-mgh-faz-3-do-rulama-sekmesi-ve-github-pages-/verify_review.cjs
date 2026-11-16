/* Test-only CDP client: opens the immutable report and its archive unchanged. */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{spawn}=require('node:child_process');
const [bin,url,widthArg,screenshot]=process.argv.slice(2),width=Number(widthArg);
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'proje-nav-'));
const chrome=spawn(bin,['--headless','--no-sandbox','--disable-gpu','--remote-debugging-pipe','--user-data-dir='+profile],{stdio:['ignore','ignore','pipe','pipe','pipe']});
const chromeExit=new Promise(resolve=>chrome.once('exit',resolve));
let next=0,buffer='',session;const pending=new Map();
function rejectPending(error){for(const [,no] of pending.values())no(error);pending.clear()}
chrome.stdio[3].on('error',rejectPending);
chrome.stdio[4].on('error',rejectPending);
chrome.stdio[4].on('end',()=>rejectPending(Error('browser pipe closed')));
chrome.stdio[4].on('data',chunk=>{buffer+=chunk.toString();let end;while((end=buffer.indexOf('\0'))>=0){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!line)continue;const msg=JSON.parse(line);if(pending.has(msg.id)){const [ok,no]=pending.get(msg.id);pending.delete(msg.id);msg.error?no(Error(JSON.stringify(msg.error))):ok(msg.result)}}});
function send(method,params={},sid=session){const id=++next;return new Promise((ok,no)=>{pending.set(id,[ok,no]);chrome.stdio[3].write(JSON.stringify({id,method,params,...(sid?{sessionId:sid}:{})})+'\0')})}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
async function load(target){const n=await send('Page.navigate',{url:target});if(n.errorText)throw Error(n.errorText);for(let i=0;i<600;i++){await new Promise(r=>setTimeout(r,100));const s=await evaluate('({ready:document.readyState,url:location.href})');if(s.ready==='complete' && s.url.split('#')[0]===target.split('#')[0])return s}throw Error('document load timeout: '+target)}
function assert(v,m){if(!v)throw Error(m)}
(async()=>{
 const t=await send('Target.createTarget',{url:'about:blank'},null);session=(await send('Target.attachToTarget',{targetId:t.targetId,flatten:true},null)).sessionId;
 await send('Page.enable');await send('Runtime.enable');
 await send('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
 await load(url+'#phase-03-verification');
 const state=await evaluate(`(async()=>{
 const pause=()=>new Promise(r=>setTimeout(r,150));
 const panel=document.getElementById('phase-03-verification'),tab=document.getElementById('tab-phase-03-verification');
 const checks={directLink:panel.checkVisibility()&&document.activeElement===panel,checks:panel.querySelectorAll('.review-card').length===6,examples:panel.querySelectorAll('.review-example').length===13,privateNotes:!panel.textContent.includes('hepsi gecti olsun')&&!panel.textContent.includes('developer')};
 const links=[...panel.querySelectorAll('.review-links a')];let traversed=0;
 for(const link of links){link.click();await pause();const target=document.getElementById(decodeURIComponent(link.hash.slice(1)));if(!target||!target.checkVisibility()||document.activeElement!==target)throw Error('Example target failed '+link.hash);history.back();await pause();if(!panel.checkVisibility())throw Error('Review return failed');traversed++;}
 checks.exampleNavigation=traversed===26;
 const cite=panel.querySelector('.citation');cite.click();await pause();const source=document.getElementById(decodeURIComponent(cite.hash.slice(1)));checks.source=source.open&&source.checkVisibility()&&!!source.querySelector('.archive-view');history.back();await pause();checks.sourceReturn=panel.checkVisibility()&&document.activeElement===cite;
 tab.focus();tab.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true,cancelable:true}));checks.keyboard=document.activeElement.id==='tab-comparison';
 document.activeElement.dispatchEvent(new KeyboardEvent('keydown',{key:'End',bubbles:true,cancelable:true}));checks.keyboardEnd=document.activeElement===tab&&panel.checkVisibility();
 const summary=panel.querySelector('.summary'),quote=panel.querySelector('.quote');checks.originColors=getComputedStyle(summary).color==='rgb(0, 51, 102)'&&getComputedStyle(quote).color==='rgb(0, 0, 0)';
 checks.noOverflow=document.documentElement.scrollWidth<=innerWidth;
 const ids=[...document.querySelectorAll('[id]')].map(x=>x.id);checks.uniqueIds=ids.length===new Set(ids).size;
 window.scrollTo(0,0);return {checks,traversed,width:innerWidth,title:panel.querySelector('h2').textContent};})()`);
 assert(Object.values(state.checks).every(Boolean),JSON.stringify(state));
 if(screenshot){const shot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});fs.writeFileSync(screenshot,Buffer.from(shot.data,'base64'));}
 console.log(JSON.stringify({url,...state}));
})().catch(e=>{console.error(e.stack);process.exitCode=1}).finally(async()=>{
 send('Browser.close',{},null).catch(()=>{});
 const waitForExit=ms=>new Promise(resolve=>{const timer=setTimeout(()=>resolve(false),ms);chromeExit.then(()=>{clearTimeout(timer);resolve(true)})});
 if(!await waitForExit(5000)){
  chrome.kill('SIGKILL');
  if(!await waitForExit(5000))throw Error('browser did not exit');
 }
 fs.rmSync(profile,{recursive:true,force:true,maxRetries:8,retryDelay:100});
});
setTimeout(()=>{console.error('browser probe timeout');chrome.kill();process.exit(1)},150000).unref();
