"""Reflect merged findings in the inspected source list and limitations."""
import json
from pathlib import Path

p = Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-04-checks')
for name in ('kayseri', 'gaziantep', 'mugla'):
    r = json.loads((p/(name+'-review-draft.json')).read_text())
    for x in r['practice_source_review']:
        additions = []
        if x['subject_kind'] in ('practice_relation','practice_relation.explanation_finding_id') and x['subject_id']=='0404-kayseri-uyelik-relation':
            additions = [('0404-kayseri-kongre-v1','0404-kayseri-kongre-p','Kayserim, 17 Ekim, Gözbaşı açıklaması ve Ayan yanıtı')]
        elif x['subject_kind']=='practice_relation.explanation_finding_id' and x['subject_id']=='0404-gaziantep-disiplin-relation':
            additions = [('0404-gaziantep-ihrac-v1','0404-gaziantep-ihrac-p','Ayıntab 24 Ağustos, il yönetimine atfedilen açıklama')]
        elif x['subject_kind'] in ('practice_dispute','practice_dispute.summary_finding_id') and x['subject_id']=='0404-kayseri-kayit-dispute':
            additions = [('epm-charter-v1','0303-epm-uyelik-kabul-itiraz-p','Tüzük Madde 7(3), üyelik başvurusu')]
        elif x['subject_kind'] in ('practice_dispute','practice_dispute.summary_finding_id') and x['subject_id']=='0404-gaziantep-disiplin-dispute':
            additions = [('epm-charter-v1','0303-epm-fourth-disiplin-yetki-p','Tüzük Madde 43(3), disiplin yetkisi')]
        elif x['subject_kind'] in ('practice_dispute','practice_dispute.summary_finding_id') and x['subject_id']=='0404-mugla-dispute-id':
            additions = [('0105-speech-v1','0105-speech-p','Euronews 4 Ağustos, doğrudan başkan seçimi beyanı')]
        if additions:
            for k,i in [('source_version_ids',0),('passage_ids',1),('inspected_sections',2)]:
                values=json.loads(x[k]); values += [a[i] for a in additions if a[i] not in values]; x[k]=json.dumps(values,ensure_ascii=False)
            x['supported_claim'] += ' İlişki açıklaması, ihtilafın karşı kaynaklı özetiyle birlikte okunmuştur.'
            x['reason'] += ' İkinci haber ve birleştirilmiş özet ayrıca karşılaştırıldı.'
    (p/(name+'-review-draft-v4.json')).write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print('COMBINED_REVIEW',name,len(r['practice_source_review']))
