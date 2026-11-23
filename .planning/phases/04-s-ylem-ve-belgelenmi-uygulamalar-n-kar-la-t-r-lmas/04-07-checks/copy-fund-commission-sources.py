"""Retain the exact committee transcript and locate the documented article 4 amendment."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sys

from arsiv import pdf_page_text

checks, shared_checks = map(Path, sys.argv[1:])
original_id = '0404-fund-commission-5472'
local_id = '0407-fund-commission-5472'
source = json.loads((shared_checks/'fund-commission-source-records.json').read_bytes())
entries = []
for kind, key, ident in [('document','id',original_id),('document_version','id',original_id+'-v1'),
                         ('source_attribution','version_id',original_id+'-v1')]:
    values = next(e['values'].copy() for e in source['entries'] if e['kind']==kind and e['values'][key]==ident)
    values[key] = ident.replace(original_id, local_id)
    if kind=='document':
        values['party_id'] = 'iyi'
    elif kind=='document_version':
        values['document_id'] = local_id
        values['verified_at'] = datetime.now(timezone.utc).isoformat()
        version = values
    entries.append(dict(kind=kind, values=values))
source_root = Path('data/practices/sources/yeni-parti')
root = Path('data/practices/sources/iyi')
paths = []
for field in ('original_path','readable_path'):
    rel = Path(version[field]); raw = (source_root/rel).read_bytes(); target = root/rel
    if field=='original_path':
        assert sha256(raw).hexdigest()==version['sha256']
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        assert target.read_bytes()==raw
    else:
        target.write_bytes(raw)
    paths.append(str(target))
original = root/version['original_path']
quote = ('Bence bunlara bizim cebren gitmemiz lazım yani bunların bu kazançları -hani, bir emsal\n'
         'getiri hesap edilecek ya, onun üzerinde kalan kazançları- bu kanunun kapsamına girmeli')
anchors = (
    ('goal',58,'Genel görüşme, Usta’nın emsal üstü kazanç önerisi',quote),
    ('signers',82,'4. madde değişikliği, Taş ve Usta imzaları','Ayyüce Türkeş Taş\nAdana\nErhan Usta\nSamsun'),
    ('motion',82,'4. madde değişikliği, zorunlu iade hükmü','haksız kazançların iadesi zorunludur.'),
    ('scope',82,'Tasfiye kuruluşları veya TMSF dava yolu','veya TMSF tarafından genel hükümlere göre dava açılır'),
    ('reject',82,'Taş ve Usta önergesinin açıklama ve ret ilanı',
     'zorunluluk getirmeye yönelik bir önergedir.\nBAŞKAN MEHMET MUŞ - Önergeyi oylarınıza sunuyorum: Kabul edenler... Etmeyenler... Kabul edilmemiştir.'),
    ('voluntary',83,'Değişen 4. maddede gönüllü iade','ortalaması kıstelyevm usulü uygulanarak bulunacak tutarı aşan kısmı, Kurulca ilan edilen genel hisse iade hesabına isteğe bağlı\nolarak iade edilebilir.'),
    ('article',83,'Değişen 4. maddenin kabul ilanı',"4'üncü madde\nkabul edilmiştir."),
)
for suffix, index, section, exact in anchors:
    assert exact in pdf_page_text(original,index),suffix
    entries.append(dict(kind='passage',values=dict(id=f'{local_id}-{suffix}',version_id=version['id'],
        exact=exact,prefix=None,suffix=None,article='4' if suffix!='goal' else None,
        section=section,pdf_page_index=index,printed_page=str(index+1))))
out = checks/'fund-commission-art4-source-records.json'
with out.open('x') as handle:
    handle.write(json.dumps(dict(party_id='iyi',entries=entries),ensure_ascii=False,indent=2)+'\n')
Path('/tmp/gsd0407-commission-art4-paths').write_text('\n'.join(paths)+'\n')
print(len(entries),len(paths),sha256(out.read_bytes()).hexdigest())
