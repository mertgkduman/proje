"""İki dar kaynak zinciri: yalnız taslak, kapsam kapanışı değildir."""
import json
import sys
from pathlib import Path

sys.path.insert(0, 'src')
from arsiv import pdf_page_text
from uygulamalar import _digest

checks = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
capture = json.loads((checks / 'capture-followup.json').read_text())['tbmm-2159-pdf-curl']
entries = json.loads((checks / 'bianet-source-draft.json').read_text())['entries']
def add(record_kind, **values):
    entries.append(dict(kind=record_kind, values=values))

digest = capture['sha256']
pdf = Path(capture['original_path']).resolve()
page0 = pdf_page_text(str(pdf), 0)
page7 = pdf_page_text(str(pdf), 7)
exact0 = 'Engellilerin İstihdam ve Temel Yurttaşlık Geliri Haklarına İlişkin Çeşitli Kanunlarda\nDeğişiklik Yapılmasına Dair Kanun Teklifimiz gerekçesiyle birlikte ekte sunulmuştur.'
exact7 = 'içinde bulunulan yıl için tespit edilen net asgari ücret oranına eşit olacak\nşekilde'
assert exact0 in page0 and exact7 in page7
add('document', id='0406-tbmm-2159', party_id='dem', title='Engellilerin İstihdam ve Temel Yurttaşlık Geliri Haklarına İlişkin Kanun Teklifi (2/2159)', source_kind='official')
add('document_version', id='0406-tbmm-2159-v1', document_id='0406-tbmm-2159', original_url=capture['original_url'], final_url=capture['final_url'], document_date='2024-05-14', version_label='TBMM Başkanlığına sunulan teklif', accessed_at=capture['accessed_at'], verified_at=capture['verified_at'], mime='application/pdf', sha256=digest, original_path='objects/'+digest+'/original.pdf', readable_path='objects/'+digest+'/readable.html', date_precision='day', date_unknown_reason=None)
for ident, exact, page, section in [('0406-2159-submission-p',exact0,0,'Başkanlığa sunuş'),('0406-2159-article1-p',exact7,7,'Teklif madde 1')]:
    add('passage', id=ident, version_id='0406-tbmm-2159-v1', exact=exact, prefix=None, suffix=None, article=None, section=section, pdf_page_index=page, printed_page=None)
add('source_attribution', version_id='0406-tbmm-2159-v1', kind='official', publisher='Türkiye Büyük Millet Meclisi', author=None, social_handle=None, published_at='2024-05-14', date_precision='day', public_url=capture['original_url'], basis='TBMM kaşeli teklif ve grup başkanvekilleri imza sayfası incelendi.')
add('actor', id='0406-dem-institution', kind='institution', party_id='dem', person_id=None, authorization_passage_id=None)
now=capture['accessed_at']
for fid, passage in [('0314-v4-dem-s','0314-dem-cochair-selection-rounds-full-p'),('0314-v4-dem-q','0314-dem-cochair-selection-rounds-full-p'),('03-v2-dem-temel-yurttaslik-geliri-summary','03-dem-gelir'),('03-v2-dem-temel-yurttaslik-geliri-quote','03-dem-gelir')]:
    add('verification',finding_id=fid,passage_id=passage,checked_at=now,result='confirmed',reason='Faz 3 pasajı, kayıtlı özgün metin ve kapsam yeniden karşılaştırıldı; yürürlük ve belge kökeni belirsizliği korunur.')
for passage in ('0305-dem-baskan-secim-also-organ-secim-yontemi-dem-passage','0305-dem-baskan-secim-dem-passage','0305-dem-baskan-secim-to-es-genel-baskan-dem-passage'):
    add('verification',finding_id='0314-v4-dem-s',passage_id=passage,checked_at=now,result='confirmed',reason='Aynı tüzükteki kısa eş genel başkan seçim pasajı tam maddeyle karşılaştırıldı; tarihsel yürürlük belirlenmedi.')
