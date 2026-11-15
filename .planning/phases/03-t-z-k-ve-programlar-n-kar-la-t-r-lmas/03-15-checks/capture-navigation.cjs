/* Gerçek Chromium DevTools: kesin viewport ve seçili karşılaştırma kaydı. */
const fs=require('node:fs'),os=require('node:os'),path=require('node:path'),{spawn}=require('node:child_process');
const [bin,report,outdir]=process.argv.slice(2);
if(!outdir)throw Error('browser, report URL and output directory required');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'proje-nav-shot-'));
const chrome=spawn(bin,['--headless','--no-sandbox','--disable-gpu','--remote-debugging-pipe','--user-data-dir='+profile],{stdio:['ignore','ignore','pipe','pipe','pipe']});
let next=0,buffer='',session;const pending=new Map();
chrome.stdio[4].on('data',chunk=>{buffer+=chunk.toString();let end;while((end=buffer.indexOf('\0'))>=0){const line=buffer.slice(0,end);buffer=buffer.slice(end+1);if(!line)continue;const msg=JSON.parse(line);if(pending.has(msg.id)){const [ok,no]=pending.get(msg.id);pending.delete(msg.id);msg.error?no(Error(JSON.stringify(msg.error))):ok(msg.result)}}});
function send(method,params={},sid=session){const id=++next;return new Promise((ok,no)=>{pending.set(id,[ok,no]);chrome.stdio[3].write(JSON.stringify({id,method,params,...(sid?{sessionId:sid}:{})})+'\0')})}
async function evaluate(expression){const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});if(r.exceptionDetails)throw Error(JSON.stringify(r.exceptionDetails));return r.result.value}
(async()=>{
 const t=await send('Target.createTarget',{url:'about:blank'},null);session=(await send('Target.attachToTarget',{targetId:t.targetId,flatten:true},null)).sessionId;
 await send('Page.enable');await send('Runtime.enable');fs.mkdirSync(outdir,{recursive:true});const results=[];
 for(const width of [360,1365]){
  await send('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});
  await send('Page.navigate',{url:report+'#comparison-04-03-v3-03-v2-iyi-demokrasi'});
  for(let i=0;i<300;i++){await new Promise(r=>setTimeout(r,100));if(await evaluate('document.readyState==="complete" && !!document.getElementById("comparison-04-03-v3-03-v2-iyi-demokrasi")'))break}
  const state=await evaluate(`(()=>{let r=document.getElementById('comparison-04-03-v3-03-v2-iyi-demokrasi');return {width:innerWidth,focused:document.activeElement===r,visible:r.checkVisibility(),overflow:document.documentElement.scrollWidth>innerWidth}})()`);
  if(state.width!==width||!state.focused||!state.visible||state.overflow)throw Error(JSON.stringify(state));
  for(const view of ['row','topic']){
   if(view==='topic')await evaluate(`document.getElementById('comparison-04-03-v3-03-v2-iyi-demokrasi').closest('.comparison-topic').scrollIntoView();true`);
   const shot=await send('Page.captureScreenshot',{format:'png'});const file=path.join(outdir,'navigation-'+view+'-'+width+'.png');fs.writeFileSync(file,Buffer.from(shot.data,'base64'));results.push({...state,view,file});
  }
 }
 console.log(JSON.stringify({report,results},null,2));
})().catch(e=>{console.error(e.stack);process.exitCode=1}).finally(async()=>{try{await send('Browser.close',{},null)}catch{}chrome.kill();fs.rmSync(profile,{recursive:true,force:true})});
setTimeout(()=>{console.error('browser screenshot timeout');chrome.kill();process.exit(1)},120000).unref();
