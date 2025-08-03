# Proje Neva

<img src="https://i.imgur.com/MH1no3T.png" alt="Neva Logo" width="250">

## ● Takım İsmi
**AI Grup 2**

## ● Takım Rolleri
* **Product Owner:** `[Beyza  Erdem]`
* **Scrum Master:** `[Osman Şener Gürel]`
* **Developer:** `[Sena Demirbaş]`
* **Developer:** `[Muhammed Enes Güryeli]`
* **Developer:** `[Pelinsu İlçin]`

## ● Ürün İsmi
**Neva**

## ● Ürün Açıklaması
Neva, modern yaşamın getirdiği stres, kaygı ve yalnızlık gibi zorluklarla mücadele eden bireylere destek olmak amacıyla geliştirilmiş, yapay zeka tabanlı bir psikolojik destek ve sohbet asistanıdır. Kullanıcılarına sesli etkileşim yoluyla empatik, yargılamayan ve güvenli bir sohbet ortamı sunar. Amacımız, herkesin ihtiyaç duyduğu anda konuşabileceği bir "dijital sırdaş" yaratarak zihinsel farkındalığı artırmak ve yalnızlık hissini azaltmaktır.

## ● Ürün Özellikleri
* **Sesli Etkileşim:** Kullanıcılar, Neva ile doğal bir konuşma deneyimi yaşayabilmek için metin girişi yerine sesli komutları kullanabilir. Gelişmiş STT (Speech-to-Text) ve TTS (Text-to-Speech) teknolojileri ile akıcı bir diyalog sağlanır.
* **Empati Odaklı Diyalog:** Neva'nın temelinde, kullanıcıyı anlamaya ve ona değer verdiğini hissettirmeye programlanmış, gelişmiş bir Büyük Dil Modeli (LLM) bulunur.
* **Kısa Süreli Hafıza:** Neva, konuşmanın bağlamını korumak için diyaloğun son birkaç adımını hatırlayarak daha tutarlı ve anlamlı cevaplar üretir.
* **Kriz Anı Desteği:** Kullanıcının ifadelerinde kendine zarar verme veya derin bir umutsuzluk gibi kritik durumlar tespit edildiğinde, Neva profesyonel yardım kuruluşlarına yönlendirme yaparak etik ve güvenli bir sınır çizer.
* **Erişilebilir Arayüz:** Özellikle yaşlı veya teknolojiye uzak kullanıcılar düşünülerek tasarlanmış, basit, sade ve kullanımı kolay bir arayüze sahiptir.

## ● Hedef Kitle
* **Birincil Hedef Kitle:** Yoğun iş temposu, eğitim hayatı veya kişisel nedenlerden dolayı stres, kaygı ve tükenmişlik hisseden gençler ve yetişkinler.
* **İkincil Hedef Kitle:** Yalnızlık hisseden ve günlük sohbet ihtiyacı duyan, özellikle yaşlı bireyler.
* **Genel Kitle:** Duygu ve düşüncelerini yargılanma korkusu olmadan paylaşmak isteyen herkes.

## ● Product Backlog
Bu liste, projenin mevcut ve gelecekteki potansiyel özelliklerini içermektedir.

---

# Sprint Raporları

<details>
<summary><h2>📋 SPRINT 1 RAPORU</h2></summary>

**Sprint Adı/Numarası:** Sprint 1: Projeye Başlangıç  
**Takım Adı:** AI takım 2   
**Sprint Başlangıç Tarihi:** 29.06.2025  
**Sprint Bitiş Tarihi:** 02.07.2025

---

### 1. Sprint Hedefi (Sprint Goal)
Bu sprintin ana hedefi, projenin her dalını bir nebze olsa da ilerletmek ve temelini oluşturmaktı. Ekip arkadaşlarımızla beraber projemizin adını "Neva" olarak seçtikten sonra, kabaca bir şekilde ekipteki herkes ilgili olduğu alanda çalışmalarına başladı.

---

