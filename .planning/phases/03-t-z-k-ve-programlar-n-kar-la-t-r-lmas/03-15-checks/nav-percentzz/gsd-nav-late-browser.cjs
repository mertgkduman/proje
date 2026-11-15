#!/usr/bin/env node
const fs=require('fs'),{spawn}=require('child_process');
const profile=process.argv.find(arg=>arg.startsWith('--user-data-dir=')).slice('--user-data-dir='.length);
process.on('SIGTERM',()=>{});
const child=spawn(process.env.NAV_REAL_BROWSER,process.argv.slice(2),{stdio:['ignore','ignore','inherit',3,4]});
child.on('exit',()=>setTimeout(()=>{
 fs.mkdirSync(profile,{recursive:true});
 fs.writeFileSync(profile+'/late-write','late');
 fs.appendFileSync(process.env.NAV_LATE_TRACE,JSON.stringify({profile,time:Date.now()})+'\n');
 process.exit(0);
},500));
