/* Real Chrome DevTools pipe; no npm package or archived script is required. */
const fs=require('node:fs'), os=require('node:os'), path=require('node:path'), {spawn}=require('node:child_process');
const [bin,report,charter,program,outdir]=process.argv.slice(2);
if(!program)throw Error('browser, report, charter and program URLs required');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'proje-browser-'));
const chrome=spawn(bin,['--headless','--no-sandbox','--disable-gpu','--disable-background-networking','--remote-debugging-pipe','--user-data-dir='+profile],{stdio:['ignore','ignore','pipe','pipe','pipe']});
let next=0,buffer='',session,errors='';const pending=new Map();
chrome.stderr.on('data',x=>errors+=x);
chrome.stdio[4].on('data',chunk=>{buffer+=chunk.toString();let end;while((end=buffer.indexOf('\0'))>=0){const text=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!text)continue;const msg=JSON.parse(text);if(pending.has(msg.id)){const [ok,no]=pending.get(msg.id);pending.delete(msg.id);msg.error?no(Error(JSON.stringify(msg.error))):ok(msg.result)}}});
function send(method,params={},sid=session){const id=++next;return new Promise((ok,no)=>{pending.set(id,[ok,no]);chrome.stdio[3].write(JSON.stringify({id,method,params,...(sid?{sessionId:sid}:{})})+'\0')})}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
async function load(url,width=1365){await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});await send('Page.navigate',{url});for(let i=0;i<100;i++){await new Promise(r=>setTimeout(r,100));if(await evaluate('document.readyState==="complete"'))break;}await evaluate('document.fonts.ready.then(()=>true)');return evaluate('({url:location.href,title:document.title,width:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth})')}
async function shot(name){if(outdir){fs.mkdirSync(outdir,{recursive:true});const image=await send('Page.captureScreenshot',{format:'png'});fs.writeFileSync(path.join(outdir,name+'.png'),Buffer.from(image.data,'base64'))}}
function assert(value,message){if(!value)throw Error(message)}
const results=[];
(async()=>{
 const target=await send('Target.createTarget',{url:'about:blank'},null);session=(await send('Target.attachToTarget',{targetId:target.targetId,flatten:true},null)).sessionId;
 await send('Page.enable');await send('Runtime.enable');await send('Network.enable');
 for(const width of [1365,360]){
  const state=await load(report,width);assert(!state.overflow,'report overflow');
  const reading=await evaluate(`(()=>{const p=document.getElementById('party-yeni-parti');return {method:document.getElementById('scope-method').open,questions:[...p.querySelectorAll('.reader-question')].map(x=>x.innerText),quotes:[...p.querySelectorAll('.findings .quote')].filter(x=>x.getClientRects().length).map(x=>getComputedStyle(x).color),summaries:[...p.querySelectorAll('.findings .summary')].filter(x=>x.getClientRects().length).map(x=>getComputedStyle(x).color),site:!!p.querySelector('a[href="https://yenipartiyiz.biz"]'),legacy:[...p.querySelectorAll('details[id^=prior-]')].every(x=>!x.open)}})()`);
  assert(!reading.method&&reading.site&&reading.legacy&&reading.questions.length===5,'reader hierarchy/attribution');assert(reading.quotes.every(c=>c==='rgb(0, 0, 0)')&&reading.summaries.every(c=>c==='rgb(0, 51, 102)'),'quote/summary colors');
  const purposeState=await evaluate(`(()=>{const legal=document.getElementById('finding-epm-legal-summary'),purpose=document.getElementById('finding-epm-purpose-summary');return {closed:!!legal.closest('details:not([open])'),purposeClosed:!!purpose.closest('details:not([open])'),purposeVisible:purpose.checkVisibility()}})()`);
  assert(purposeState.closed&&!purposeState.purposeClosed&&purposeState.purposeVisible,'purpose must precede technical identity detail: '+JSON.stringify(purposeState));
  await shot('report-'+width);results.push({kind:'report',width,...state,questions:reading.questions});
  for(const [name,pid,url,needle] of [['charter','epm-member-rights-p',charter,'Madde 54'],['program','epm-parliamentary-p',program,'DEĞİŞİM ÇAĞRISI']]){
   await load(report,width);
   const opened=await evaluate(`(()=>{document.querySelector('.citation[href="#source-${pid}"]').click();const d=document.getElementById('source-${pid}');const a=d.querySelector('.archive-view');const result={open:d.open,url:a.href};a.click();return result})()`);
   assert(opened.open&&opened.url===url,'citation opened wrong archive');
   await new Promise(r=>setTimeout(r,200));await evaluate('document.fonts.ready.then(()=>true)');
   const archive=await evaluate(`({title:document.title,text:document.body.innerText.includes(${JSON.stringify(needle)}),scripts:document.scripts.length,forms:document.forms.length,images:[...document.images].map(x=>({loaded:x.complete&&x.naturalWidth>0,url:x.currentSrc})),resources:performance.getEntriesByType('resource').map(x=>x.name),overflow:document.documentElement.scrollWidth>innerWidth})`);
   assert(archive.text&&!archive.scripts&&!archive.forms&&!archive.overflow,'passive document content');assert(archive.images.length&&archive.images.every(x=>x.loaded),'local logo loaded');
   assert(archive.resources.every(x=>x.startsWith(new URL('.',url).href)||x.startsWith('file:')),'archive attempted remote resources');
   await shot(name+'-'+width);results.push({kind:name,width,...archive});
  }
 }
 if(process.env.PROJE_LIVE_SHOTS){for(const [name,url] of [['live-charter','https://yenipartiyiz.biz/parti-tuzugu'],['live-program','https://yenipartiyiz.biz/parti-programi']]){for(const width of [1365,360]){const state=await load(url,width);await shot(name+'-'+width);results.push({kind:name,width,...state});}}}
 console.log(JSON.stringify({status:'BROWSER_ARCHIVES_OK',results},null,2));
})().catch(e=>{console.error(e.stack,errors.slice(-1000));process.exitCode=1}).finally(async()=>{try{await send('Browser.close',{},null)}catch{}chrome.kill();fs.rmSync(profile,{recursive:true,force:true})});
setTimeout(()=>{console.error('browser probe timeout');chrome.kill();process.exit(1)},90000).unref();
