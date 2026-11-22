"""Mekke görüşmesi ve isimli oy için özgün kaynak pasajı taslağı."""
import json, sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
root=Path('data/practices/sources/dem')
checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
load=lambda name:json.loads((checks/name).read_text())
main=load('tbmm-2026-3961-capture.json'); news=load('tbmm-2026-3961-news-capture.json'); vote=next(x for x in load('tbmm-2026-3961-followup-captures.json') if x['id']=='vote')
vote['document_date']='2026-11-05'
vote_raw=(root/vote['original_path']).read_bytes().decode('utf-8',errors='replace')
pos=vote_raw.index('TEMELL&#x130;</td>'); start=vote_raw.rfind('<td>MU&#x15E;',0,pos); end=vote_raw.index('</tr>',pos)+len('</tr>')
items=[
 ('0406-tbmm-2026-3961','5 Kasım 2026 TBMM 14. birleşim tutanağı',main,'Biz DEM PARTİ olarak savaşa karşıyız, her türlü bu türden anlaşmalara da karşıyız ama bu anlaşmaya 2 defa karşıyız çünkü biz hem NATO\'ya karşıyız hem NATO\'nun taşeron anlaşmalarına da karşıyız.','Sezai Temelli DEM grubu konuşması'),
 ('0406-tbmm-2026-3961-news','4 Kasım 2026 TBMM görüşme haberi',news,"DEM Parti Diyarbakır Milletvekili Ceylan Akça Cupolo, Anlaşma'yı eleştirdi.</p><p>Anlaşma'ya karşı olduklarını söyleyen Cupolo, Anlaşma'nın Türkiye'yi daha çok çatışmanın içerisine çekeceğini iddia etti.",'Akça Cupolo görüşünün TBMM haberinde aktarımı'),
 ('0406-tbmm-2026-3961-vote','5 Kasım 2026 TBMM kesin açık oylama cetveli',vote,vote_raw[start:end],'Temelli isimli kesin oy satırı')]
entries=[]
def add(k,v):entries.append(dict(kind=k,values=v))
for ident,title,c,exact,section in items:
 raw=(root/c['original_path']).read_bytes(); assert exact in html_source_text(raw),(ident,section)
 v=ident+'-v1'; view=dict(c['view']);view['version_id']=v
 add('document',dict(id=ident,party_id='dem',title=title,source_kind='official'))
 add('document_version',dict(id=v,document_id=ident,original_url=c['original_url'],final_url=c['final_url'],document_date=c['document_date'],version_label=title,accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime='text/html',sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'],date_precision='day',date_unknown_reason=None))
 add('archive_view',view)
 add('passage',dict(id=ident+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
 add('source_attribution',dict(version_id=v,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=c['document_date'],date_precision='day',public_url=c['final_url'],basis='Resmî tutanak, haber veya kesin cetvelin ilgili bölümü ve bağlamı okundu.'))
for ident,version,exact,section in [
 ('0406-2026-3961-speaker-p','0406-tbmm-2026-3961-v1','DEM PARTİ GRUBU ADINA SEZAİ TEMELLİ (Muş)','DEM grubu konuşmacısının kimliği'),
 ('0406-2026-3961-accept-p','0406-tbmm-2026-3961-vote-v1','Kabul Edenler </td>\n                                    <td align="left">:&nbsp;277','Kesin cetvel kabul toplamı'),
 ('0406-2026-3961-reject-p','0406-tbmm-2026-3961-vote-v1','Reddedenler </td>\n                                    <td align="left">:&nbsp;118','Kesin cetvel ret toplamı')]:
 c=main if version=='0406-tbmm-2026-3961-v1' else vote
 assert exact in html_source_text((root/c['original_path']).read_bytes()),ident
 add('passage',dict(id=ident,version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
(checks/'2026-3961-source-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries,source_root=str(root),limitations='Komisyon şerhinin görsel okuması bu makine pasajlarına dahil değildir; 4 Kasım tam tutanağı hâlâ açık.'),ensure_ascii=False,indent=2)+'\n')
print('3961_SOURCE_SLICES_DRAFT',len(entries))
