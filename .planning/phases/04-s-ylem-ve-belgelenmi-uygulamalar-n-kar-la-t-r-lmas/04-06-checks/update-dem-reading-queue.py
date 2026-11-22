"""Yalnız biten okuma dilimlerini ve açık kalan araştırma uçlarını kaydet."""
import json
from pathlib import Path
path = Path('data/practices/04-dem-tranches.json')
data = json.loads(path.read_text())
assert data['status'] == 'pending' and not data['tranches']
lead = {x['id']: x for x in data['candidate_leads']}
lead['tbmm-10-1831']['reason'] = 'Özgün PDF yakalandı ve 189–191 indeksli önerge eki görsel okundu; son rapor ve muhalefet şerhleri açık.'
lead['tbmm-2024-101831']['reason'] = 'Önerge, ortak komisyon ve tartışma okundu; taranmış önerge eki görsel okundu; komisyon son raporu ve şerhler açık.'
data['candidate_leads'].append({'id':'tbmm-2026-3961','url':'https://cdn.tbmm.gov.tr/TbmmWeb/Tutanak/28/5/14/Ham/7a9ec4d0-5611-415d-a3f5-6c7d1677d672.html','state':'pending','reason':'DEM grup konuşması, iki bireysel oy ve komisyonun DEM şerhi okundu; diğer bağlam, kapsam eşleşmesi ve kapılar açık.'})
data['tranches'] = [
 {'source_sha256':'3561d414c56eb9e903bb2cb3b256e879328b02ab6ca3527b87919f928dba4413','scope':'Parti sitesindeki kongre kararları, page-content metni','character_start':0,'character_end_exclusive':42000,'status':'read','evidence':'.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks/kongre-kararlari-kismi-okuma.md'},
 {'source_sha256':'3561d414c56eb9e903bb2cb3b256e879328b02ab6ca3527b87919f928dba4413','scope':'Parti sitesindeki kongre kararları, page-content metni','character_start':42000,'character_end_exclusive':87390,'status':'read','evidence':'.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks/kongre-kararlari-kismi-okuma.md'}
]
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('QUEUE_UPDATED_WITHOUT_CLOSURE', len(data['cells']), len(data['source_queue']), len(data['candidate_leads']))
