# 📺 Anime Haber • Nyaa.si Anime Çeviri & Bölüm Takipçisi

Anime çevirmenleri ve fansub ekipleri için özel olarak geliştirilmiş, **Nyaa.si** üzerindeki yeni bölüm yüklemelerini arka planda otomatik olarak takip eden, bildiren ve tek tıkla indirme imkanı sunan masaüstü uygulaması.

---

## 🚀 Öne Çıkan Özellikler

1. **Akıllı Anime Takip Sistemi:**
   - İstediğiniz animeleri ekleyin (örn: `Sousou no Frieren`, `One Piece`, `Dandadan`, `Bleach`).
   - İsteğe bağlı **Çözünürlük Filtresi** (`1080p`, `720p`, `Hepsi`).
   - İsteğe bağlı **Fansub/Grup Filtresi** (örn: `SubsPlease`, `Erai-raws` veya boş bırakarak tümü).
   - **Kategori Filtresi** (İngilizce Altyazılı `1_2`, Ham/Raw `1_4`, Tüm Anime `1_0`).

2. **Gelişmiş Bildirimler:**
   - 🔔 **Windows 10/11 Masaüstü Bildirimi:** Yeni bölüm düştüğü an ekranın sağ alt köşesinde başlık, boyut ve seed sayısı ile toast bildirimi açılır.
   - 🔊 **Sesli Uyarı (Chime):** Bilgisayarda başka işle uğraşırken veya anime izlerken anında duymanız için ses çalar.
   - 💬 **Discord Webhook Entegrasyonu (Fansub Ekipleri İçin):** Çeviri ekibinizin Discord sunucusundaki kanala otomatik olarak şık bir duyuru mesajı yollar (Boyut, Seed/Leech, Magnet ve Nyaa linkleri dahil).

3. **Hızlı İndirme & Magnet Desteği:**
   - 🧲 **Tek Tıkla Magnet Aç:** qBittorrent, uTorrent vb. torrent istemcinizde doğrudan indirmeyi başlatır.
   - 📥 **.torrent İndir:** Torrent dosyasını doğrudan çeker.
   - 🌐 **Nyaa Sayfası:** Tek tıkla tarayıcıda ilgili torrent sayfasını açar.
   - ⚡ **Otomatik Magnet:** Ayarlardan açılırsa yeni bölüm gelir gelmez torrent istemcinizi otomatik açabilir.

4. **Nyaa Canlı Arama:**
   - Tarayıcı açmadan doğrudan uygulama içinden Nyaa.si'de arama yapabilir, çıkan sonuçlardan tek tıkla animeyi takip listenize ekleyebilirsiniz.

5. **Sistem Tepsisi (System Tray) & Arka Plan:**
   - Pencereyi kapattığınızda sistem saatinin yanına (tepsiye) küçülür ve arka planda takip etmeye devam eder.

6. **Mükerrer Önleme:**
   - `infoHash` tabanlı kontrol sayesinde daha önce görülen bölümler için asla gereksiz bildirim almazsınız.

---

## 🛠️ Nasıl Çalıştırılır?

Klasör içindeki dosyalar:
- **`baslat.bat`**: Çift tıklayarak uygulamayı başlatabilirsiniz. Gerekli kütüphaneleri otomatik kontrol eder ve açar.
- **`arkaplanda_baslat.vbs`**: Konsol (siyah CMD penceresi) olmadan doğrudan sessizce başlatmak için çift tıklayın.
- **`Masaustune_Kisayol_Olustur.ps1`**: Sağ tıklayıp "PowerShell ile Çalıştır" derseniz Masaüstünüze `Anime Haber` kısayolu ekler.

---

## ⚙️ Yapılandırma ve Dosyalar

- `config.json`: Takip edilen animeler ve genel ayarlarınızı saklar.
- `history.json`: Tespit edilen bölümlerin geçmişini ve mükerrer engelleme hash'lerini saklar.
- `main.py`: Ana başlatıcı.
- `ui.py`: CustomTkinter grafik arayüzü.
- `tracker.py`: Nyaa.si RSS veri çekici ve filtreleme motoru.
- `notifier.py`: Windows bildirimleri ve Discord Webhook yöneticisi.
- `tray.py`: Sistem tepsisi simge yöneticisi.
