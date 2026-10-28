#!/usr/bin/env bash
# ==============================================================================
# Anime Haber - Arch Linux & Linux Kurulum Betiği
# ==============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}======================================================${NC}"
echo -e "${CYAN}   📺 Anime Haber - Linux Kurulum Sihirbazı          ${NC}"
echo -e "${CYAN}======================================================${NC}"

if [ "$EUID" -ne 0 ]; then
  echo -e "${YELLOW}[Bilgi] Sistem geneline (/opt/anime-haber) kurulum için root yetkisi gereklidir.${NC}"
  echo -e "Yönetici şifreniz istenebilir..."
  exec sudo "$0" "$@"
fi

INSTALL_DIR="/opt/anime-haber"
BIN_LINK="/usr/bin/anime-haber"
DESKTOP_DIR="/usr/share/applications"
ICONS_BASE="/usr/share/icons/hicolor"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "\n${BLUE}1/4: Sistem Bağımlılıkları Kontrol Ediliyor...${NC}"

if command -v pacman >/dev/null 2>&1; then
    echo -e "${GREEN}Arch Linux tespit edildi. pacman ile bağımlılıklar kuruluyor...${NC}"
    pacman -S --noconfirm --needed python python-pillow python-requests tk libnotify xdg-utils
elif command -v apt-get >/dev/null 2>&1; then
    echo -e "${GREEN}Debian/Ubuntu tespit edildi. apt ile bağımlılıklar kuruluyor...${NC}"
    apt-get update && apt-get install -y python3 python3-pil python3-requests python3-tk libnotify-bin xdg-utils
elif command -v dnf >/dev/null 2>&1; then
    echo -e "${GREEN}Fedora tespit edildi. dnf ile bağımlılıklar kuruluyor...${NC}"
    dnf install -y python3 python3-pillow python3-requests python3-tkinter libnotify xdg-utils
fi

echo -e "${BLUE}Python kütüphaneleri kontrol ediliyor (customtkinter, pystray)...${NC}"
pip install --break-system-packages -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || \
pip install -r "$SCRIPT_DIR/requirements.txt" 2>/dev/null || true

echo -e "\n${BLUE}2/4: Uygulama Dosyaları $INSTALL_DIR Dizinine Kopyalanıyor...${NC}"
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/config_manager.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/main.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/notifier.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/os_utils.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/tracker.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/tray.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/ui.py" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/icon.png" "$INSTALL_DIR/" 2>/dev/null || true
cp -r "$SCRIPT_DIR/icon.ico" "$INSTALL_DIR/" 2>/dev/null || true
if [ -d "$SCRIPT_DIR/icons" ]; then
    cp -r "$SCRIPT_DIR/icons" "$INSTALL_DIR/"
fi
cp -r "$SCRIPT_DIR/anime-haber" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/run.sh" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/anime-haber.desktop" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
cp -r "$SCRIPT_DIR/README.md" "$INSTALL_DIR/" 2>/dev/null || true

chmod -R 755 "$INSTALL_DIR"
chmod +x "$INSTALL_DIR/anime-haber"
chmod +x "$INSTALL_DIR/run.sh"

echo -e "\n${BLUE}3/4: Sistem Başlatıcısı ve Masaüstü Kısayolu Oluşturuluyor...${NC}"
ln -sf "$INSTALL_DIR/anime-haber" "$BIN_LINK"

mkdir -p "$DESKTOP_DIR"
cp "$INSTALL_DIR/anime-haber.desktop" "$DESKTOP_DIR/anime-haber.desktop"
chmod 644 "$DESKTOP_DIR/anime-haber.desktop"

echo -e "\n${BLUE}4/4: Simgeler ve Önbellek Güncelleniyor...${NC}"
for size in 16 32 48 64 128 256 512; do
  if [ -f "$INSTALL_DIR/icons/${size}x${size}.png" ]; then
    mkdir -p "$ICONS_BASE/${size}x${size}/apps"
    cp "$INSTALL_DIR/icons/${size}x${size}.png" "$ICONS_BASE/${size}x${size}/apps/anime-haber.png"
  fi
done

if [ -f "$INSTALL_DIR/icon.png" ]; then
    mkdir -p /usr/share/pixmaps
    cp "$INSTALL_DIR/icon.png" /usr/share/pixmaps/anime-haber.png
fi

if command -v gtk-update-icon-cache >/dev/null 2>&1; then
  gtk-update-icon-cache -f -t "$ICONS_BASE" 2>/dev/null || true
fi
if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   ✅ Anime Haber Başarıyla Kuruldu!${NC}"
echo -e "${GREEN}======================================================${NC}"
echo -e "Uygulamayı çalıştırmak için:"
echo -e "  - Uygulama menünüzden ${CYAN}Anime Haber${NC} seçin"
echo -e "  - Veya terminalde doğrudan ${CYAN}anime-haber${NC} komutunu verin."
echo -e ""
echo -e "Kaldırmak isterseniz: ${YELLOW}sudo rm -rf /opt/anime-haber /usr/bin/anime-haber /usr/share/applications/anime-haber.desktop${NC}\n"
