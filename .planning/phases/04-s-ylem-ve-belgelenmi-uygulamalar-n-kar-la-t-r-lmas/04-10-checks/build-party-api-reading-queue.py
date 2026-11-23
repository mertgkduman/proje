import datetime, hashlib, json
from pathlib import Path

D=Path(__file__).parent
pages=D/'party-api-pages'
paths=sorted(pages.glob('page-*.json'))
assert len(paths)==33
cutoff=datetime.datetime.fromisoformat('2026-11-10T14:38:46.154751+00:00')
items=[]; pages_info=[]; seen=set()
for path in paths:
 raw=path.read_bytes(); data=json.loads(raw)
 assert isinstance(data,list) and len(data)<=100
 pages_info.append(dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),count=len(data)))
 for post in data:
  assert post['id'] not in seen
  seen.add(post['id'])
  dt=datetime.datetime.fromisoformat(post['date_gmt']).replace(tzinfo=datetime.timezone.utc)
  assert dt<=cutoff
  mod=datetime.datetime.fromisoformat(post['modified_gmt']).replace(tzinfo=datetime.timezone.utc)
  body=post['content']['rendered']
  items.append(dict(id=post['id'],url=post['link'],date=post['date'],date_gmt=post['date_gmt'],modified_gmt=post['modified_gmt'],body_temporal_status='modified_after_cutoff' if mod>cutoff else 'last_modified_at_or_before_cutoff',title=post['title']['rendered'],page=str(path),body_sha256=hashlib.sha256(body.encode()).hexdigest(),body_characters=len(body)))
assert len(items)==3270
catalog=dict(captured_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),endpoint='https://www.emep.org/wp-json/wp/v2/posts',query='per_page=100; before=2026-11-10T17:38:46 (site local time); id,date,date_gmt,modified,modified_gmt,link,title,content',cutoff=cutoff.isoformat(),scope_note='Bu API listesindeki oluşturulma/yayın alanı ve güncelleme alanı ayrıdır. Aynı saniyenin kesirli sınırında before sorgusunun dışladığı olası kayıtlar ayrıca kontrol edilmeli; cutoff sonrası değiştirilmiş gövdenin cutoff öncesi sürümü varsayılamaz. API gövdesi okundu sayılmaz, orijinal makale arşivi değildir.',post_count=len(items),pages=pages_info,posts=items)
tranches=[]; current=[]; used=0
for item in items:
 n=item['body_characters']; start=0
 while start<n:
  room=48000-used
  if room==0:
   tranches.append(dict(tranche_id='0410-emep-api-%03d'%(len(tranches)+1),state='pending',parts=current));current=[];used=0;room=48000
  end=min(n,start+room)
  current.append(dict(post_id=item['id'],url=item['url'],page=item['page'],body_sha256=item['body_sha256'],start_char=start,end_char=end,body_temporal_status=item['body_temporal_status']))
  used+=end-start;start=end
if current:tranches.append(dict(tranche_id='0410-emep-api-%03d'%(len(tranches)+1),state='pending',parts=current))
queue=dict(created_at=catalog['captured_at'],method='API HTML body character aralıkları 48000 karakterlik üst sınırlarla gruplanır; bu mekanik iş sırası kanıt, insan okuması veya kapanış sayısı değildir.',cutoff=catalog['cutoff'],tranche_count=len(tranches),tranches=tranches)
for name,obj in [('party-api-catalog.json',catalog),('party-api-reading-queue.json',queue)]:
 out=D/name;assert not out.exists();out.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
print('API_CATALOG',len(items),'PAGES',len(paths),'AFTER_CUTOFF_MODIFIED',sum(x['body_temporal_status']=='modified_after_cutoff' for x in items),'TRANCHES',len(tranches))
