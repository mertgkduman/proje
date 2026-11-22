"""Hakkâri ön seçim kaynakları için kayıt taslağı."""
import json,sys
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text
root=Path('data/practices/sources/dem');checks=Path('.planning/phases/04-s-ylem-ve-belgelenmi-uygulamalar-n-kar-la-t-r-lmas/04-06-checks')
caps=json.loads((checks/'hakkari-rounds-captures.json').read_text());entries=[]
details={'hakkari_round1_alt':('Hakkâri ön seçimi ilk turu','Şükrü Çallı, 272 delegeden oy alırken, Mehmet Sıddık Akış 240 oy aldı.',None),'hakkari_round2':('Hakkâri ön seçimi ikinci turu','Bugün yapılan 2.tur seçimin sonucuna göre DEM Partisinin Hakkari belediye başkan adayları Sıddık Akış ve Viyan Tekçe seçildi.','Ulaş Güven'),'hakkari_speech':('Çallı seçim sonrası beyanı','Netice demokrasi ile taçlandı. Bugün 16 oy farkla Sıddık Akış arkadaşımız seçilmiştir.',None)}
def add(kind,values):entries.append(dict(kind=kind,values=values))
for c in caps:
 name=c['id'];title,exact,author=details[name];ident='0406-'+name.replace('_','-');v=ident+'-v1';assert exact in html_source_text((root/c['original_path']).read_bytes())
 add('document',dict(id=ident,party_id='dem',title=title,source_kind='journalism'))
 add('document_version',dict(id=v,document_id=ident,original_url=c['url'],final_url=c['url'],document_date=c['date'],version_label='Yayımlanan seçim haberi HTML',accessed_at=c['accessed_at'],verified_at=c['accessed_at'],mime='text/html',sha256=c['sha256'],original_path=c['original_path'],readable_path=c['readable_path'],date_precision='day',date_unknown_reason=None))
 add('archive_view',c['view'])
 add('passage',dict(id=ident+'-p',version_id=v,exact=exact,prefix=None,suffix=None,article=None,section=title,pdf_page_index=None,printed_page=None))
 add('source_attribution',dict(version_id=v,kind='journalism',publisher=c['publisher'],author=author,social_handle=None,published_at=c['date'],date_precision='day',public_url=c['url'],basis='Haberin yayın tarihi, yerel oylama bağlamı ve atfedilen açıklama incelendi.'))
(checks/'hakkari-rounds-source-slices-draft.json').write_text(json.dumps(dict(status='draft_unvalidated',source_root=str(root),entries=entries,limitation='16 oy farkı Çallı’ya aynı gün atfedilen sözdür; 24 Ocak beyanındaki 10 oy ile çelişir, kesin sayı ve usulsüzlük tutanakla doğrulanmadı.'),ensure_ascii=False,indent=2)+'\n')
print('HAKKARI_ROUNDS_DRAFT',len(entries))
