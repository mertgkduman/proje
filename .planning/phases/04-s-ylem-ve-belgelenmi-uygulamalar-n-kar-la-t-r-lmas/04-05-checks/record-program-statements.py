import json,sys
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,'src')
from arsiv import html_source_text

comparison=json.loads(Path('data/comparisons/03-tip-program.json').read_text())['records']
source=html_source_text(Path('data/objects/6aa8a0087e2426e808defbc8e427281f08862b1206fdad2ae847fd294854c7e0/original.html.bin').read_bytes())
topics={
 'inanc-mezhep-esitligi':(['0304-tip-program-inanc-p1','0304-tip-program-inanc-p2'],'Program Alevilerin eşit yurttaşlığı, zorunlu din dersleri ve Diyanet yanında, din işlerinin tüm din ve mezheplere eşit mesafeli bir kurumda yeniden düzenlenmesini de içerir.'),
 'anadilde-egitim':(['0304-tip-program-egitim-dil-p1'],'Program her düzeyde nitelikli, parasız, anadilde, laik ve bilimsel eğitim hakkını savunur.'),
 'tarim-hayvancilik':(['0304-tip-program-tarim-p1'],'Program tohum üretim merkezleri, kooperatif taban fiyatı, mera koruması ve yerli hayvancılık desteğini birlikte önerir.'),
 'din-egitimi':(['0304-tip-program-din-ders-p1'],'Program zorunlu din derslerinin kaldırılmasını savunur; bütün din eğitimine genel yasak çıkarılmaz.'),
 'tarimsal-fiyatlar':(['0304-tip-program-fiyat-p1'],'Program taban fiyatlarının hasattan önce, üretici lehine ve üretici kooperatiflerince belirlenmesini önerir.'),
 'alevi-inanc-orgutlenmesi':(['0304-tip-program-alevi-p1'],'Program Alevilerin eşit yurttaşlık mücadelesini destekler; incelenen programda inanç kurumlarının hukuki statüsüne ayrı açık düzenleme saptanmamıştır. Bu tek belge bütün diğer söylemler için yokluk değildir.'),
 'nato-iliskileri':(['0304-tip-program-nato-p1'],'Program NATO dahil emperyalist olarak nitelediği kurumlara ve Türkiye’nin bu kuruluşlarla ilişkilerine karşı mücadele edeceğini belirtir.'),
 'yabanci-askeri-usler':(['0304-tip-program-yabanci-us-p1'],'Program İncirlik ve Kürecik dahil Türkiye’deki yabancı askerî üslere karşı mücadele edeceğini belirtir.'),
 'sagliga-erisim':(['0304-tip-program-saglik-p1'],'Program herkese ücretsiz, ulaşılabilir ve anadilde sağlık hizmetini ve koruyucu hekimliği savunur; sağlık ocakları ve hastaneler kurulması için çaba söyler.'),
 'toplumsal-cinsiyet':(['0304-tip-program-kadin-p1','0304-tip-program-kadin-p2'],'Program kadınların ataerki ve sermaye egemenliğine karşı mücadelesini destekler; incelenen bölüm belirli bir şiddet başvuru kurumu tanımlamaz.'),
 'cocuk-haklari':(['0304-tip-program-cocuk-p1','0304-tip-program-cocuk-p2'],'Program 18 yaş altını çocuk sayar ve çocukların çeşitli hakları ile şiddet ve sömürüden korunması için mücadeleyi anlatır.'),
 'temiz-enerji-gecisi':(['0304-tip-program-enerji-p1'],'Program temiz ve yenilenebilir enerji kaynaklarının planlı kullanımını destekler; belirli kapanış tarihi veya gerçekleşme oranı vermez.'),
 'orman-su-yonetimi':(['0304-tip-program-su-p1'],'Program temiz su ve gıdaya erişimi temel hak sayar; bu pasaj ayrı bir orman veya su idaresi modeli tanımlamaz.'),
 'yargi-bagimsizligi':(['0304-tip-program-adalet-p1'],'Program bağımsız ve tarafsız yargı, savunmanın bağımsızlığı ve adalete erişimde ekonomik engellerin kaldırılmasını savunur.'),
 'kultur-sanat':(['0304-tip-program-sanat-p1'],'Program kültür ve sanatta sansür ve baskıya karşı çıkar, herkesin etkinliklere katılımı için önlem savunur.'),
 'cinsel-yonelim':(['0304-tip-program-lgbti-p1'],'Program LGBTİ+ yurttaşlara ayrımcı uygulamalara karşı mücadeleyi ve örgütlenme ve yaşam haklarını koruma mücadelelerinin güçlendirilmesini belirtir; ayrı yasa veya başvuru kurumu bu pasajda tanımlanmaz.'),
 'engellilik':(['0304-tip-program-engelli-p1'],'Program engelli yurttaşların toplumsal, ekonomik ve sağlıkla ilgili taleplerinin yok sayılmasına karşı mücadele eder; ayrı hizmet mekanizması bu pasajda tanımlanmaz.'),
 'guvencesiz-istihdam':(['0304-tip-program-guvence-p1'],'Program güvenceli çalışma hakkı için mücadeleye katılmayı savunur; ilgili pasaj ayrı istihdam güvencesi düzenlemesi vermez.'),
 'halk-meclisi':(['0304-tip-program-halk-meclis-p1'],'Program iş ve yaşam alanlarında meclis tipi halk örgütlenmelerini ve koordinasyonunu savunur.'),
 'ifade-basin-ozgurlugu':(['0304-tip-program-ifade-p1'],'Program örgütlenme, eylem, ifade ve basın özgürlüklerinin korunması ve geliştirilmesi için mücadele eder.'),
 'kurt-sorunu':(['0304-tip-program-kurt-esitlik-p1','0304-tip-program-kurt-esitlik-p2'],'Program Kürt halkının eşit yurttaşlık mücadelesini destekler, anadilde eğitim ve yaşam hakkını benimser ve kendi geleceğini belirleme hakkını kabul eder; hakkın kullanımına tutumunu sınıf mücadelesinin çıkarları doğrultusunda oluşturur.'),
 'anadil-hakki':(['0304-tip-program-anadil-p1'],'Program Kürt halkının eşit yurttaşlık mücadelesini ve anadilde eğitim ile yaşam hakkını destekler.'),
 'genclik':(['0304-tip-program-genclik-p1'],'Program gençlerin ülke yönetiminde daha çok söz sahibi olması için çaba söyler; bu pasaj ayrı katılım kurulu veya seçim mekanizması tanımlamaz.'),
 'teknoloji-inovasyon':(['0304-tip-program-teknoloji-p1'],'Program teknolojinin toplumsal çıkar doğrultusunda geliştirilmesini, çalışma saatlerinin azaltılması ve yaratıcılık için kullanılmasını savunur.'),
 'kamucu-planli-ekonomi':(['0304-tip-program-ekonomi-p1'],'Program ekonomik bağımsızlık ve kamucu, planlı üretimi refahın koşulu görür.'),
 'kamulastirma':(['0304-tip-program-kamulastirma-p1'],'Program özelleştirilen toplumsal varlıkların kamulaştırılmasını hedefler.'),
 'doga-ekoloji':(['0304-tip-program-doga-p1'],'Program doğa ve kamusal alan yağmasına, betonlaşmaya ve doğal varlıkların metalaştırılmasına karşı mücadeleyi anlatır.'),
 'dis-politika':(['0304-tip-program-dis-sosyalizm-p1','0304-tip-program-dis-sosyalizm-p2'],'Programın sosyalist Türkiye modelinde emperyalizme bağımlı kılan kurumlar ve bağımsızlığı ihlal eden anlaşmalarla ilişkilerin sonlandırılması, barış ve halkların kardeşliği öngörülür; model koşulu korunur.'),
 'sehircilik':(['0304-tip-program-sehir-p1'],'Program kentlerde betonlaşma ve mega projeleri durdurmayı hedefler.')}
passages={x['values']['id']:x['values']['exact'] for x in comparison if x['kind']=='passage'}
for ids,_ in topics.values():
 for ident in ids: assert passages[ident] in source,ident
path=Path('data/practices/04-tip-tranches.json'); data=json.loads(path.read_text()); count=0
for row in data['tranches']:
 if row['research_kind']!='statement' or row['topic_id'] not in topics: continue
 assert row['state']=='pending' and row['processed_at'] is None and not row['closure_refs']
 ids,note=topics[row['topic_id']]
 row['research_progress']=dict(recorded_at=datetime.now(timezone.utc).isoformat(),note=note+' Bu kaynak tek başına dönem boyu bütün söylemleri veya tarihsel sürümü belirlemez; TBMM, parti, haber ve diğer uçlar açıktır.',source_ids=['0203-tip-program-v1'],urls=['https://tip.org.tr/parti-programi'],source_passage_ids=ids,status='partial')
 count+=1
assert count==29
path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print('PARTIAL_STATEMENT_LINKS',count)
