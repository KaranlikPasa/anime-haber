# 📺 Anime Haber • Nyaa.si Anime Çeviri & Bölüm Takipçisi

[![Arch Linux](https://img.shields.io/badge/Arch%20Linux-AUR%20%7C%20PKGBUILD-1793d1?style=for-the-badge&logo=arch-linux&logoColor=white)](https://github.com/KaranlikPasa/anime-haber)
[![Platform](https://img.shields.io/badge/Platform-Arch%20Linux%20%7C%20Windows-blue?style=for-the-badge)](https://github.com/KaranlikPasa/anime-haber)
[![GitHub Release](https://img.shields.io/github/v/release/KaranlikPasa/anime-haber?style=for-the-badge&color=00b4d8)](https://github.com/KaranlikPasa/anime-haber/releases/latest)

Anime çevirmenleri ve fansub ekipleri için özel olarak geliştirilmiş, **Nyaa.si** üzerindeki yeni bölüm yüklemelerini arka planda otomatik takip eden, bildiren ve tek tıkla doğrudan bilgisayara indiren masaüstü uygulaması. **Arch Linux** ve **Windows** üzerinde tam uyumludur.

---

## 📥 Kurulum

### 🐧 1. Arch Linux Kurulumu

#### Yöntem A: PKGBUILD ile Kurulum
```bash
git clone https://github.com/KaranlikPasa/anime-haber.git
cd anime-haber
makepkg -si
```

#### Yöntem B: Tek Komutla Kurulum Betiği (`install.sh`)
```bash
git clone https://github.com/KaranlikPasa/anime-haber.git
cd anime-haber
chmod +x install.sh
sudo ./install.sh
```

Kurulumdan sonra uygulama menünüzden **Anime Haber**'i seçebilir veya terminalde doğrudan çalıştırabilirsiniz:
```bash
anime-haber
```

---

### 🪟 2. Windows Kurulumu

👉 **[📦 AnimeHaber-v1.0.0-Windows.zip İndir (Son Sürüm)](https://github.com/KaranlikPasa/anime-haber/releases/latest)**

> **Kurulum:** İndirdiğiniz `.zip` dosyasını bir klasöre çıkartın ve içindeki `AnimeHaber.exe` dosyasına çift tıklayarak çalıştırın!

---

## 🚀 Öne Çıkan Özellikler

1. **Akıllı Anime Takip Sistemi:**
   - İstediğiniz animeleri ekleyin (örn: `Sousou no Frieren`, `One Piece`, `Dandadan`, `Bleach`).
   - İsteğe bağlı **Çözünürlük Filtresi** (`1080p`, `720p`, `Hepsi`).
   - İsteğe bağlı **Fansub/Grup Filtresi** (örn: `SubsPlease`, `Erai-raws` veya boş bırakarak tümü).
   - **Kategori Filtresi** (İngilizce Altyazılı `1_2`, Ham/Raw `1_4`, Tüm Anime `1_0`).

2. **Gelişmiş Bildirimler:**
   - 🔔 **Masaüstü Bildirimi:** Linux'ta `notify-send` ile entegre native toast bildirimleri; Windows'ta native toast bildirimi.
   - 🔊 **Sesli Uyarı (Chime):** Bilgisayarda başka işle uğraşırken veya anime izlerken anında duymanız için ses çalar.
   - 💬 **Discord Webhook Entegrasyonu (Fansub Ekipleri İçin):** Çeviri ekibinizin Discord sunucusundaki kanala otomatik olarak şık bir duyuru mesajı yollar (Boyut, Seed/Leech, Magnet ve Nyaa linkleri dahil).

3. **📥 Doğrudan İndirme & Otomatik İndirme Motoru:**
   - 📥 **Doğrudan .torrent İndir:** Tarayıcı açmadan doğrudan `torrentler/` klasörüne indirir ve torrent istemcinizde (qBittorrent vb.) anında başlatır.
   - 🧲 **Tek Tıkla Magnet Aç:** Torrent programınızda indirmeyi hemen başlatır.
   - ⚡ **Otomatik İndirme (Auto-Download):** Ayarlardan aktif edildiğinde, yeni bölüm tespit edilir edilmez dosyayı otomatik bilgisayara indirip torrent programında başlatır!
   - 📁 **İndirilenleri Görüntüle:** Arayüzden tek tıkla indirilen torrent dosyalarının bulunduğu klasörü açabilirsiniz.

4. **Nyaa Canlı Arama:**
   - Tarayıcı açmadan doğrudan uygulama içinden Nyaa.si'de arama yapabilir, çıkan sonuçlardan tek tıkla animeyi takip listenize ekleyebilir veya indirebilirsiniz.

5. **Sistem Tepsisi (System Tray) & Arka Plan:**
   - Pencereyi kapattığınızda sistem saatinin yanına (tepsiye) küçülür ve arka planda takip etmeye devam eder.

---

## 🛠️ Kaynak Koddan Çalıştırma

```bash
pip install -r requirements.txt
python main.py
```

---

## 📄 Lisans
MIT License
