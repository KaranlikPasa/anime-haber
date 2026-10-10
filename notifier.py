# -*- coding: utf-8 -*-
"""
Anime Haber - Nyaa.si Takipçisi
Bildirim Yöneticisi (Windows Native Toast, Ses, Discord Webhook)
"""

import os
import sys
import time
import threading
import requests
from typing import Dict, Any, Optional

try:
    import winsound
except ImportError:
    winsound = None

try:
    import win11toast
except ImportError:
    win11toast = None


class Notifier:
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self._last_sound_time = 0.0
        self._notification_lock = threading.Lock()

    def notify_release(self, release: Dict[str, Any], anime_name: str):
        """Yeni bir bölüm tespit edildiğinde bildirim kanallarını tetikler."""
        settings = self.config_manager.get_settings()

        # 1. Sesli Uyarı (Maksimum 3 saniyede 1 kez çalar, ses patlamasını önler)
        if settings.get("enable_sound_alerts", True):
            now = time.time()
            if now - self._last_sound_time > 3.0:
                self._last_sound_time = now
                self.play_sound()

        # 2. Windows Masaüstü Bildirimi (Non-blocking)
        if settings.get("enable_desktop_notifications", True):
            self.send_desktop_notification(release, anime_name)

        # 3. Discord Webhook Bildirimi
        if settings.get("enable_discord", False) and settings.get("discord_webhook_url"):
            threading.Thread(
                target=self.send_discord_webhook,
                args=(settings.get("discord_webhook_url"), release, anime_name),
                daemon=True
            ).start()

    def play_sound(self):
        """Windows sistem sesini çalar."""
        def _beep():
            try:
                if winsound:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
            except Exception as e:
                print(f"[Notifier] Ses çalınamadı: {e}")
        threading.Thread(target=_beep, daemon=True).start()

    def send_desktop_notification(self, release: Dict[str, Any], anime_name: str):
        """Windows 10/11 Yerel Toast Bildirimi (Kilitlenmeyen / Non-blocking)."""
        rel_title = release.get("title", "")
        size = release.get("size", "")
        seeders = release.get("seeders", "0")
        page_url = release.get("page_url", "")
        magnet_link = release.get("magnet_link", "")

        title = f"🎬 Yeni Bölüm: {anime_name}"
        body = f"{rel_title}\n📦 {size} | 🟢 {seeders} seed"
        launch_url = magnet_link if magnet_link else page_url

        def _send():
            with self._notification_lock:
                try:
                    if win11toast:
                        # win11toast.notify ASYNC/WAIT YAPMAZ, doğrudan Windows Shell'e iletir
                        win11toast.notify(
                            title=title,
                            body=body,
                            on_click=launch_url if launch_url else None
                        )
                    else:
                        print(f"[Notifier] Bildirim: {title} - {body}")
                except Exception as e:
                    print(f"[Notifier] Bildirim gönderilirken hata: {e}")

        threading.Thread(target=_send, daemon=True).start()

    def send_batch_notification(self, anime_name: str, count: int, latest_title: str):
        """Çoklu bölüm yüklendiğinde tek bir özet bildirim gönderir."""
        settings = self.config_manager.get_settings()
        if settings.get("enable_sound_alerts", True):
            self.play_sound()

        if settings.get("enable_desktop_notifications", True):
            title = f"🎬 {anime_name}: {count} Yeni Bölüm!"
            body = f"En son: {latest_title}"
            def _send():
                try:
                    if win11toast:
                        win11toast.notify(title=title, body=body)
                except Exception as e:
                    print(f"[Notifier] Toplu bildirim hatası: {e}")
            threading.Thread(target=_send, daemon=True).start()

    def send_discord_webhook(self, webhook_url: str, release: Dict[str, Any], anime_name: str) -> bool:
        """Discord sunucusuna zengin bildirim gönderir."""
        if not webhook_url or not webhook_url.startswith("http"):
            return False

        rel_title = release.get("title", "")
        size = release.get("size", "Bilinmiyor")
        seeders = release.get("seeders", "0")
        leechers = release.get("leechers", "0")
        category = release.get("category", "Anime")
        page_url = release.get("page_url", "https://nyaa.si")
        torrent_url = release.get("torrent_url", "")
        magnet_link = release.get("magnet_link", "")

        links_text = f"[🌐 Nyaa Sayfası]({page_url})"
        if torrent_url:
            links_text += f" • [📥 .torrent İndir]({torrent_url})"
        if magnet_link:
            links_text += f" • [🧲 Magnet Link]({magnet_link})"

        payload = {
            "username": "Anime Haber",
            "avatar_url": "https://nyaa.si/static/favicon.png",
            "embeds": [
                {
                    "title": f"🎬 Yeni Yükleme: {anime_name}",
                    "description": f"```fix\n{rel_title}\n```",
                    "color": 3066993,
                    "fields": [
                        {"name": "📦 Boyut", "value": size, "inline": True},
                        {"name": "🟢 Seeders", "value": str(seeders), "inline": True},
                        {"name": "🔴 Leechers", "value": str(leechers), "inline": True},
                        {"name": "🏷️ Kategori", "value": category, "inline": True},
                        {"name": "🔗 Bağlantılar", "value": links_text, "inline": False}
                    ],
                    "footer": {
                        "text": "Anime Çeviri Takip Sistemi • Nyaa.si Otomasyonu"
                    }
                }
            ]
        }

        try:
            resp = requests.post(webhook_url, json=payload, timeout=8)
            return resp.status_code in (200, 204)
        except Exception as e:
            print(f"[Notifier] Discord webhook hatası: {e}")
            return False

    def test_discord_webhook(self, webhook_url: str) -> bool:
        sample_release = {
            "title": "[FansubTest] Sample Anime - 01 [1080p].mkv",
            "size": "1.35 GiB",
            "seeders": "42",
            "leechers": "3",
            "category": "Anime - English-translated",
            "page_url": "https://nyaa.si",
            "torrent_url": "https://nyaa.si",
            "magnet_link": "magnet:?xt=urn:btih:0000000000000000000000000000000000000000"
        }
        return self.send_discord_webhook(webhook_url, sample_release, "Test Anime")