def finding(ident, text, passages):
    add('finding',id=ident,party_id='dem',heading='Söylem ve uygulama',pair_id=ident,text=text,provenance='summary',epistemic_type='claim')
    for passage in passages:
        add('finding_evidence',finding_id=ident,passage_id=passage,role='support')
        add('verification',finding_id=ident,passage_id=passage,checked_at=now,result='confirmed',reason='Belirtilen kaynak pasajı ve kapsamı incelendi; kanıtın sınırı korundu.')
    add('review',id='review-'+ident,kind='finding',subject_id=ident,reviewer_kind='agent',reviewed_at=now,result='reviewed',reason='Kaynak pasajları ve olay/ifade sınırı karşılaştırıldı.')
finding('0406-congress-result','BİA Haber Merkezi, Yeşil Sol Parti kongresinde Tülay Hatimoğulları ve Tuncer Bakırhan’ın eş genel başkanlığa getirildiğini bildirdi.',['0406-bianet-congress-p'])
finding('0406-congress-link','Eş genel başkanların belirlenmesi tüzükte düzenlenen makamla ilgilidir; seçimin usulü ve tüzük nüshasının olay tarihindeki yürürlüğü bu haberle doğrulanmaz.',['0406-bianet-congress-p','0314-dem-cochair-selection-rounds-full-p'])
finding('0406-2159-event','DEM Parti grup başkanvekilleri engellilerin istihdamı ve temel yurttaşlık geliri hakkında 2/2159 sayılı kanun teklifini TBMM’ye sundu.',['0406-2159-submission-p'])
finding('0406-2159-link','Kongre ekindeki gelirsiz yurttaşlara gelir hedefi ile engelli aylıklarını düzenleyen teklif aynı gelir güvencesi konusundadır; yararlanıcı kapsamları farklıdır ve teklifin yasalaştığı gösterilmemiştir.',['03-dem-gelir','0406-2159-submission-p','0406-2159-article1-p'])
pkg=json.loads(Path('data/practices/04-coverage-tracer.json').read_text())
pkg['party_id']='dem';pkg['entries']=entries;pkg['scope_inventory']=[];pkg['tranches']=[];pkg['source_review_refs']=[]
pr=pkg['practice_records']
for k in pr:
    if k not in ('practice_contract','practice_coverage_contract'): pr[k]=[]
