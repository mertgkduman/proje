import hashlib, json, sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import pdf_page_text, readable_bytes

root=Path('data/practices/sources/tip'); out=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-05-checks')
sources=[
 dict(id='0405-tip-sendika-274390-pdf',sha='c679a7e811b5815bb95508e5dd11952768209064d89f8883b30540c93fb2f58c',url='https://cdn.tbmm.gov.tr/KKBSPublicFile/D27/Y5/T2/WebOnergeMetni/9c60b46f-6665-479a-aa0f-9025c059f4e9.pdf',date='2022-04-12',accessed='2026-11-22T03:17:26+00:00',title='27. dönem 2/4390 sendika kanun teklifi',passages=[('intro',0,'Sendikalar Ve Toplu İş Sözleşmesi Kanununda Değişiklik Yapılmasına Dair Kanun Teklifi','Başkanlığa teklif'),('identity',0,'Erkan Baş\nTİP Genel Başkanı\nİstanbul Milletvekili','İlk imza ve unvan'),('provision',6,'Sigortasız çalıştırılan işçiler de, e-Devlet kapısı üzerinden beyana dayalı olarak sendika üyelik\nbaşvurusunda bulunabilir.','Madde 1')]),
 dict(id='0405-tip-sendika-hukumsuz',sha='ba2883e38fed0a4a930fb66c3d51b7e72248196ebffb8df52e6688fef57a75ed',url='https://www5.tbmm.gov.tr/tutanaklar/TUTANAK/TBMM/d28/c001/tbmm28001001.pdf',date='2023-06-02',accessed='2026-11-22T03:27:42+00:00',title='28. dönem ilk birleşim hükümsüz milletvekili teklifleri',passages=[('lapsed',232,'4115 2/4390 Sendikalar ve Toplu İş Sözleşmesi Kanununda Değişiklik Yapılmasına Dair Kanun Teklifi\n(Türkiye İşçi Partisi Genel Başkanı İstanbul Milletvekili Erkan Baş ve 3 Milletvekili)','Hükümsüz sayılan teklifler sıra 4115')])]
entries=[]
for s in sources:
 path=root/'objects'/s['sha']/'original.pdf'; raw=path.read_bytes(); assert hashlib.sha256(raw).hexdigest()==s['sha']
 readable=path.parent/'readable.html'; content=readable_bytes(raw,'pdf',legacy=False)
 if readable.exists(): assert readable.read_bytes()==content
 else: readable.write_bytes(content)
 def add(k,v):entries.append(dict(kind=k,values=v))
 vid=s['id']+'-v1'; add('document',dict(id=s['id'],party_id='tip',title=s['title'],source_kind='official'))
 add('document_version',dict(id=vid,document_id=s['id'],original_url=s['url'],final_url=s['url'],document_date=s['date'],version_label='TBMM özgün belgesi',accessed_at=s['accessed'],verified_at=s['accessed'],mime='application/pdf',sha256=s['sha'],original_path=f"objects/{s['sha']}/original.pdf",readable_path=f"objects/{s['sha']}/readable.html",date_precision='day',date_unknown_reason=None))
 add('source_attribution',dict(version_id=vid,kind='official',publisher='Türkiye Büyük Millet Meclisi',author=None,social_handle=None,published_at=None,date_precision='unknown',public_url=s['url'],basis='TBMM özgün belge başlığı ve ilgili sayfa incelendi.'))
 for name,page,exact,section in s['passages']:
  assert exact in pdf_page_text(path,page),(s['id'],name)
  add('passage',dict(id=s['id']+'-'+name+'-p',version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,pdf_page_index=page,printed_page='200' if name=='lapsed' else None))
(out/'union-sources-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',entries=entries),ensure_ascii=False,indent=2)+'\n')
print('DRAFT ONLY',len(entries))
