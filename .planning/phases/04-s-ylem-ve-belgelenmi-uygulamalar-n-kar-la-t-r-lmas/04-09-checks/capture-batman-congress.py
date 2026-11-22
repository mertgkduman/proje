from datetime import datetime,timezone
from hashlib import sha256
import html,json,re,sys
from pathlib import Path
from arsiv import html_source_text,pdf_page_text,readable_bytes
from arsiv_gorunum import build_view,validate_view

phase=Path(sys.argv[1])
stage=Path(sys.argv[2])
when=datetime.now(timezone.utc).isoformat()

cases={
 'dbp':('09',[
  ('dbp-batman-plan','html','DBP Batman İl Örgütü 2. Olağan Kongre duyurusunun haber kaydı','2026-09-17',None,'Batman Express',[
    ('planned','DBP Batman 2. Olağan Kongresinin duyurulan günü ve yeri','19 Eylül 2026 Cumartesi günü saat 13.00’te Roza Düğün Salonu’nda gerçekleştirilecek.',None),
  ]),
  ('dbp-batman-result','html','DBP Batman 2. Olağan Kongresi seçim sonucu','2026-09-20',None,'Batman Express',[
    ('venue','Gerçekleştiği bildirilen kongrenin yeri ve partinin temsili','Roza Düğün Salonu’nda düzenlenen kongreye DBP Eş Genel Başkanı Keskin Bayındır’ın yanı sıra',None),
    ('result','Tek listeyle seçilen DBP Batman İl Eş Başkanları','Tek listeyle gidilen kongrede yapılan seçim sonucunda DBP Batman İl Eş Başkanlığı’na Celile Yıldız ve Rıdvan Erzik seçildi.',None),
  ]),
  ('dbp-batman-duties','html','DBP Batman İl Eş Başkanlarının göreve başladığına ilişkin haber','2026-09-22',None,'Batman Burada',[
    ('duties','Seçilen eş başkanların göreve başladığına ilişkin haber','görevlerine başladı.',None),
    ('result','Parti il eş başkanlığına tek listeden seçilen iki isim','Tek listeyle yapılan seçimde Celile Yıldız ve Rıdvan Erzik, DBP Batman İl Eş Başkanlığı görevine seçildi.',None),
  ]),
 ]),
}
def archive(party,plan,sources):
 root=Path('data/practices/sources')/party
 entries,paths,receipts=[],set(),[]
 def add(table,**values):
  entries.append(dict(kind=table,values=values))
 def put(relative,content):
  dest=root/relative
  dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.exists():
   assert content==dest.read_bytes()
  else:
   dest.write_bytes(content)
  paths.add(str(dest))
  return dest
 for name,ext,title,docdate,author,publisher,snippets in sources:
  rec=json.loads((stage/(name+'.json')).read_bytes())
  receipts.append(rec)
  raw=Path(rec['path']).read_bytes()
  sha=sha256(raw).hexdigest()
  assert (sha,len(raw),rec['http_status'])==(rec['sha256'],rec['byte_count'],'200')
  slug=f'04{plan}-policy-{name}'
  vid=slug+'-v1'
  original=f'objects/{sha}/original.'+('html.bin' if ext=='html' else 'pdf')
  readable=f'objects/{sha}/readable.html'
  path=put(original,raw)
  put(readable,readable_bytes(raw,ext,legacy=False))
  url=rec['final_url']
  add('document',id=slug,party_id=party,title=title,source_kind='news')
  add('document_version',id=vid,document_id=slug,original_url=rec['url'],final_url=url,document_date=docdate,
      date_precision='day' if docdate else 'unknown',date_unknown_reason=None if docdate else 'TBMM kayıt sayfasının ilk yayım günü belirtilmiyor.',
      version_label='Erişilen özgün haber HTML’si.',accessed_at=rec['accessed_at'],verified_at=when,
      mime=rec['mime'].split(';')[0],sha256=sha,original_path=original,readable_path=readable)
  published=docdate
  add('source_attribution',version_id=vid,publisher=publisher,author=author,kind='journalism',published_at=published,
      date_precision='day' if published else 'unknown',social_handle=None,public_url=url,
      basis='Yayıncı, erişilen haber tarihi ve sayfa içinde gösterilen atıf denetlendi. Kullanıcı adı gerçek kişi kimliği olarak kullanılmadı.')
  if ext=='html':
   text=html_source_text(raw)
   cells=[x.strip() for x in re.findall(r'>([^<>]+)<',text) if x.strip()]
   view=build_view(raw,url,root,fetch_assets=False)
   view['version_id']=vid
   validate_view(root,view)
   add('archive_view',**view)
   manifest=root/view['manifest_path']
   paths.add(str(manifest))
   paths.update(str(manifest.parent/n) for n in json.loads(manifest.read_bytes())['files'])
  for key,section,marker,index in snippets:
   pid=slug+'-'+key
   manual=False
   if ext=='pdf':
    native=pdf_page_text(path,index)
    manual=not native.strip()
    assert manual or marker in native,(name,key,marker)
    exact=marker
   else:
    matches=[cell for cell in cells if marker.casefold() in html.unescape(cell).casefold() and len(cell)<1600]
    assert matches,(name,key,marker)
    exact=matches[0]
   add('passage',id=pid,version_id=vid,exact=exact,prefix=None,suffix=None,article=None,section=section,
       pdf_page_index=index,printed_page=None)
   if manual:
    add('manual_passage',passage_id=pid,checked_at=when,
        method='Poppler ile PDF’nin metin katmanı bulunmayan sayfası görsel olarak okundu.',
        reason='İmzalı metnin kaynak pasajı, bağlamı ve imza bölümü özgün sayfada denetlendi.')
 out=phase/f'04-{plan}-checks'/'batman-congress-source-records.json'
 with out.open('x') as f:
  f.write(json.dumps(dict(party_id=party,entries=entries,fetches=receipts+[json.loads((stage/'dbp-batman-date.json').read_bytes())]),ensure_ascii=False,indent=2)+'\n')
 Path(f'/tmp/gsd04{plan}-batman-congress-source-paths').write_text('\n'.join(sorted(paths))+'\n')
 print(party,len(entries),len(paths),sha256(out.read_bytes()).hexdigest())

for party,(plan,sources) in cases.items():
 archive(party,plan,sources)