pr['practice_scope_v2']=[dict(id='practice-a433ea5fa3150ee0f0b832989d2c0ca7c9ff2925ed20fec91567a684719d2d83',party_id='dem',topic_id='organ-secim-yontemi',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='2023 kongresi dar aday zinciri; kapsam araştırması sürüyor.'),dict(id='practice-dc586aedd6823cc75eed15c27730c61cb76b7188c1144547f739f0c8edb96f4d',party_id='dem',topic_id='temel-yurttaslik-geliri',taxonomy_version=4,period_start='2012-11-30',cutoff_at='2026-11-10T14:38:46.154751+00:00',research_kind='event',boundary_reason='Yalnız 2/2159 teklif girişimi; kapsam araştırması sürüyor.')]
pr['practice_event']=[dict(id='0406-2023-congress',common_event_key='yesil-sol-2023-10-15-kongre',event_at='2023-10-15',date_precision='day',date_unknown_reason=None,scope_context='Ankara Yeşil Sol Parti kongresi',title='Kongrede eş genel başkanların belirlenmesi',occurrence_basis='BİA haberi iki ismi ve kongre bağlamını bildirir; oy tutanağını sunmaz.'),dict(id='0406-2159',common_event_key='tbmm-28-2-2159',event_at='2024-05-14',date_precision='day',date_unknown_reason=None,scope_context='TBMM 28. dönem, 2/2159 teklif sunuşu',title='Engelli aylıkları ve istihdamı teklifi',occurrence_basis='TBMM kaşeli teklif ve grup başkanvekillerinin imzaları.')]
pr['practice_event_evidence']=[dict(event_id='0406-2023-congress',passage_id='0406-bianet-congress-p',supported_point='İki ismin eş genel başkanlığa getirilmesi',stage='result',concrete_basis='Haber tarih, kongre ve iki ismi açıkça bildirir.',limitation='Haber oy sayısı ve seçim tutanağını sunmaz.',epistemic_type='claim'),dict(event_id='0406-2159',passage_id='0406-2159-submission-p',supported_point='Teklifin TBMM Başkanlığına sunulması',stage='initiative',concrete_basis='Grup başkanvekilleri imzalı ve TBMM kayıt kaşeli teklif.',limitation='Sunulan teklif yasalaşma veya uygulama sonucu değildir.',epistemic_type='claim')]
pr['practice_contribution']=[dict(id='0406-congress-contribution',event_id='0406-2023-congress',party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id='0406-congress-result',authority_passage_id=None,membership_passage_id=None,responsibility_limit='Yalnız belirtilen kongre ve haberin bildirdiği görev değişikliği.'),dict(id='0406-2159-contribution',event_id='0406-2159',party_id='dem',actor_id='0406-dem-institution',contribution_kind='task',finding_id='0406-2159-event',authority_passage_id=None,membership_passage_id=None,responsibility_limit='DEM grup başkanvekillerinin teklif sunma yetkisi; yasama sonucu Meclise aittir.')]
pr['practice_statement']=[dict(id='0406-charter-statement',party_id='dem',topic_id='organ-secim-yontemi',taxonomy_version=4,summary_finding_id='0314-v4-dem-s',quote_finding_id='0314-v4-dem-q',statement_at=None,date_precision='unknown',version_id='0204-dem-charter-v1',period_basis='DEM kısa adlı tüzük nüshası; kabul ve yürürlük tarihi bilinmiyor.',uncertainty_reason='Nüshanın 2023 kongresinde yürürlükte olduğu doğrulanmadı.',comparison_row_id='0314-v4-fix-dem-3'),dict(id='0406-income-statement',party_id='dem',topic_id='temel-yurttaslik-geliri',taxonomy_version=4,summary_finding_id='03-v2-dem-temel-yurttaslik-geliri-summary',quote_finding_id='03-v2-dem-temel-yurttaslik-geliri-quote',statement_at=None,date_precision='unknown',version_id='0204-dem-policies-v1',period_basis='Kongre kararları eki; tam program değildir.',uncertainty_reason='Belge tarihi ve kongre kökeni ayrıca doğrulanıyor.',comparison_row_id='04-03-v3-03-v2-dem-temel-yurttaslik-geliri')]
pr['practice_relation']=[dict(id='0406-congress-relation',statement_id='0406-charter-statement',event_id='0406-2023-congress',party_id='dem',topic_id='organ-secim-yontemi',scope_id='practice-a433ea5fa3150ee0f0b832989d2c0ca7c9ff2925ed20fec91567a684719d2d83',comparability_reason='Her iki kayıt eş genel başkanların belirlenmesiyle ilgilidir; uygulanan seçim usulü bilinmiyor.',target_finding_id='0314-v4-dem-s',result_finding_id='0406-congress-result',explanation_finding_id='0406-congress-link',temporal_context='Kongre 2023; nüshanın yürürlük tarihi belirlenmedi.',authority_context='Büyük kongre ve delegelerin seçimi tüzükte düzenlenir.',uncertainty_reason='Haber oy tutanağını ve tüzük nüshasının tarihsel yürürlüğünü kanıtlamıyor.'),dict(id='0406-2159-relation',statement_id='0406-income-statement',event_id='0406-2159',party_id='dem',topic_id='temel-yurttaslik-geliri',scope_id='practice-dc586aedd6823cc75eed15c27730c61cb76b7188c1144547f739f0c8edb96f4d',comparability_reason='Her iki kayıt gelir desteğiyle ilgilidir; genel hedef ve engelli aylıkları ayrı kapsamlardır.',target_finding_id='03-v2-dem-temel-yurttaslik-geliri-summary',result_finding_id='0406-2159-event',explanation_finding_id='0406-2159-link',temporal_context='Teklif 14 Mayıs 2024; kongre eki tarihi kesinleştirilmedi.',authority_context='İki grup başkanvekili teklif sunar; Meclisin yasama yetkisi ayrıdır.',uncertainty_reason='Teklifin yasama sonucu ve metnin dönemsel önceliği burada doğrulanmadı.')]
pkg['scope_inventory']=json.loads(Path('data/practices/04-coverage-tracer.json').read_text())['scope_inventory']
pr['practice_contract'][0]['inventory_digest']=_digest(pkg['scope_inventory'])
(checks/'package-tracer-draft.json').write_text(json.dumps(pkg,ensure_ascii=False,indent=2)+'\n')
print('DRAFT_ONLY entries',len(entries),'events',len(pr['practice_event']))
