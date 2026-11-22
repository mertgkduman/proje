import copy, datetime, hashlib, json, re, shutil, sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv_gorunum import validate_view
D=Path(__file__).parent; records=json.loads(Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-12-checks/tezkere-3761-source-records.json').read_text())['entries']; source=Path('data/practices/sources/demokrat');target=Path('data/practices/sources/emep');now=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds');out=[]
for role,tmp in [('session','/tmp/gsd0410-mandate-transcript.html'),('ballot','/tmp/gsd0410-mandate-ballot.html')]:
    old='0412-tezkere-3761-'+role;new='0410-emep-tezkere-3761-'+role
    chosen=[copy.deepcopy(e) for e in records if e['kind'] in ('document','document_version','source_attribution','archive_view') and (e['values'].get('id') in (old,old+'-v1') or e['values'].get('version_id')==old+'-v1')]
    assert len(chosen)==4
    for e in chosen:
        v=e['values']
        if e['kind']=='document':v.update(id=new,party_id='emep')
        if e['kind']=='document_version':
            assert hashlib.sha256(Path(tmp).read_bytes()).hexdigest()==v['sha256']
            v.update(id=new+'-v1',document_id=new,accessed_at=now,verified_at=now)
            for k in ('original_path','readable_path'):
                src=source/v[k];dest=target/v[k];dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists():assert dest.read_bytes()==src.read_bytes()
                else:shutil.copyfile(src,dest)
        if e['kind'] in ('source_attribution','archive_view'):v['version_id']=new+'-v1'
        if e['kind']=='archive_view':
            for k in ('index_path','manifest_path'):
                src=source/v[k];dest=target/v[k];dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists():assert dest.read_bytes()==src.read_bytes()
                else:shutil.copyfile(src,dest)
            validate_view(target,v)
        out.append(e)
    text=Path(tmp).read_bytes().decode('windows-1254')
    if role=='session':
        exact='Bunun için EMEP partisi olarak tezkereye “hayır” diyoruz ve bütün Türkiye halkını da “hayır” demeye çağırıyoruz.';assert exact in text;section='Bayhan’ın EMEP adına açıklaması'
    else:
        rows=[x for x in re.findall(r'<tr[^>]*>.*?</tr>',text,re.S|re.I) if '<td>BAYHAN</td>' in x];assert len(rows)==1 and 'Emek Partisi' in rows[0] and 'RET' in rows[0];exact=rows[0][4:-5].strip();section='Bayhan’ın 17 Ekim açık oy cetvelindeki satırı'
    out.append(dict(kind='passage',values=dict(id=new+'-emep-p',version_id=new+'-v1',exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None)))
with (D/'mandate-3761-source-draft.json').open('x') as f:json.dump(dict(entries=out,status='source_read_package_pending',note='Bayhan EMEP adına konuştu; 2023te EMEP TBMM grubu olduğu varsayılmaz. Oturum anonsu ve kesin cetvel toplamları ayrı.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('MANDATE_SOURCE_CAPTURE_OK',len(out))
