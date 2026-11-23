import hashlib,json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text,readable_bytes
root=Path('data/practices/sources/emep');raw=Path('/tmp/gsd0410-election2015/decision.pdf').read_bytes();sha=hashlib.sha256(raw).hexdigest();obj=root/'objects'/sha;obj.mkdir(parents=True,exist_ok=True)
url='https://www.ysk.gov.tr/doc/karar/dosya/2041/2015-1584.pdf';ident='0410-emep-election-2015-ysk';version=ident+'-v1';now=datetime.now(timezone.utc).isoformat(timespec='seconds')
for name,content in [('original.pdf',raw),('readable.html',readable_bytes(raw,'pdf',legacy=False))]:
 p=obj/name
 if p.exists():assert p.read_bytes()==content
 else:p.write_bytes(content)
exact='2- Ancak, Demokratik Gelişim Partisi, Doğru Yol Partisi, Emek Partisi, Genç Parti, Muhafazakâr\nYükseliş Partisi, Özgürlük ve Dayanışma Partisi ile Türkiye Komünist Partisi\'nin, 2820 sayılı Siyasi Partiler\nKanunu’nun 37. maddesinin ikinci fıkrası uyarınca, adaylarını merkez yoklaması usulü ile\nbelirleyebileceğine,'
assert exact in pdf_page_text(Path('/tmp/gsd0410-election2015/decision.pdf'),2)
entries=[dict(kind='document',values=dict(id=ident,party_id='emep',title='YSK 1 Eylül 2015 tarihli 1584 sayılı karar',source_kind='official')),dict(kind='document_version',values=dict(id=version,document_id=ident,original_url=url,final_url=url,document_date='2015-09-01',date_precision='day',date_unknown_reason=None,version_label='2015/1584 sayılı karar; yayın zamanı doğrulanmadı',accessed_at=now,verified_at=now,mime='application/pdf',sha256=sha,original_path='objects/'+sha+'/original.pdf',readable_path='objects/'+sha+'/readable.html')),dict(kind='source_attribution',values=dict(version_id=version,kind='official',publisher='Yüksek Seçim Kurulu',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='1 Eylül karar tarihi; belgenin yayın tarihi ayrıca doğrulanmadı.')),dict(kind='passage',values=dict(id=ident+'-result-p',version_id=version,exact=exact,prefix=None,suffix=None,article=None,section='Merkez yoklaması imkânına ilişkin karar',pdf_page_index=2,printed_page='3'))]
prohibition='yapacağını Kurulumuz Başkanlığına bildirmediğinden, Demokratik Gelişim Partisi, Doğru Yol Partisi, Emek\nPartisi, Genç Parti, Muhafazakâr Yükseliş Partisi, Özgürlük ve Dayanışma Partisi ile Türkiye Komünist\nPartisi\'nin bu aşamadan sonra adaylarını ön seçim veya aday yoklaması usulü ile belirlemesinin mümkün\nolmadığına,'
assert prohibition in pdf_page_text(Path('/tmp/gsd0410-election2015/decision.pdf'),2)
entries.append(dict(kind='passage',values=dict(id=ident+'-restriction-p',version_id=version,exact=prohibition,prefix=None,suffix=None,article=None,section='Önseçim ve aday yoklamasına ilişkin kararın devamı',pdf_page_index=2,printed_page='3')))
out=Path(__file__).parent/'election-2015-source-draft.json'
with out.open('x') as f:json.dump(dict(entries=entries,status='source_read_package_pending',note='YSK 1 Eylül 2015 kararı süresinde bildirim yapılmadığını, önseçim veya aday yoklamasının artık mümkün olmadığını ve merkez yoklamasının mümkün olduğunu söyler; fiilen uygulanan yöntem ya da 2015 tüzük sürümü ayrı araştırılmalı.'),f,ensure_ascii=False,indent=2);f.write('\n')
print('ELECTION2015_SOURCE_OK',sha)
