import json, hashlib
from datetime import datetime, timezone
from pathlib import Path
import sys
sys.path.insert(0,'src')
from arsiv import html_source_text
from uygulamalar import _digest

checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
receipt=json.loads((checks/'2121-detail-capture.json').read_text()); digest=receipt['sha256']; url=receipt['url']; now=datetime.now(timezone.utc).isoformat()
raw=Path(f'data/practices/sources/tip/objects/{digest}/original.html.bin').read_bytes(); text=html_source_text(raw)
summary=text[text.index('Teklif ile;'):text.index('</td>',text.index('Teklif ile;'))]
assert '2 / 2121' in text and '24/04/2024' in text and 'KOM&#x130;SYONDA' in text
version='0405-tip-282121-v1'; doc='0405-tip-282121'; passage=doc+'-summary-p'; datep=doc+'-date-p'; statep=doc+'-status-p'
entries=[]
def add(k,v): entries.append(dict(kind=k,values=v))
add('document',dict(id=doc,party_id='tip',title='28. dönem 2/2121 çalışma süresi teklifi',source_kind='official'))
add('document_version',dict(id=version,document_id=doc,original_url=url,final_url=receipt['final_url'],document_date=None,version_label='TBMM dinamik teklif kaydı',accessed_at=receipt['accessed_at'],verified_at=receipt['accessed_at'],mime='text/html',sha256=digest,original_path=f'objects/{digest}/original.html.bin',readable_path=f'objects/{digest}/readable.html',date_precision='unknown',date_unknown_reason='Kayıt sayfasının yayın tarihi belirtilmez; geliş tarihi ayrı pasajdır.'))
add('archive_view',receipt['view'])
for pid,exact,section in [(passage,summary,'Teklif özeti'),(datep,'24/04/2024','Başkanlığa geliş tarihi'),(statep,'KOM&#x130;SYONDA','Erişim anında son durum')]:
 add('passage',dict(id=pid,version_id=version,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=None,printed_page=None))
add('source_attribution',dict(version_id=version,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=url,basis='TBMM 28. dönem teklif kayıt künyesi ve giriş tarihi okundu.'))
fid='0405-calisma-2121-iliski'; program='0304-tip-program-emek-talepleri-p1'
add('finding',dict(id=fid,party_id='tip',heading='Söylem ve uygulama',pair_id=fid,text='Program çalışma saatleri taleplerini sosyalizm mücadelesiyle ilişkilendirir. Erkan Baş’ın 2024 tarihli teklifi haftalık çalışma süresinin genel olarak 35 saate indirilmesini önerir; teklifin verilmesi hedefin gerçekleştiğini göstermez.',provenance='summary',epistemic_type='claim'))
for pid in [program,passage,datep]:
 add('finding_evidence',dict(finding_id=fid,passage_id=pid,role='support'))
 add('verification',dict(finding_id=fid,passage_id=pid,checked_at=now,result='confirmed',reason='Program ve 28. dönem TBMM kayıt kapsamı karşılaştırıldı; gerçekleşme çıkarılmadı.'))
add('review',dict(id='review-'+fid,kind='finding',subject_id=fid,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Programdaki genel talep ile somut teklifin farklı kapsamı ve dönem belirsizliği incelendi.'))
e='0405-tip-282121-event'; s='0405-tip-calisma-statement'; rel='0405-tip-282121-relation'
records={
 'practice_contract':[dict(version=1,taxonomy_version=4,stage='partial',method_version=1,inventory_digest=_digest([]))],
 'practice_event':[dict(id=e,common_event_key='tbmm-28-2-2121',event_at='2024-04-24',date_precision='day',date_unknown_reason=None,scope_context='28. dönem TBMM çalışma süresi kanun teklifi',title='Haftalık çalışma süresi teklifi',occurrence_basis='TBMM teklif kayıt özeti ve geliş tarihi.')],
 'practice_event_evidence':[dict(event_id=e,passage_id=passage,supported_point='35 saat ve diğer çalışma koşulları teklif edildi',stage='initiative',concrete_basis='TBMM teklif kayıt özeti',limitation='Teklif kanunlaşma veya hedefin gerçekleşmesi değildir.',epistemic_type='claim')],
 'practice_evidence_assessment':[dict(event_id=e,passage_id=passage,stage='initiative',basis_kind='document')],
 'practice_statement':[dict(id=s,party_id='tip',topic_id='calisma-sureleri',taxonomy_version=4,summary_finding_id='0304-tip-program-emek-talepleri-summary',quote_finding_id='0304-tip-program-emek-talepleri-quote',statement_at=None,date_precision='unknown',version_id='0203-tip-program-v1',period_basis='Faz 3 seçili program yakalaması.',uncertainty_reason='Programın kabul ve yürürlük tarihi bilinmiyor; teklif öncesi geçerlilik varsayılmaz.',comparison_row_id='04-03-v3-0304-tip-program-emek-talepleri-row')],
 'practice_relation':[dict(id=rel,statement_id=s,event_id=e,party_id='tip',topic_id='calisma-sureleri',scope_id=None,comparability_reason='İkisi çalışma saatleriyle ilgilidir; program saat sayısı belirlemez.',target_finding_id='0304-tip-program-emek-talepleri-summary',result_finding_id=None,explanation_finding_id=fid,temporal_context='Teklif 24 Nisan 2024; programın tarihsel yürürlük zamanı belirsiz.',authority_context='Teklif milletvekili girişimidir; yasa yapma yetkisi TBMM bütünündedir.',uncertainty_reason='Programın o tarihteki sürümü ve teklifin kesim anındaki durumu ayrıca doğrulanmalıdır.')]
}
base=json.loads(Path('data/practices/04-yeni-parti.json').read_text())
records['practice_coverage_contract']=base['practice_records']['practice_coverage_contract']
payload=dict(contract_version=1,base_release='f67ca0a35e634035bf3aa83a46571f50',party_id='tip',taxonomy_version=4,stage='partial',entries=entries,practice_records=records,scope_inventory=[],tranches=[],source_review_refs=[])
(checks/'policy-tracer-draft.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
print('DRAFT ONLY',len(entries))