### 2. Tamamlanan İşler (Completed Work)
- **Sohbet API'si (`/chat`) oluşturuldu:** Uygulama, kullanıcıdan gelen mesajı alıp yapay zeka modeline gönderebiliyor ve modelin cevabını geri döndürebiliyor.
- **Google Generative AI API’si ile chat kısmı oluşturuldu:** Uygulama tabanı olarak hem bir dost hem de psikolojik bir yapay zeka asistanı olarak, karşısındaki insan ile yazılı olarak konuşma özelliği eklendi.
- **Kullanıcının chat üzerindeki hafızası `.json` olarak eklendi:** Uygulama kullanıcının önceki konuşma ve fikirlerini hatırlayacak şekilde güncellendi ve konuşma geçmişi kayıt edildi.
- **Ortak bir çalışma alanı (Github Repo’su) oluşturuldu:** Github üzerinden herkesin erişip çalışabileceği ve PR açabileceği bir ortam oluşturuldu.
- **Uygulamanın ilk arayüz tasarımı oluşturuldu:** `.html` ile ara yüz tasarımının ilk hali yapıldı.

---

### 3. Tamamlanamayan İşler ve Karşılaşılan Zorluklar
İlk sprintimiz olduğu için net hedefler konulmamıştı, bu yüzden teknik olarak tamamlanamayan bir görev bulunmamaktadır.
- **Karşılaşılan Zorluk:** Ekip olarak toplu olarak bir toplantıya katılıp fikir alış-verişinde bulunmakta zorlandık fakat son zamanlarda bu sorunun üstesinden gelindi gibi.

---

### 4. Sprint Metrikleri ve Puanlama

**Puanlama Mantığı:**
> Takım olarak bu sprintte işlerin büyüklüğünü tahmin etmek için Fibonacci (1, 2, 3, 5, 8...) ölçeğini kullandık. Puanlar, bir işin saat olarak ne kadar süreceğini değil; karmaşıklığını, belirsizliğini ve gereken eforu temsil eden göreceli bir ölçüttür.

**Sprint Puanları:**
- **Planlanan Toplam Puan:** 18 Puan
- **Tamamlanan Toplam Puan:** 13 Puan
- **Takım Hızı (Velocity):** 13

---

### 5. Sprint İlerleme Grafiği (Burndown Chart)

