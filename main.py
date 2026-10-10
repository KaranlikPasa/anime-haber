# -*- coding: utf-8 -*-
"""
Anime Haber - Nyaa.si Takipçisi
Ana Başlatıcı Dosyası (Entry Point)
"""

import os
import sys
import traceback

# Çalışma dizinini bu dosyanın bulunduğu klasöre ayarla
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

LOG_FILE = os.path.join(BASE_DIR, "anime_haber.log")

def log(msg):
    try:
        timestamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {msg}\n")
    except Exception:
        pass
    print(msg)


def main():
    log("[Anime Haber] Başlatılıyor...")

    try:
        from config_manager import ConfigManager
        from notifier import Notifier
        from tracker import NyaaTracker
        from tray import TrayManager
        from ui import AnimeHaberUI
    except Exception as e:
        err = f"Modüller yüklenirken kritik hata oluştu:\n{traceback.format_exc()}"
        log(err)
        try:
            import tkinter.messagebox as mb
            mb.showerror("Anime Haber Başlatma Hatası", err)
        except Exception:
            pass
        sys.exit(1)

    try:
        # 1. Konfigürasyon yöneticisi
        config_manager = ConfigManager(base_dir=BASE_DIR)

        # 2. Bildirim yöneticisi
        notifier = Notifier(config_manager)

        # 3. Nyaa Takip motoru
        tracker = NyaaTracker(config_manager, notifier)

        # 4. Arayüz ve Sistem Tepsisi
        app = None
        tray_manager = None

        def on_show_window():
            if app:
                app.restore_window()

        def on_check_now():
            tracker.trigger_check_now()

        def on_quit_app():
            if app:
                app.quit_application()

        try:
            tray_manager = TrayManager(
                on_show_window=on_show_window,
                on_check_now=on_check_now,
                on_quit_app=on_quit_app
            )
        except Exception as e:
            log(f"Sistem tepsisi başlatılamadı (devam ediliyor): {e}")
            tray_manager = None

        # GUI Başlat
        app = AnimeHaberUI(config_manager, tracker, notifier, tray_manager)

        # Arka plan servislerini çalıştır
        tracker.start()
        if tray_manager:
            try:
                tray_manager.start()
            except Exception as e:
                log(f"Tepsi ikonu başlatma hatası: {e}")

        # Başlangıçta gizli başlama seçeneği kontrolü
        if config_manager.get_settings().get("start_minimized", False):
            app.withdraw()

        log("[Anime Haber] Arayüz başarıyla açıldı.")
        app.mainloop()

    except Exception as e:
        err = f"Uygulama çalışırken beklenmeyen bir hata oluştu:\n{traceback.format_exc()}"
        log(err)
        try:
            import tkinter.messagebox as mb
            mb.showerror("Anime Haber Hatası", err)
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
