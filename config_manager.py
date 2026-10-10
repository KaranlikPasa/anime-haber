# -*- coding: utf-8 -*-
"""
Anime Haber - Nyaa.si Takipçisi
Konfigürasyon ve Geçmiş Yöneticisi
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional

DEFAULT_CONFIG = {
    "check_interval_minutes": 5,
    "enable_desktop_notifications": True,
    "enable_sound_alerts": True,
    "enable_discord": False,
    "discord_webhook_url": "",
    "close_to_tray": True,
    "start_minimized": False,
    "auto_open_magnet": False,
    "anime_list": []
}

DEFAULT_HISTORY = {
    "seen_hashes": [],
    "recent_releases": []
}

class ConfigManager:
    def __init__(self, base_dir: Optional[str] = None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = base_dir
        self.config_path = os.path.join(self.base_dir, "config.json")
        self.history_path = os.path.join(self.base_dir, "history.json")
        
        self.config = self._load_json(self.config_path, DEFAULT_CONFIG)
        self.history = self._load_json(self.history_path, DEFAULT_HISTORY)
        self._seen_set = set(self.history.get("seen_hashes", []))

        if not os.path.exists(self.config_path):
            self.save_config()
        if not os.path.exists(self.history_path):
            self.save_history()

    def _load_json(self, path: str, default_data: dict) -> dict:
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Eksik anahtarları varsayılanlarla doldur
                    for k, v in default_data.items():
                        if k not in data:
                            data[k] = v
                    return data
            except Exception as e:
                print(f"[ConfigManager] Dosya okunamadı ({path}): {e}")
        return json.loads(json.dumps(default_data))

    def save_config(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ConfigManager] Ayarlar kaydedilemedi: {e}")

    def save_history(self):
        try:
            self.history["seen_hashes"] = list(self._seen_set)[-1000:]  # Son 1000 hash'i sakla
            with open(self.history_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[ConfigManager] Gecmis kaydedilemedi: {e}")

    # Anime Listesi Yönetimi
    def get_anime_list(self) -> List[Dict[str, Any]]:
        return self.config.get("anime_list", [])

    def add_anime(self, name: str, quality: str = "Hepsi", group: str = "", category: str = "1_0", alias: str = "") -> Dict[str, Any]:
        item = {
            "id": str(uuid.uuid4())[:8],
            "name": name.strip(),
            "alias": alias.strip(),
            "quality": quality.strip() if quality else "Hepsi",
            "group": group.strip(),
            "category": category,
            "is_active": True
        }
        self.config.setdefault("anime_list", []).append(item)
        self.save_config()
        return item

    def update_anime(self, anime_id: str, updates: Dict[str, Any]) -> bool:
        anime_list = self.config.get("anime_list", [])
        for item in anime_list:
            if item.get("id") == anime_id:
                item.update(updates)
                self.save_config()
                return True
        return False

    def remove_anime(self, anime_id: str) -> bool:
        anime_list = self.config.get("anime_list", [])
        initial_len = len(anime_list)
        self.config["anime_list"] = [x for x in anime_list if x.get("id") != anime_id]
        if len(self.config["anime_list"]) < initial_len:
            self.save_config()
            return True
        return False

    def toggle_anime(self, anime_id: str, is_active: bool) -> bool:
        return self.update_anime(anime_id, {"is_active": is_active})

    # Ayarlar
    def get_settings(self) -> Dict[str, Any]:
        return {
            "check_interval_minutes": self.config.get("check_interval_minutes", 5),
            "enable_desktop_notifications": self.config.get("enable_desktop_notifications", True),
            "enable_sound_alerts": self.config.get("enable_sound_alerts", True),
            "enable_discord": self.config.get("enable_discord", False),
            "discord_webhook_url": self.config.get("discord_webhook_url", ""),
            "close_to_tray": self.config.get("close_to_tray", True),
            "start_minimized": self.config.get("start_minimized", False),
            "auto_open_magnet": self.config.get("auto_open_magnet", False),
        }

    def update_settings(self, new_settings: Dict[str, Any]):
        for k, v in new_settings.items():
            self.config[k] = v
        self.save_config()

    # Geçmiş ve Mükerrer Kontrolü
    def is_hash_seen(self, item_hash: str) -> bool:
        return item_hash in self._seen_set

    def mark_hash_seen(self, item_hash: str):
        self._seen_set.add(item_hash)

    def add_release(self, release_data: Dict[str, Any]):
        info_hash = release_data.get("info_hash") or release_data.get("guid") or release_data.get("title")
        if info_hash:
            self._seen_set.add(info_hash)
        
        releases = self.history.setdefault("recent_releases", [])
        # Başa ekle (en yeni en üstte)
        releases.insert(0, release_data)
        if len(releases) > 200:
            self.history["recent_releases"] = releases[:200]
        self.save_history()

    def get_recent_releases(self) -> List[Dict[str, Any]]:
        return self.history.get("recent_releases", [])

    def clear_history(self):
        self.history["recent_releases"] = []
        self._seen_set.clear()
        self.save_history()