![Sprint 1 Burndown Chart](https://i.imgur.com/XvUqLdA.png)

---

### 6. Sprint Review Sonuçları ve Notlar

**Katılımcılar:** Tüm "Neva" takımı.

**Sunulan İşler:**
- Komut satırı üzerinden çalışan, hafıza yeteneğine sahip temel sohbet uygulaması canlı olarak test edildi.
- Oluşturulan GitHub deposu ve çalışma kuralları sunuldu.

**Alınan Geri Bildirim (Feedback):**
- Hafıza özelliğinin çalışması çok beğenildi.
- Arayüzün bir an önce geliştirilmesi gerektiği belirtildi.
- Sesli konuşma özelliğinin bir sonraki sprintin ana hedefi olması gerektiği vurgulandı.

**Alınan Kararlar:**
- Bir sonraki sprintte TTS (Text-to-Speech) özelliğine öncelik verilecek.

---

### 7. Sprint Geri Bildirimi (Retrospective'den Notlar)

- **İyi Gidenler:** Genel olarak uygulamanın geliştirilmesi, herkesin en sonunda senkronize olup yapılacaklara odaklanması ve birbirine kolaylık sağlaması.
- **Geliştirilmesi Gerekenler:** Takım içi iletişimi daha düzenli hale getirmek ve projedeki boş kalan alanları proaktif olarak doldurmak.

---

### 8. Sonraki Sprint İçin Öncelikli Konular
- TTS (Text-to-Speech) teknolojisinin belirlenmesi ve implementasyonu.
- Backend mimarisinin geliştirilmesi.
- Arayüz tasarımı ve temel kaynak kodlarının geliştirilmesi.

</details>

---

<details>
<summary><h2>📋 SPRINT 2 RAPORU</h2></summary>

**Sprint Adı/Numarası:** Sprint 2: Projeye Gelişimi   
**Takım Adı:** AI takım 2   
**Sprint Başlangıç Tarihi:** 02.07.2025  
**Sprint Bitiş Tarihi:** 20.07.2025

### 1. Sprint Hedefi (Sprint Goal)
Bu sprintin ana hedefi, Faz 1'de oluşturulan komut satırı uygulamasını bir adım ileri taşıyarak, ses teknolojilerini (TTS/STT) seçip implemente etmek, projenin statik frontend arayüzünü (HTML/CSS/JS) hayata geçirmek ve backend mimarisinin geliştirilmesiydi.

---

### 2. Tamamlanan İşler (Completed Work)
- **Frontend Arayüzü Hayata Geçirildi:** Projenin ilk görsel tasarımı, HTML, CSS ve JavaScript kullanılarak statik bir web arayüzüne dönüştürüldü.
- **Ses Teknolojileri (TTS/STT) Seçildi:** Metinden sese ve sesten metne çeviri işlemleri için Google Cloud'un TTS ve STT servislerinin kullanılmasına karar verildi.
- **TTS Entegrasyonu Tamamlandı:** Google Cloud TTS servisi, ana uygulama mantığına başarıyla entegre edildi, böylece Neva ile sesli etkileşim mümkün hale geldi ve hafıza sesli iletişimle desteklendi.

---

### 3. Tamamlanamayan İşler ve Karşılaşılan Zorluklar
- **Tamamlanamayan İşler:**
  - Backend Mimarisi ve API Entegrasyonu: Backend'in bir web API'sine dönüştürülmesi ve ana bileşenlerin bağlanması görevi tamamlanamadı.
  - Frontend-Backend Bağlantısı: Statik olarak hazırlanan frontend'in, backend ile haberleşmesi sağlanamadı.
  - Kullanıcı Veritabanı Yönetimi: Kullanıcı verilerinin yönetileceği veritabanı altyapısı oluşturulamadı.
- **Karşılaşılan Zorluk:** Frontend ve ses teknolojileri entegrasyonu, tahmin edilenden daha fazla zaman ve detaylı çalışma gerektirdi. Bu nedenle, backend ve API geliştirme görevlerine bu sprintte başlanamadı.

---

### 4. Sprint Metrikleri ve Puanlama

**Puanlama Mantığı:**
> Takım olarak işlerin büyüklüğünü tahmin etmek için Fibonacci (1, 2, 3, 5, 8...) ölçeğini kullanıyoruz. Puanlar, bir işin saat olarak ne kadar süreceğini değil; karmaşıklığını, eforunu ve belirsizliğini temsil eden göreceli bir ölçüttür.

**Sprint Puanları:**
- **Planlanan Toplam Puan:** 21
- **Tamamlanan Toplam Puan:** 13
- **Takım Hızı (Velocity):** 13

### 5. Sprint İlerleme Grafiği (Burndown Chart)

![Sprint 2 Burndown Chart](https://i.imgur.com/nXTBvpy.png)

---

### 6. Sprint Review Sonuçları ve Notlar

**Sunulan İşler:**
- Çalışan statik frontend arayüzü ve buton etkileşimleri sunuldu.
- Komut satırı üzerinden Neva'nın sesli cevap verme yeteneği (TTS) canlı olarak gösterildi.

**Alınan Geri Bildirim (Feedback):**
- TTS entegrasyonunun başarısı ve frontend'in görsel olarak ilerlemesi olumlu karşılandı.
- Backend-frontend bağlantısının olmaması, bir sonraki sprint için en yüksek öncelik olarak belirlendi.

---

### 7. Sprint Geri Bildirimi (Retrospective'den Notlar)

- **İyi Gidenler:** Frontend ve ses teknolojileri üzerinde çalışan ekip üyeleri arasında güçlü bir senkronizasyon vardı ve bu alanlarda somut çıktılar elde edildi.
- **Geliştirilmesi Gerekenler:** Sprint hedefini daha dar ve odaklı belirlemeliyiz. Bu sprintte hem frontend hem de backend bağlantısını tamamlama hedefi fazla iddialıydı.

---

### 8. Sonraki Sprint İçin Öncelikli Konular
- Backend mimarisini api servisleri kullanarak oluşturmak.
- Frontend ile Backend arasında API bağlantısını kurmak.
- Temel kullanıcı veritabanı yapısını oluşturmak.
- Projenin deploy edilmesi için gerekli adımları atmak.

</details>

---

<details>
<summary><h2>📋 SPRINT 3 RAPORU</h2></summary>

**Sprint Adı/Numarası:** Sprint 3: Projeye Gelişimi   
**Takım Adı:** AI takım 2   
**Sprint Başlangıç Tarihi:** 20.07.2025  
**Sprint Bitiş Tarihi:** 03.08.2025

---

### 1. Sprint Hedefi (Sprint Goal)
Bu sprintin ana hedefi, projenin tüm bileşenlerini (Frontend, Backend-AI, Backend-Kullanıcı) bir araya getirerek tam fonksiyonel bir yerel prototip oluşturmak ve projeyi canlı bir sunucu ortamına taşımaktı.

---

### 2. Tamamlanan İşler (Completed Work)

Bu sprintte projemiz baştan sona entegre edilerek canlıya hazır hale getirilmiştir:

- **Canlı Kullanıcı Yönetim API'si :**
  - Kullanıcı kaydı, girişi, çıkışı ve şifre sıfırlama gibi tüm kimlik doğrulama işlemleri tamamlandı ve canlı bir PHP API'sine bağlandı.
  - Kullanıcı veritabanı ve yönetimi altyapısı başarıyla oluşturuldu.

- **Canlı Sunucu Kurulumu ve Host Etme :**
  - Proje, gerekli tüm konfigürasyonlar yapılarak bir Ubuntu sunucusuna başarıyla kuruldu ve herkesin erişebileceği bir link üzerinden canlıya alındı.

- **Ses Teknolojileri ve Ana Mantık :**
  - Google Speech Service API kullanılarak TTS (Metinden Sese) ve STT (Sesten Metne) özellikleri ana mantığa entegre edildi.
  - Sesli konuşmaların da, aynı yazılı sohbet gibi, `.json` formatında hafızada tutulması sağlandı.

- **Yerel Tam Entegrasyon :**
  - FastAPI kullanılarak oluşturulan yerel backend, `app.py`'deki ana mantığı ve ses servislerini kullanarak frontend ile tam entegre hale getirildi.
  - Performans ve güvenlik iyileştirmeleri yapılarak, kullanıcı girişi ve sohbet özellikleriyle tam fonksiyonel, canlıya hazır bir yerel sürüm tamamlandı.

- **Nihai Frontend Tasarımı :**
  - Frontend arayüzü, faviconlar, yönlendirmeler (redirects) ve çok sayıda kullanıcı deneyimi iyileştirmesi ile tamamen bitirilmiş ve cilalanmış bir hale getirildi.

---

### 3. Karşılaşılan Zorluklar
- **Hibrit Mimarinin Yönetimi:** İki farklı backend teknolojisini (PHP ve Python) bir arada yönetmek ve aralarındaki veri akışını planlamak, başlangıçta ek koordinasyon gerektirdi. Ancak bu zorluk, API'lerin net bir şekilde dokümante edilmesiyle aşıldı.

---

### 4. Sprint Metrikleri ve Puanlama

**Puanlama Mantığı:**
> Takım olarak işlerin büyüklüğünü tahmin etmek için Fibonacci (1, 2, 3, 5, 8...) ölçeğini kullanıyoruz. Puanlar, bir işin saat olarak ne kadar süreceğini değil; karmaşıklığını, eforunu ve belirsizliğini temsil eden göreceli bir ölçüttür.

**Sprint Puanları:**
- **Planlanan Toplam Puan:** 21
- **Tamamlanan Toplam Puan:** 18
- **Takım Hızı (Velocity):** 13

---

### 5. Sprint İlerleme Grafiği (Burndown Chart)

![Sprint 3 Burndown Chart](https://i.imgur.com/StOP4sv.png)

---

### 6. Sprint Review Sonuçları ve Notlar

**Sunulan İşler:**
- Canlı sunucu üzerindeki linkten, kullanıcı kaydı ve girişi başarıyla gösterildi.
- Yerel ortamda, giriş yapmış bir kullanıcının frontend arayüzü üzerinden Neva ile hem yazılı hem de sesli olarak sohbet edebildiği tam entegre bir demo yapıldı.

**Alınan Geri Bildirim (Feedback):**
- Projenin bu kadar kısa sürede fikir aşamasından tam fonksiyonel bir prototipe dönüşmesi büyük takdir topladı.
- Özellikle sesli konuşma özelliğinin akıcılığı ve hafıza yeteneği çok beğenildi.

---

### 7. Sprint Geri Bildirimi (Retrospective'den Notlar)

- **İyi Gidenler:** Takım üyeleri arasındaki rol dağılımı ve uzmanlık alanlarına göre sorumluluk alınması projenin hızla ilerlemesini sağladı. Özellikle backend ve frontend ekiplerinin paralel çalışması çok verimliydi.
- **Geliştirilmesi Gerekenler:** Projenin son aşamasında olduğumuz için, kullanıcıların canlı feedbackleri ile gereken geliştirmelerin tamamlanması.

---

### 8. Sonraki Sprint İçin Öncelikli Konular
- Tüm uygulama akışı için uçtan uca testlerin yapılması.
- Olası hataların (bug) tespiti ve giderilmesi.

</details>