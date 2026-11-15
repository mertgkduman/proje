#!/usr/bin/env node
const fs=require('fs'),{spawn}=require('child_process');
const mode=process.env.WR01_MODE,profile=process.argv.find(a=>a.startsWith('--user-data-dir=')).slice(16);
const trace=(event,extra={})=>fs.appendFileSync(process.env.WR01_TRACE,JSON.stringify({event,mode,pid:process.pid,profile,time:Date.now(),...extra})+'\n');
const browser=spawn(process.env.WR01_BROWSER,process.argv.slice(2),{stdio:['ignore','ignore','ignore','pipe','pipe']});
const input=fs.createReadStream(null,{fd:3}),output=fs.createWriteStream(null,{fd:4});
let inputBuffer='',outputBuffer='',closeId=null;
trace('start',{browserPid:browser.pid});
input.on('data',chunk=>{inputBuffer+=chunk.toString();let end;while((end=inputBuffer.indexOf('\0'))>=0){let msg=inputBuffer.slice(0,end);inputBuffer=inputBuffer.slice(end+1);if(!msg)continue;let data=JSON.parse(msg);if(data.method==='Browser.close'){closeId=data.id;trace('close-request');}browser.stdio[3].write(msg+'\0');}});
browser.stdio[4].on('data',chunk=>{outputBuffer+=chunk.toString();let end;while((end=outputBuffer.indexOf('\0'))>=0){let msg=outputBuffer.slice(0,end);outputBuffer=outputBuffer.slice(end+1);if(!msg)continue;let data=JSON.parse(msg);if(data.id===closeId){trace('suppress-close-response');continue;}output.write(msg+'\0');}});
browser.on('exit',(code,signal)=>{trace('browser-exit',{code,signal});if(mode==='exit')process.exit(0);});
process.on('SIGTERM',()=>{trace('term');browser.kill('SIGKILL');process.exit(143)});
