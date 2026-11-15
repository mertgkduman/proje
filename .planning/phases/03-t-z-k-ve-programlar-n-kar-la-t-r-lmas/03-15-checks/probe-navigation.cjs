/* Browser discovery remains in tests/browser_probe.py; this pipe enforces CSS viewport. */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{spawn}=require('node:child_process');
const [bin,url,widthArg]=process.argv.slice(2),width=Number(widthArg);
if(!bin||!url||!width)throw Error('browser, URL and viewport width required');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'proje-nav-probe-'));
const chrome=spawn(bin,['--headless','--no-sandbox','--disable-gpu','--remote-debugging-pipe','--user-data-dir='+profile],{stdio:['ignore','ignore','pipe','pipe','pipe']});
let next=0,buffer='',session;const pending=new Map();
chrome.stdio[4].on('data',chunk=>{buffer+=chunk.toString();let end;while((end=buffer.indexOf('\0'))>=0){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!line)continue;const msg=JSON.parse(line);if(pending.has(msg.id)){const [ok,no]=pending.get(msg.id);pending.delete(msg.id);msg.error?no(Error(JSON.stringify(msg.error))):ok(msg.result)}}});
function send(method,params={},sid=session){const id=++next;return new Promise((ok,no)=>{pending.set(id,[ok,no]);chrome.stdio[3].write(JSON.stringify({id,method,params,...(sid?{sessionId:sid}:{})})+'\0')})}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
(async()=>{
 const t=await send('Target.createTarget',{url:'about:blank'},null);session=(await send('Target.attachToTarget',{targetId:t.targetId,flatten:true},null)).sessionId;
 await send('Page.enable');await send('Runtime.enable');
 await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});await send('Page.navigate',{url});
 let state;
 for(let i=0;i<600;i++){await new Promise(r=>setTimeout(r,100));state=await evaluate(`document.body && ({width:innerWidth,checks:document.body.dataset.navigationChecks,error:document.body.dataset.navigationError})`);if(state && (state.checks||state.error))break}
 if(!state||state.width!==width||!state.checks||state.error)throw Error(JSON.stringify(state));
 console.log(JSON.stringify(state));
})().catch(e=>{console.error(e.stack);process.exitCode=1}).finally(async()=>{try{await send('Browser.close',{},null)}catch{}chrome.kill();fs.rmSync(profile,{recursive:true,force:true})});
setTimeout(()=>{console.error('browser probe timeout');chrome.kill();process.exit(1)},120000).unref();
