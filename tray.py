# -*- coding: utf-8 -*-
"""
Anime Haber - Nyaa.si Takipçisi
Sistem Tepsisi (System Tray) Yöneticisi
"""

import threading
from typing import Optional, Callable
from PIL import Image, ImageDraw

try:
    import pystray
except ImportError:
    pystray = None


def create_tray_icon_image() -> Image.Image:
    """Sistem tepsisi için şık bir anime/bildirim ikon görseli üretir (64x64)."""
    image = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Dış daire (Koyu Lacivert / Mor)
    draw.ellipse((4, 4, 60, 60), fill=(30, 34, 42, 255), outline=(0, 180, 216), width=3)

    # Zil / Çan çizimi (Turkuaz - #00b4d8)
    # Üst düğme
    draw.ellipse((29, 14, 35, 20), fill=(0, 180, 216, 255))
    # Zil gövdesi
    draw.polygon([(32, 18), (20, 40), (44, 40)], fill=(0, 180, 216, 255))
    draw.pieslice((18, 30, 46, 44), 0, 180, fill=(0, 180, 216, 255))
    # Zil dili
    draw.ellipse((28, 42, 36, 50), fill=(255, 183, 3, 255))

    return image


class TrayManager:
    def __init__(self, on_show_window: Callable[[], None], on_check_now: Callable[[], None], on_quit_app: Callable[[], None]):
        self.on_show_window = on_show_window
        self.on_check_now = on_check_now
        self.on_quit_app = on_quit_app
        self.tray_icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None

    def start(self):
        """Tepsi ikonunu arka planda başlatır."""
        if not pystray:
            return

        image = create_tray_icon_image()
        menu = pystray.Menu(
            pystray.MenuItem("Anime Haber'i Göster", self._action_show, default=True),
            pystray.MenuItem("Şimdi Nyaa'yı Kontrol Et", self._action_check_now),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Çıkış", self._action_quit)
        )

        def _safe_run():
            try:
                self.tray_icon.run()
            except Exception as e:
                print(f"[TrayManager] Sistem tepsisi hatası: {e}")

        self._thread = threading.Thread(target=_safe_run, daemon=True)
        self._thread.start()

    def _action_show(self, icon=None, item=None):
        if self.on_show_window:
            self.on_show_window()

    def _action_check_now(self, icon=None, item=None):
        if self.on_check_now:
            self.on_check_now()

    def _action_quit(self, icon=None, item=None):
        self.stop()
        if self.on_quit_app:
            self.on_quit_app()

    def stop(self):
        """Tepsi ikonunu kaldırır."""
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
            self.tray_icon = None
