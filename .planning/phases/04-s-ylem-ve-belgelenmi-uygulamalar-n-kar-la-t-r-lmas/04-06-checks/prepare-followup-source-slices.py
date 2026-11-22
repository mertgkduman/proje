"""Takip kaynaklarının doğrulanmamış owner-scope pasaj girdileri."""
import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
caps=json.loads((checks/'followup-captures.json').read_text())
details={
 'ipek_result':('Zeyni İpek hakkında Merkez Disiplin Kurulu açıklaması','partiden kesin çıkarılmasına (ihraç edilmesine) oy birliği ile karar verilmiştir.',None),
 'ipek_aug':('Zeyni İpek Ağustos açıklaması','bu kararımı resmileştirmedim.','Haber Merkezi'),
 'silopi_rally':('Silopi ilçe örgütünün yürüyüşü','belediye binasına yürüyüş düzenledi.',None),
}
entries=[]
def add(kind,values):entries.append(dict(kind=kind,values=values))
for c in caps:
 name=c['id'];title,exact,author=details[name]; ident='0406-'+name.replace('_','-');v=ident+'-v1'
 assert exact in html_source_text((root/c['original_path']).read_bytes()),name
 add('document',dict(id=ident,party_id='dem',title=title,source_kind='journalism'))
 add('document_version',dict(id=v,document_id=ident,original_url=c['original_url'],final_url=c['final_url'],document_date=c['document_date'],version_label='Yayımlanan haberin özgün HTML baytları',accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime='text/html',sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'],date_precision='day',date_unknown_reason=None))
 add('archive_view',c['view'])
 add('passage',dict(id=ident+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section=title,pdf_page_index=None,printed_page=None))
 add('source_attribution',dict(version_id=v,kind='journalism',publisher=c['publisher'],author=author,social_handle=None,published_at=c['document_date'],date_precision='day',public_url=c['final_url'],basis='Haberin yayım tarihi, kaynak künyesi ve aktardığı tarafların sözleri okundu.'))
(checks/'followup-source-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries),ensure_ascii=False,indent=2)+'\n')
print('FOLLOWUP_SOURCE_SLICES_DRAFT',len(entries))
