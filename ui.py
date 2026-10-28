from os_utils import open_path_or_url
# -*- coding: utf-8 -*-
"""
Anime Haber - Nyaa.si Takipçisi
CustomTkinter Tabanlı Modern Grafik Arayüzü (GUI)
"""

import os
import sys
import webbrowser
import threading
from typing import Dict, Any, List, Optional
import customtkinter as ctk
from tkinter import messagebox

# Görünüm Teması
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AnimeHaberUI(ctk.CTk):
    def __init__(self, config_manager, tracker, notifier, tray_manager):
        super().__init__()

        self.config_manager = config_manager
        self.tracker = tracker
        self.notifier = notifier
        self.tray_manager = tray_manager

        # Pencere Yapılandırması
        self.title("Anime Haber • Nyaa.si Takipçisi")
        self.geometry("1100x720")
        self.minsize(950, 600)

        # Kapanma davranışı (Tepsiye küçültme)
        self.protocol("WM_DELETE_WINDOW", self.on_close_requested)

        # UI Durum Değişkenleri
        self.status_text_var = ctk.StringVar(value="Hazır")
        self.active_count_var = ctk.StringVar(value="0 anime takip ediliyor")
        self.search_filter_var = ctk.StringVar()
        self.search_filter_var.trace_add("write", lambda *args: self.filter_feed())

        # Tracker Dinleyicileri
        self.tracker.on_check_started = self._tracker_started
        self.tracker.on_check_completed = self._tracker_completed
        self.tracker.on_new_release = self._tracker_new_release
        self.tracker.on_status_update = self._tracker_status_update

        # Arayüz Bileşenlerini Kur
        self._build_header()
        self._build_tabs()
        self._build_statusbar()

        # İlk veri yüklemeleri
        self.load_tracked_anime_list()
        self.refresh_feed()
        self._update_stats()

    # -------------------------------------------------------------
    # Başlık ve Üst Panel
    # -------------------------------------------------------------
    def _build_header(self):
        header_frame = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=0, height=70)
        header_frame.pack(fill="x", padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Sol Başlık Grubu
        left_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_box.pack(side="left", padx=20, pady=10)

        title_lbl = ctk.CTkLabel(
            left_box, 
            text="📺 ANİME HABER", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#00b4d8"
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            left_box, 
            text="Nyaa.si Yeni Bölüm Takip & İndirme Otomasyonu", 
            font=ctk.CTkFont(size=12),
            text_color="#94a3b8"
        )
        sub_lbl.pack(anchor="w")

        # Sağ Kontrol Grubu
        right_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_box.pack(side="right", padx=20, pady=12)

        self.btn_check_now = ctk.CTkButton(
            right_box,
            text="🔄 Şimdi Kontrol Et",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=160,
            height=38,
            command=self.action_check_now
        )
        self.btn_check_now.pack(side="right", padx=5)

    # -------------------------------------------------------------
    # Sekmeler
    # -------------------------------------------------------------
    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(self, fg_color="#1e222b", segmented_button_selected_color="#00b4d8")
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 5))

        self.tab_feed = self.tabview.add("🎬 Son Yüklenenler (Akış)")
        self.tab_tracked = self.tabview.add("📋 Takip Listesi")
        self.tab_search = self.tabview.add("🔍 Nyaa Hızlı Arama")
        self.tab_settings = self.tabview.add("⚙️ Ayarlar")

        self._setup_feed_tab()
        self._setup_tracked_tab()
        self._setup_search_tab()
        self._setup_settings_tab()

    # -------------------------------------------------------------
    # Sekme 1: Son Yüklenenler (Akış / Feed)
    # -------------------------------------------------------------
    def _setup_feed_tab(self):
        top_bar = ctk.CTkFrame(self.tab_feed, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=8)

        search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="🔎 Gelen bölümlerde filtrele...",
            textvariable=self.search_filter_var,
            width=320,
            height=34
        )
        search_entry.pack(side="left")

        btn_clear = ctk.CTkButton(
            top_bar,
            text="Geçmişi Temizle",
            fg_color="#334155",
            hover_color="#475569",
            width=130,
            height=34,
            command=self.action_clear_feed
        )
        btn_clear.pack(side="right", padx=5)

        self.feed_scroll = ctk.CTkScrollableFrame(self.tab_feed, fg_color="#13161c", corner_radius=8)
        self.feed_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def refresh_feed(self):
        """Akış paneline geçmiş yüklemeleri doldurur."""
        for child in self.feed_scroll.winfo_children():
            child.destroy()

        releases = self.config_manager.get_recent_releases()[:40]
        filter_text = self.search_filter_var.get().lower().strip()

        matched_count = 0
        for rel in releases:
            title = rel.get("title", "")
            anime = rel.get("matched_anime", "")
            if filter_text and filter_text not in title.lower() and filter_text not in anime.lower():
                continue

            matched_count += 1
            self._create_release_card(rel)

        if matched_count == 0:
            empty_lbl = ctk.CTkLabel(
                self.feed_scroll,
                text="📭 Henüz takip ettiğiniz animelerle eşleşen yeni bir yükleme yok.\nTakip listesini kontrol edebilir veya 'Şimdi Kontrol Et' butonuna basabilirsiniz.",
                font=ctk.CTkFont(size=14),
                text_color="#64748b"
            )
            empty_lbl.pack(pady=60)

    def filter_feed(self):
        self.refresh_feed()

    def _create_release_card(self, rel: Dict[str, Any]):
        card = ctk.CTkFrame(self.feed_scroll, fg_color="#1c212c", corner_radius=8)
        card.pack(fill="x", pady=5, padx=5)

        # Üst Etiketler Satırı
        badge_row = ctk.CTkFrame(card, fg_color="transparent")
        badge_row.pack(fill="x", padx=12, pady=(10, 4))

        anime_name = rel.get("matched_anime") or "Anime"
        anime_badge = ctk.CTkLabel(
            badge_row, 
            text=f" 🎯 {anime_name} ", 
            fg_color="#0369a1", 
            text_color="#ffffff",
            corner_radius=4,
            font=ctk.CTkFont(size=11, weight="bold")
        )
        anime_badge.pack(side="left", padx=(0, 6))

        group = rel.get("group")
        if group:
            grp_badge = ctk.CTkLabel(
                badge_row, 
                text=f" 👥 {group} ", 
                fg_color="#6366f1", 
                text_color="#ffffff",
                corner_radius=4,
                font=ctk.CTkFont(size=11)
            )
            grp_badge.pack(side="left", padx=(0, 6))

        res = rel.get("resolution")
        if res:
            res_badge = ctk.CTkLabel(
                badge_row, 
                text=f" 📺 {res.upper()} ", 
                fg_color="#10b981", 
                text_color="#ffffff",
                corner_radius=4,
                font=ctk.CTkFont(size=11, weight="bold")
            )
            res_badge.pack(side="left", padx=(0, 6))

        size_badge = ctk.CTkLabel(
            badge_row, 
            text=f" 📦 {rel.get('size', '')} ", 
            fg_color="#334155", 
            text_color="#cbd5e1",
            corner_radius=4,
            font=ctk.CTkFont(size=11)
        )
        size_badge.pack(side="left", padx=(0, 6))

        time_lbl = ctk.CTkLabel(
            badge_row,
            text=f"🕒 {rel.get('detected_at', '')}",
            text_color="#64748b",
            font=ctk.CTkFont(size=11)
        )
        time_lbl.pack(side="right")

        # Orta Bölüm: Başlık
        title_lbl = ctk.CTkLabel(
            card,
            text=rel.get("title", ""),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#f1f5f9",
            anchor="w",
            wraplength=700,
            justify="left"
        )
        title_lbl.pack(fill="x", padx=12, pady=(2, 6))

        # Alt Satır: Seed/Leech + İşlem Butonları
        bottom_row = ctk.CTkFrame(card, fg_color="transparent")
        bottom_row.pack(fill="x", padx=12, pady=(0, 10))

        seed_str = f"🟢 {rel.get('seeders', '0')} seed  |  🔴 {rel.get('leechers', '0')} leech"
        seed_lbl = ctk.CTkLabel(bottom_row, text=seed_str, text_color="#94a3b8", font=ctk.CTkFont(size=12))
        seed_lbl.pack(side="left")

        # Butonlar
        magnet_btn = ctk.CTkButton(
            bottom_row,
            text="🧲 Magnet Aç",
            fg_color="#059669",
            hover_color="#047857",
            width=100,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda m=rel.get("magnet_link"): self.open_magnet(m)
        )
        magnet_btn.pack(side="right", padx=3)

        torrent_btn = ctk.CTkButton(
            bottom_row,
            text="📥 İndir (.torrent)",
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=110,
            height=28,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda u=rel.get("torrent_url"), t=rel.get("title", ""): self.action_download_torrent(u, t)
        )
        torrent_btn.pack(side="right", padx=3)

        nyaa_btn = ctk.CTkButton(
            bottom_row,
            text="🌐 Nyaa",
            fg_color="#475569",
            hover_color="#334155",
            width=70,
            height=28,
            font=ctk.CTkFont(size=11),
            command=lambda u=rel.get("page_url"): self.open_url(u)
        )
        nyaa_btn.pack(side="right", padx=3)

        copy_btn = ctk.CTkButton(
            bottom_row,
            text="📋",
            fg_color="#334155",
            hover_color="#1e293b",
            width=36,
            height=28,
            command=lambda t=rel.get("title", ""): self.copy_to_clipboard(t)
        )
        copy_btn.pack(side="right", padx=3)

    # -------------------------------------------------------------
    # Sekme 2: Takip Listesi (Animelerim)
    # -------------------------------------------------------------
    def _setup_tracked_tab(self):
        top_bar = ctk.CTkFrame(self.tab_tracked, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=8)

        btn_add = ctk.CTkButton(
            top_bar,
            text="➕ Yeni Anime Ekle",
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=160,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.show_add_anime_modal
        )
        btn_add.pack(side="left")

        self.tracked_count_lbl = ctk.CTkLabel(
            top_bar,
            textvariable=self.active_count_var,
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        )
        self.tracked_count_lbl.pack(side="right", padx=10)

        self.tracked_scroll = ctk.CTkScrollableFrame(self.tab_tracked, fg_color="#13161c", corner_radius=8)
        self.tracked_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def load_tracked_anime_list(self):
        """Takip edilen anime listesini UI'de listeler."""
        for child in self.tracked_scroll.winfo_children():
            child.destroy()

        anime_list = self.config_manager.get_anime_list()
        if not anime_list:
            empty_lbl = ctk.CTkLabel(
                self.tracked_scroll,
                text="📝 Takip listeniz şu an boş.\nYukarıdaki '➕ Yeni Anime Ekle' butonuna basarak çevirdiğiniz animeleri ekleyin!",
                font=ctk.CTkFont(size=14),
                text_color="#64748b"
            )
            empty_lbl.pack(pady=60)
            self._update_stats()
            return

        for anime in anime_list:
            self._create_tracked_anime_item(anime)

        self._update_stats()

    def _create_tracked_anime_item(self, anime: Dict[str, Any]):
        item_frame = ctk.CTkFrame(self.tracked_scroll, fg_color="#1c212c", corner_radius=8)
        item_frame.pack(fill="x", pady=4, padx=5)

        # Sol Bilgiler
        info_box = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_box.pack(side="left", fill="both", expand=True, padx=12, pady=10)

        title_lbl = ctk.CTkLabel(
            info_box,
            text=anime.get("name", ""),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff",
            anchor="w"
        )
        title_lbl.pack(anchor="w")

        # Filtre etiketleri
        meta_box = ctk.CTkFrame(info_box, fg_color="transparent")
        meta_box.pack(anchor="w", pady=(4, 0))

        qual = anime.get("quality", "Hepsi")
        q_color = "#10b981" if qual != "Hepsi" else "#475569"
        q_lbl = ctk.CTkLabel(
            meta_box, 
            text=f" Çözünürlük: {qual} ", 
            fg_color=q_color, 
            corner_radius=4, 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#ffffff"
        )
        q_lbl.pack(side="left", padx=(0, 6))

        grp = anime.get("group", "")
        if grp:
            g_lbl = ctk.CTkLabel(
                meta_box, 
                text=f" Grup: {grp} ", 
                fg_color="#6366f1", 
                corner_radius=4, 
                font=ctk.CTkFont(size=10),
                text_color="#ffffff"
            )
            g_lbl.pack(side="left", padx=(0, 6))

        cat_names = {"1_0": "Tüm Anime", "1_2": "İngilizce Altyazılı", "1_4": "Ham / Raw", "1_3": "Diğer Diller"}
        cat_str = cat_names.get(anime.get("category", "1_0"), "Anime")
        c_lbl = ctk.CTkLabel(
            meta_box, 
            text=f" Kategori: {cat_str} ", 
            fg_color="#334155", 
            corner_radius=4, 
            font=ctk.CTkFont(size=10),
            text_color="#cbd5e1"
        )
        c_lbl.pack(side="left")

        # Sağ Butonlar
        action_box = ctk.CTkFrame(item_frame, fg_color="transparent")
        action_box.pack(side="right", padx=12, pady=10)

        # Aktif/Pasif switch
        is_active = anime.get("is_active", True)
        switch_var = ctk.BooleanVar(value=is_active)
        switch = ctk.CTkSwitch(
            action_box,
            text="Aktif" if is_active else "Pasif",
            variable=switch_var,
            onvalue=True,
            offvalue=False,
            progress_color="#00b4d8",
            command=lambda aid=anime.get("id"), sv=switch_var, sw=None: self.toggle_anime_active(aid, sv)
        )
        switch.pack(side="left", padx=10)

        # Nyaa'da Canlı Test Butonu
        test_btn = ctk.CTkButton(
            action_box,
            text="🔍 Nyaa'da Ara",
            fg_color="#334155",
            hover_color="#475569",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            command=lambda a=anime: self.test_anime_on_nyaa(a)
        )
        test_btn.pack(side="left", padx=4)

        # Sil Butonu
        del_btn = ctk.CTkButton(
            action_box,
            text="🗑️ Sil",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            width=65,
            height=28,
            font=ctk.CTkFont(size=11),
            command=lambda aid=anime.get("id"): self.action_delete_anime(aid)
        )
        del_btn.pack(side="left", padx=4)

    def toggle_anime_active(self, anime_id: str, switch_var: ctk.BooleanVar):
        val = switch_var.get()
        self.config_manager.toggle_anime(anime_id, val)
        self.load_tracked_anime_list()

    def action_delete_anime(self, anime_id: str):
        if messagebox.askyesno("Onay", "Bu animeyi takip listesinden kaldırmak istediğinizden emin misiniz?"):
            self.config_manager.remove_anime(anime_id)
            self.load_tracked_anime_list()

    def test_anime_on_nyaa(self, anime: Dict[str, Any]):
        """Arama sekmesine geçip bu animenin sonuçlarını listeler."""
        self.tabview.set("🔍 Nyaa Hızlı Arama")
        self.search_entry.delete(0, "end")
        self.search_entry.insert(0, anime.get("name", ""))
        self.action_run_search()

    # Modal: Yeni Anime Ekle
    def show_add_anime_modal(self, prefill_title: str = ""):
        modal = ctk.CTkToplevel(self)
        modal.title("Yeni Anime Ekle")
        modal.geometry("520x460")
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        lbl_header = ctk.CTkLabel(modal, text="Yeni Anime Takibi Başlat", font=ctk.CTkFont(size=18, weight="bold"), text_color="#00b4d8")
        lbl_header.pack(pady=(20, 15))

        form_frame = ctk.CTkFrame(modal, fg_color="transparent")
        form_frame.pack(fill="x", padx=30)

        # Anime Adı
        ctk.CTkLabel(form_frame, text="Anime Adı (Nyaa arama ifadesi):", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", pady=(5, 2))
        entry_name = ctk.CTkEntry(form_frame, placeholder_text="Örn: Sousou no Frieren, One Piece, Bleach", height=35)
        entry_name.pack(fill="x")
        if prefill_title:
            entry_name.insert(0, prefill_title)

        # Alternatif İsim
        ctk.CTkLabel(form_frame, text="Alternatif İsim / İngilizce Ad (Opsiyonel):", font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(10, 2))
        entry_alias = ctk.CTkEntry(form_frame, placeholder_text="Örn: Frieren: Beyond Journey's End", height=35)
        entry_alias.pack(fill="x")

        # Çözünürlük & Grup Filtresi (Yan yana)
        filter_row = ctk.CTkFrame(form_frame, fg_color="transparent")
        filter_row.pack(fill="x", pady=(10, 0))

        box_qual = ctk.CTkFrame(filter_row, fg_color="transparent")
        box_qual.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ctk.CTkLabel(box_qual, text="Kalite / Çözünürlük:").pack(anchor="w", pady=(0, 2))
        combo_quality = ctk.CTkComboBox(box_qual, values=["Hepsi", "1080p", "720p", "480p", "2160p"], height=35)
        combo_quality.set("1080p")
        combo_quality.pack(fill="x")

        box_grp = ctk.CTkFrame(filter_row, fg_color="transparent")
        box_grp.pack(side="left", fill="x", expand=True, padx=(5, 0))
        ctk.CTkLabel(box_grp, text="Çeviri Grubu (Opsiyonel):").pack(anchor="w", pady=(0, 2))
        entry_group = ctk.CTkEntry(box_grp, placeholder_text="Örn: SubsPlease, Erai-raws", height=35)
        entry_group.pack(fill="x")

        # Kategori
        ctk.CTkLabel(form_frame, text="Kategori:").pack(anchor="w", pady=(10, 2))
        combo_category = ctk.CTkComboBox(
            form_frame, 
            values=["İngilizce Altyazılı (1_2)", "Ham / Raw (1_4)", "Tüm Anime (1_0)", "Diğer Diller (1_3)"], 
            height=35
        )
        combo_category.set("İngilizce Altyazılı (1_2)")
        combo_category.pack(fill="x")

        # Kaydet Butonu
        def _save():
            name = entry_name.get().strip()
            if not name:
                messagebox.showerror("Hata", "Lütfen bir anime adı girin!")
                return
            
            alias = entry_alias.get().strip()
            quality = combo_quality.get().strip()
            group = entry_group.get().strip()
            cat_val = combo_category.get()
            cat_code = "1_2"
            if "1_0" in cat_val:
                cat_code = "1_0"
            elif "1_4" in cat_val:
                cat_code = "1_4"
            elif "1_3" in cat_val:
                cat_code = "1_3"

            self.config_manager.add_anime(name, quality=quality, group=group, category=cat_code, alias=alias)
            self.load_tracked_anime_list()
            modal.destroy()
            messagebox.showinfo("Başarılı", f"'{name}' takip listesine eklendi!")

        btn_save = ctk.CTkButton(
            modal, 
            text="Listeye Ekle ve Takibi Başlat", 
            fg_color="#0284c7", 
            hover_color="#0369a1", 
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=_save
        )
        btn_save.pack(pady=20, padx=30, fill="x")

    # -------------------------------------------------------------
    # Sekme 3: Nyaa Hızlı Arama
    # -------------------------------------------------------------
    def _setup_search_tab(self):
        top_bar = ctk.CTkFrame(self.tab_search, fg_color="transparent")
        top_bar.pack(fill="x", padx=10, pady=8)

        self.search_entry = ctk.CTkEntry(
            top_bar,
            placeholder_text="Nyaa.si üzerinde anime ara... (Örn: Frieren, Bleach, Dandadan)",
            width=400,
            height=36
        )
        self.search_entry.pack(side="left", padx=(0, 6))
        self.search_entry.bind("<Return>", lambda e: self.action_run_search())

        self.search_cat_combo = ctk.CTkComboBox(
            top_bar,
            values=["Anime - Tümü (1_0)", "Anime - İngilizce (1_2)", "Anime - Raw (1_4)"],
            width=180,
            height=36
        )
        self.search_cat_combo.set("Anime - İngilizce (1_2)")
        self.search_cat_combo.pack(side="left", padx=(0, 6))

        self.search_btn = ctk.CTkButton(
            top_bar,
            text="🔍 Ara",
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=100,
            height=36,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.action_run_search
        )
        self.search_btn.pack(side="left")

        self.search_scroll = ctk.CTkScrollableFrame(self.tab_search, fg_color="#13161c", corner_radius=8)
        self.search_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def action_run_search(self):
        query = self.search_entry.get().strip()
        if not query:
            return

        cat_choice = self.search_cat_combo.get()
        cat_code = "1_2"
        if "1_0" in cat_choice:
            cat_code = "1_0"
        elif "1_4" in cat_choice:
            cat_code = "1_4"

        # Yükleniyor durumu
        for child in self.search_scroll.winfo_children():
            child.destroy()
        loading_lbl = ctk.CTkLabel(self.search_scroll, text="⏳ Nyaa.si taranıyor, lütfen bekleyin...", font=ctk.CTkFont(size=14))
        loading_lbl.pack(pady=40)

        def _fetch():
            results = self.tracker.search_nyaa_rss(query, category=cat_code)
            self.after(0, lambda: self._display_search_results(results, query))

        threading.Thread(target=_fetch, daemon=True).start()

    def _display_search_results(self, results: List[Dict[str, Any]], query: str):
        for child in self.search_scroll.winfo_children():
            child.destroy()

        if not results:
            no_lbl = ctk.CTkLabel(
                self.search_scroll, 
                text=f"'{query}' için hiçbir yükleme bulunamadı.", 
                font=ctk.CTkFont(size=14),
                text_color="#ef4444"
            )
            no_lbl.pack(pady=40)
            return

        # Sonuç başlığı ve listeye ekleme kısayolu
        header_box = ctk.CTkFrame(self.search_scroll, fg_color="#1e222b", corner_radius=6)
        header_box.pack(fill="x", pady=(0, 8), padx=5)

        h_lbl = ctk.CTkLabel(
            header_box, 
            text=f"Toplam {len(results)} yükleme bulundu.", 
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#00b4d8"
        )
        h_lbl.pack(side="left", padx=10, pady=6)

        btn_track_this = ctk.CTkButton(
            header_box,
            text=f"➕ '{query}' Takip Listesine Ekle",
            fg_color="#0284c7",
            hover_color="#0369a1",
            height=30,
            command=lambda q=query: self.show_add_anime_modal(prefill_title=q)
        )
        btn_track_this.pack(side="right", padx=10, pady=6)

        for rel in results:
            self._create_search_item_card(rel)

    def _create_search_item_card(self, rel: Dict[str, Any]):
        card = ctk.CTkFrame(self.search_scroll, fg_color="#1c212c", corner_radius=8)
        card.pack(fill="x", pady=4, padx=5)

        # Üst satır
        top_box = ctk.CTkFrame(card, fg_color="transparent")
        top_box.pack(fill="x", padx=10, pady=(8, 2))

        group = rel.get("group")
        if group:
            grp_lbl = ctk.CTkLabel(top_box, text=f" [{group}] ", fg_color="#6366f1", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"))
            grp_lbl.pack(side="left", padx=(0, 5))

        res = rel.get("resolution")
        if res:
            res_lbl = ctk.CTkLabel(top_box, text=f" {res.upper()} ", fg_color="#10b981", corner_radius=4, font=ctk.CTkFont(size=10, weight="bold"))
            res_lbl.pack(side="left", padx=(0, 5))

        size_lbl = ctk.CTkLabel(top_box, text=f"📦 {rel.get('size')} | 🟢 {rel.get('seeders')} seed | 🔴 {rel.get('leechers')} leech", text_color="#94a3b8", font=ctk.CTkFont(size=11))
        size_lbl.pack(side="left")

        # Başlık
        title_lbl = ctk.CTkLabel(
            card,
            text=rel.get("title", ""),
            font=ctk.CTkFont(size=13),
            wraplength=720,
            anchor="w",
            justify="left"
        )
        title_lbl.pack(fill="x", padx=10, pady=(2, 6))

        # Butonlar
        btn_box = ctk.CTkFrame(card, fg_color="transparent")
        btn_box.pack(fill="x", padx=10, pady=(0, 8))

        magnet_btn = ctk.CTkButton(
            btn_box,
            text="🧲 Magnet Aç",
            fg_color="#059669",
            hover_color="#047857",
            width=90,
            height=26,
            font=ctk.CTkFont(size=11),
            command=lambda m=rel.get("magnet_link"): self.open_magnet(m)
        )
        magnet_btn.pack(side="right", padx=3)

        torrent_btn = ctk.CTkButton(
            btn_box,
            text="📥 İndir (.torrent)",
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=105,
            height=26,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda u=rel.get("torrent_url"), t=rel.get("title", ""): self.action_download_torrent(u, t)
        )
        torrent_btn.pack(side="right", padx=3)

        nyaa_btn = ctk.CTkButton(
            btn_box,
            text="🌐 Nyaa",
            fg_color="#475569",
            hover_color="#334155",
            width=65,
            height=26,
            font=ctk.CTkFont(size=11),
            command=lambda u=rel.get("page_url"): self.open_url(u)
        )
        nyaa_btn.pack(side="right", padx=3)

    # -------------------------------------------------------------
    # Sekme 4: Ayarlar
    # -------------------------------------------------------------
    def _setup_settings_tab(self):
        settings_frame = ctk.CTkScrollableFrame(self.tab_settings, fg_color="transparent")
        settings_frame.pack(fill="both", expand=True, padx=20, pady=15)

        settings = self.config_manager.get_settings()

        # 1. Kontrol Sıklığı
        ctk.CTkLabel(settings_frame, text="⏱️ Kontrol Sıklığı:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(10, 4))
        self.combo_interval = ctk.CTkComboBox(
            settings_frame,
            values=["1 dakika", "3 dakika", "5 dakika", "10 dakika", "15 dakika", "30 dakika", "60 dakika"],
            height=35,
            width=260
        )
        cur_inv = settings.get("check_interval_minutes", 5)
        self.combo_interval.set(f"{cur_inv} dakika")
        self.combo_interval.pack(anchor="w")

        # 2. Bildirim Tercihleri
        ctk.CTkLabel(settings_frame, text="🔔 Bildirim Ayarları:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(20, 6))

        self.sw_toast = ctk.CTkSwitch(
            settings_frame,
            text="Windows Masaüstü Bildirimi Göster (Toast / Banner)",
            progress_color="#00b4d8"
        )
        if settings.get("enable_desktop_notifications", True):
            self.sw_toast.select()
        self.sw_toast.pack(anchor="w", pady=4)

        self.sw_sound = ctk.CTkSwitch(
            settings_frame,
            text="Yeni bölüm gelince sesli uyarı çal (Chime)",
            progress_color="#00b4d8"
        )
        if settings.get("enable_sound_alerts", True):
            self.sw_sound.select()
        self.sw_sound.pack(anchor="w", pady=4)

        self.sw_auto_magnet = ctk.CTkSwitch(
            settings_frame,
            text="Yeni bölüm gelince Magnet'i torrent istemcisine otomatik gönder",
            progress_color="#00b4d8"
        )
        if settings.get("auto_open_magnet", False):
            self.sw_auto_magnet.select()
        self.sw_auto_magnet.pack(anchor="w", pady=4)

        self.sw_auto_download = ctk.CTkSwitch(
            settings_frame,
            text="Yeni bölüm gelince .torrent dosyasını otomatik bilgisayara indir ve başlat",
            progress_color="#00b4d8"
        )
        if settings.get("auto_download_torrent", False):
            self.sw_auto_download.select()
        self.sw_auto_download.pack(anchor="w", pady=4)

        btn_open_torrents = ctk.CTkButton(
            settings_frame,
            text="📁 İndirilen Torrentler Klasörünü Aç",
            fg_color="#334155",
            hover_color="#475569",
            width=260,
            height=32,
            font=ctk.CTkFont(size=12),
            command=self.action_open_torrent_dir
        )
        btn_open_torrents.pack(anchor="w", pady=(6, 4))

        self.sw_close_tray = ctk.CTkSwitch(
            settings_frame,
            text="Pencereyi kapatınca (X) arka planda sistem tepsisine küçült",
            progress_color="#00b4d8"
        )
        if settings.get("close_to_tray", True):
            self.sw_close_tray.select()
        self.sw_close_tray.pack(anchor="w", pady=4)

        # 3. Discord Webhook
        ctk.CTkLabel(settings_frame, text="💬 Discord Çeviri Grubu Bildirimi (Opsiyonel):", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", pady=(20, 4))
        ctk.CTkLabel(settings_frame, text="Çeviri ekibinizin Discord sunucusundaki kanala anlık bildirim göndermek için Webhook URL'sini yapıştırın:", font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(anchor="w", pady=(0, 6))

        self.sw_discord = ctk.CTkSwitch(
            settings_frame,
            text="Discord Webhook Bildirimini Etkinleştir",
            progress_color="#00b4d8"
        )
        if settings.get("enable_discord", False):
            self.sw_discord.select()
        self.sw_discord.pack(anchor="w", pady=4)

        discord_row = ctk.CTkFrame(settings_frame, fg_color="transparent")
        discord_row.pack(fill="x", pady=4)

        self.entry_webhook = ctk.CTkEntry(
            discord_row,
            placeholder_text="https://discord.com/api/webhooks/...",
            width=480,
            height=35
        )
        self.entry_webhook.pack(side="left", padx=(0, 10))
        if settings.get("discord_webhook_url"):
            self.entry_webhook.insert(0, settings.get("discord_webhook_url"))

        btn_test_webhook = ctk.CTkButton(
            discord_row,
            text="🚀 Webhook Test Et",
            fg_color="#475569",
            hover_color="#334155",
            height=35,
            command=self.action_test_discord
        )
        btn_test_webhook.pack(side="left")

        # Kaydet Butonu
        btn_save_settings = ctk.CTkButton(
            settings_frame,
            text="💾 Ayarları Kaydet",
            fg_color="#0284c7",
            hover_color="#0369a1",
            width=200,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.action_save_settings
        )
        btn_save_settings.pack(anchor="w", pady=(30, 20))

    def action_test_discord(self):
        url = self.entry_webhook.get().strip()
        if not url:
            messagebox.showwarning("Uyarı", "Lütfen önce geçerli bir Discord Webhook URL girin!")
            return

        def _test():
            ok = self.notifier.test_discord_webhook(url)
            if ok:
                self.after(0, lambda: messagebox.showinfo("Başarılı", "Test mesajı Discord kanalınıza başarıyla gönderildi! 🎉"))
            else:
                self.after(0, lambda: messagebox.showerror("Hata", "Test mesajı gönderilemedi! Webhook URL'sini kontrol edin."))

        threading.Thread(target=_test, daemon=True).start()

    def action_save_settings(self):
        inv_text = self.combo_interval.get().split()[0]
        try:
            inv = int(inv_text)
        except ValueError:
            inv = 5

        new_settings = {
            "check_interval_minutes": inv,
            "enable_desktop_notifications": bool(self.sw_toast.get()),
            "enable_sound_alerts": bool(self.sw_sound.get()),
            "enable_discord": bool(self.sw_discord.get()),
            "discord_webhook_url": self.entry_webhook.get().strip(),
            "close_to_tray": bool(self.sw_close_tray.get()),
            "auto_open_magnet": bool(self.sw_auto_magnet.get()),
            "auto_download_torrent": bool(self.sw_auto_download.get())
        }

        self.config_manager.update_settings(new_settings)
        messagebox.showinfo("Bilgi", "Ayarlar kaydedildi! Yeni kontrol aralığı devreye alındı.")

    # -------------------------------------------------------------
    # Durum Çubuğu (Status Bar)
    # -------------------------------------------------------------
    def _build_statusbar(self):
        status_bar = ctk.CTkFrame(self, fg_color="#181a20", height=32, corner_radius=0)
        status_bar.pack(fill="x", side="bottom")
        status_bar.pack_propagate(False)

        lbl_status = ctk.CTkLabel(
            status_bar,
            textvariable=self.status_text_var,
            font=ctk.CTkFont(size=11),
            text_color="#94a3b8"
        )
        lbl_status.pack(side="left", padx=15)

        lbl_credits = ctk.CTkLabel(
            status_bar,
            text="Anime Haber v1.0 • Anime Çeviri Asistanı",
            font=ctk.CTkFont(size=11),
            text_color="#64748b"
        )
        lbl_credits.pack(side="right", padx=15)

    def _update_stats(self):
        anime_list = self.config_manager.get_anime_list()
        active_count = len([a for a in anime_list if a.get("is_active", True)])
        self.active_count_var.set(f"{active_count} aktif anime takip ediliyor")

    # -------------------------------------------------------------
    # Tracker Geri Çağrımları (Thread-Safe)
    # -------------------------------------------------------------
    def _tracker_started(self):
        self.after(0, lambda: self._on_ui_tracker_started())

    def _on_ui_tracker_started(self):
        self.status_text_var.set("⏳ Nyaa.si taranıyor...")
        self.btn_check_now.configure(state="disabled", text="⏳ Kontrol Ediliyor...")

    def _tracker_completed(self, found_count: int, new_count: int):
        self.after(0, lambda: self._on_ui_tracker_completed(found_count, new_count))

    def _on_ui_tracker_completed(self, found_count: int, new_count: int):
        self.btn_check_now.configure(state="normal", text="🔄 Şimdi Kontrol Et")
        self.refresh_feed()
        self._update_stats()

    def _tracker_new_release(self, release: Dict[str, Any]):
        pass

    def _tracker_status_update(self, msg: str):
        self.after(0, lambda: self.status_text_var.set(msg))

    # -------------------------------------------------------------
    # Eylemler (Aksiyonlar)
    # -------------------------------------------------------------
    def action_check_now(self):
        self.tracker.trigger_check_now()

    def action_clear_feed(self):
        if messagebox.askyesno("Onay", "Tüm tespit geçmişi temizlensin mi?"):
            self.config_manager.clear_history()
            self.refresh_feed()

    def open_magnet(self, magnet_link: str):
        if not magnet_link:
            messagebox.showwarning("Uyarı", "Bu yükleme için magnet linki bulunamadı.")
            return
        try:
            open_path_or_url(magnet_link)
        except Exception as e:
            webbrowser.open(magnet_link)

    def open_url(self, url: str):
        if url:
            webbrowser.open(url)

    def copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Kopyalandı", "Başlık panoya kopyalandı!")

    def action_download_torrent(self, torrent_url: str, title: str):
        if not torrent_url:
            messagebox.showwarning("Uyarı", "Bu yükleme için torrent indirme bağlantısı bulunamadı.")
            return

        def _do_download():
            path = self.tracker.download_torrent_file(torrent_url, title, open_after=True)
            if path:
                fname = os.path.basename(path)
                self.after(0, lambda: messagebox.showinfo("Torrent İndirildi", f"✅ .torrent dosyası başarıyla indirildi ve torrent istemcinizde açıldı!\n\nDosya: {fname}\nKonum: {os.path.dirname(path)}"))
            else:
                self.after(0, lambda: messagebox.showerror("Hata", "Torrent dosyası indirilemedi. Nyaa bağlantısını kontrol edin."))

        threading.Thread(target=_do_download, daemon=True).start()

    def action_open_torrent_dir(self):
        d = self.config_manager.get_torrent_dir()
        try:
            open_path_or_url(d)
        except Exception:
            webbrowser.open(f"file:///{d}")

    # -------------------------------------------------------------
    # Pencere Gizleme / Gösterme & Çıkış
    # -------------------------------------------------------------
    def on_close_requested(self):
        settings = self.config_manager.get_settings()
        if settings.get("close_to_tray", True) and self.tray_manager:
            self.withdraw()  # Pencereyi gizle
            self.notifier.send_desktop_notification(
                {"title": "Anime Haber Arka Planda Çalışıyor", "size": "", "seeders": "Tepsi simgesinden açabilirsiniz."},
                "Bilgilendirme"
            )
        else:
            self.quit_application()

    def restore_window(self):
        self.after(0, self._do_restore)

    def _do_restore(self):
        self.deiconify()
        self.lift()
        self.focus_force()

    def quit_application(self):
        self.tracker.stop()
        if self.tray_manager:
            self.tray_manager.stop()
        self.destroy()
        sys.exit(0)
