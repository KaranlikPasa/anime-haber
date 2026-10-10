# -*- coding: utf-8 -*-
"""
Anime Haber - Nyaa.si Takipçisi
Nyaa.si RSS Çekici, Arama ve Filtreleme Motoru
"""

import os
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable

NYAA_TRACKERS = [
    "http://nyaa.tracker.wf:7777/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://tracker.torrent.eu.org:451/announce"
]

XML_NAMESPACES = {
    "nyaa": "https://nyaa.si/xmlns/nyaa"
}

class NyaaTracker:
    def __init__(self, config_manager, notifier):
        self.config_manager = config_manager
        self.notifier = notifier
        self.is_running = False
        self._worker_thread: Optional[threading.Thread] = None
        self._force_check_event = threading.Event()
        self.last_check_time: Optional[datetime] = None
        
        # Daha önce en az bir kez taranmış animelerin ID seti (İlk açılışta yüzlerce geçmiş bildirimi engellemek için)
        self._initialized_anime_ids = set()

        # UI Callbacks
        self.on_check_started: Optional[Callable[[], None]] = None
        self.on_check_completed: Optional[Callable[[int, int], None]] = None
        self.on_new_release: Optional[Callable[[Dict[str, Any]], None]] = None
        self.on_status_update: Optional[Callable[[str], None]] = None

    def start(self):
        """Arka plan kontrol iş parçacığını başlatır."""
        if self.is_running:
            return
        self.is_running = True
        self._worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker_thread.start()

    def stop(self):
        """Arka plan iş parçacığını durdurur."""
        self.is_running = False
        self._force_check_event.set()

    def trigger_check_now(self):
        """Beklemeden anında bir kontrol başlatır."""
        self._force_check_event.set()

    def _worker_loop(self):
        """Periyodik aralıklarla Nyaa.si'yi sorgulayan arka plan döngüsü."""
        # İlk açılışta hemen bir kontrol yap
        self._check_all_tracked_anime()

        while self.is_running:
            settings = self.config_manager.get_settings()
            interval_mins = max(1, settings.get("check_interval_minutes", 5))
            sleep_seconds = interval_mins * 60

            # force_check_event veya timeout bekler
            awakened = self._force_check_event.wait(timeout=sleep_seconds)
            self._force_check_event.clear()

            if not self.is_running:
                break

            self._check_all_tracked_anime()

    def _check_all_tracked_anime(self):
        """Takip listesindeki tüm aktif animeleri kontrol eder."""
        if self.on_check_started:
            try:
                self.on_check_started()
            except Exception:
                pass

        if self.on_status_update:
            try:
                self.on_status_update("Nyaa.si taranıyor...")
            except Exception:
                pass

        anime_list = self.config_manager.get_anime_list()
        active_animes = [a for a in anime_list if a.get("is_active", True)]
        total_found = 0
        new_count = 0

        for anime in active_animes:
            if not self.is_running:
                break
            try:
                anime_id = anime.get("id")
                anime_name = anime.get("name", "Anime")
                is_first_scan_for_this_anime = anime_id not in self._initialized_anime_ids

                results = self.fetch_anime_releases(anime)
                total_found += len(results)

                new_releases_this_batch = []

                for item in results:
                    info_hash = item.get("info_hash") or item.get("guid") or item.get("title")
                    
                    if not self.config_manager.is_hash_seen(info_hash):
                        # Geçmişe kaydet
                        self.config_manager.add_release(item)

                        if not is_first_scan_for_this_anime:
                            # Bu anime daha önce taranmıştı, bu GERÇEKTEN YENİ bir bölüm!
                            new_count += 1
                            new_releases_this_batch.append(item)

                # İlk tarama bitti, bu animeyi artık başlatılmış olarak işaretle
                self._initialized_anime_ids.add(anime_id)

                # Bildirim gönderme (Mükerrer veya sel baskını önleme)
                if new_releases_this_batch:
                    if len(new_releases_this_batch) == 1:
                        # Tek bölüm: Detaylı bildirim
                        single_item = new_releases_this_batch[0]
                        self.notifier.notify_release(single_item, anime_name)
                    else:
                        # Çoklu bölüm aynı anda geldiyse: Toplu özet bildirim
                        self.notifier.send_batch_notification(
                            anime_name, 
                            len(new_releases_this_batch), 
                            new_releases_this_batch[0].get("title", "")
                        )

                    # Otomatik magnet açma seçeneği
                    if self.config_manager.get_settings().get("auto_open_magnet", False):
                        for n_item in new_releases_this_batch:
                            magnet = n_item.get("magnet_link")
                            if magnet:
                                try:
                                    os.startfile(magnet)
                                except Exception:
                                    pass

                # Nyaa sunucusuna saygı için sorgular arası kısa mola
                time.sleep(1.0)

            except Exception as e:
                print(f"[NyaaTracker] '{anime.get('name')}' sorgulanırken hata: {e}")

        self.last_check_time = datetime.now()

        if self.on_check_completed:
            try:
                self.on_check_completed(total_found, new_count)
            except Exception:
                pass

        if self.on_status_update:
            try:
                if new_count > 0:
                    status_msg = f"Son kontrol: {self.last_check_time.strftime('%H:%M:%S')} ({new_count} YENİ BÖLÜM BİLDİRİLDİ!)"
                else:
                    status_msg = f"Son kontrol: {self.last_check_time.strftime('%H:%M:%S')} (Yeni yükleme yok)"
                self.on_status_update(status_msg)
            except Exception:
                pass

    def fetch_anime_releases(self, anime_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Belirtilen anime konfigürasyonuna göre Nyaa RSS'ini çeker ve filtreler."""
        name = anime_config.get("name", "").strip()
        alias = anime_config.get("alias", "").strip()
        category = anime_config.get("category", "1_0")
        quality_filter = anime_config.get("quality", "Hepsi").strip()
        group_filter = anime_config.get("group", "").strip().lower()

        results = []
        # Ana isim ile ara
        if name:
            results.extend(self.search_nyaa_rss(name, category=category))

        # Varsa alternatif isimle de ara
        if alias and alias.lower() != name.lower():
            alias_results = self.search_nyaa_rss(alias, category=category)
            existing_hashes = {r.get("info_hash") for r in results if r.get("info_hash")}
            for ar in alias_results:
                if ar.get("info_hash") not in existing_hashes:
                    results.append(ar)

        # Filtreleme (Kalite ve Çeviri Grubu)
        filtered = []
        for item in results:
            title = item.get("title", "")
            title_lower = title.lower()

            # Kalite filtresi (1080p, 720p vs.)
            if quality_filter and quality_filter != "Hepsi":
                if quality_filter.lower() not in title_lower:
                    continue

            # Fansub / Çeviri Grubu filtresi
            if group_filter:
                if group_filter not in title_lower:
                    continue

            item["matched_anime"] = name
            filtered.append(item)

        return filtered

    def search_nyaa_rss(self, query: str, category: str = "1_0") -> List[Dict[str, Any]]:
        """Nyaa.si RSS üzerinden arama yapar ve parse eder."""
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://nyaa.si/?page=rss&q={encoded_query}&c={category}&f=0"

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AnimeHaber/1.0",
                "Accept": "application/rss+xml, application/xml, text/xml"
            }
        )

        try:
            with urllib.request.urlopen(req, timeout=12) as response:
                content = response.read()
        except Exception as e:
            print(f"[NyaaTracker] RSS istek hatası ({url}): {e}")
            return []

        try:
            root = ET.fromstring(content)
        except Exception as e:
            print(f"[NyaaTracker] XML parse hatası: {e}")
            return []

        channel = root.find("channel")
        if channel is None:
            return []

        items = []
        for item_node in channel.findall("item"):
            title = self._get_node_text(item_node, "title")
            torrent_url = self._get_node_text(item_node, "link")
            guid = self._get_node_text(item_node, "guid")
            pub_date = self._get_node_text(item_node, "pubDate")
            
            info_hash = self._get_node_text(item_node, "nyaa:infoHash")
            size = self._get_node_text(item_node, "nyaa:size")
            seeders = self._get_node_text(item_node, "nyaa:seeders")
            leechers = self._get_node_text(item_node, "nyaa:leechers")
            downloads = self._get_node_text(item_node, "nyaa:downloads")
            cat_name = self._get_node_text(item_node, "nyaa:category")

            # Magnet link oluştur
            magnet_link = ""
            if info_hash:
                tr_params = "&".join([f"tr={urllib.parse.quote(tr)}" for tr in NYAA_TRACKERS])
                magnet_link = f"magnet:?xt=urn:btih:{info_hash}&dn={urllib.parse.quote(title)}&{tr_params}"

            # Grup adını başlıktan çıkar (örnek: [SubsPlease] veya [Erai-raws])
            group_match = re.match(r"^\[(.*?)\]", title)
            group_name = group_match.group(1) if group_match else ""

            # Çözünürlüğü başlıktan çıkar (örnek: 1080p, 720p, 480p)
            res_match = re.search(r"\b(1080p|720p|480p|2160p|4k)\b", title, re.IGNORECASE)
            resolution = res_match.group(1).lower() if res_match else ""

            items.append({
                "title": title,
                "group": group_name,
                "resolution": resolution,
                "torrent_url": torrent_url,
                "page_url": guid,
                "guid": guid,
                "info_hash": info_hash,
                "magnet_link": magnet_link,
                "size": size or "Bilinmiyor",
                "seeders": seeders or "0",
                "leechers": leechers or "0",
                "downloads": downloads or "0",
                "category": cat_name or "Anime",
                "pub_date": pub_date,
                "detected_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        return items

    def _get_node_text(self, parent_node: ET.Element, tag_name: str) -> str:
        """Namespace destekli olarak XML düğüm metnini alır."""
        if ":" in tag_name:
            prefix, local_name = tag_name.split(":", 1)
            ns_uri = XML_NAMESPACES.get(prefix)
            if ns_uri:
                elem = parent_node.find(f"{{{ns_uri}}}{local_name}")
                if elem is not None and elem.text:
                    return elem.text.strip()
        elem = parent_node.find(tag_name)
        if elem is not None and elem.text:
            return elem.text.strip()
        return ""
