# Maintainer: KaranlikPasa <https://github.com/KaranlikPasa>
pkgname=anime-haber
pkgver=1.0.1
pkgrel=1
pkgdesc="Anime çevirmenleri için Nyaa.si yeni bölüm takip ve masaüstü bildirim otomasyonu"
arch=('any')
url="https://github.com/KaranlikPasa/anime-haber"
license=('MIT')
depends=('python' 'python-pillow' 'python-requests' 'tk' 'libnotify' 'xdg-utils')
optdepends=(
    'python-customtkinter: Modern arayüz bileşenleri'
    'python-pystray: Sistem tepsisi (system tray) simgesi'
)
provides=('anime-haber')
conflicts=('anime-haber')

package() {
    install -d "${pkgdir}/opt/anime-haber"
    cp -r "${srcdir}/.."/{config_manager.py,main.py,notifier.py,os_utils.py,tracker.py,tray.py,ui.py,icon.png,icon.ico,icons,anime-haber,run.sh,anime-haber.desktop,requirements.txt,README.md} "${pkgdir}/opt/anime-haber/" 2>/dev/null || \
    cp -r "${startdir}"/{config_manager.py,main.py,notifier.py,os_utils.py,tracker.py,tray.py,ui.py,icon.png,icon.ico,icons,anime-haber,run.sh,anime-haber.desktop,requirements.txt,README.md} "${pkgdir}/opt/anime-haber/"
    
    chmod -R 755 "${pkgdir}/opt/anime-haber"
    chmod +x "${pkgdir}/opt/anime-haber/anime-haber"
    chmod +x "${pkgdir}/opt/anime-haber/run.sh"

    # Wrapper executable
    install -d "${pkgdir}/usr/bin"
    ln -sf /opt/anime-haber/anime-haber "${pkgdir}/usr/bin/anime-haber"

    # Desktop entry
    install -Dm644 "${pkgdir}/opt/anime-haber/anime-haber.desktop" "${pkgdir}/usr/share/applications/anime-haber.desktop"

    # High-resolution icons
    for size in 16 32 48 64 128 256 512; do
        if [ -f "${pkgdir}/opt/anime-haber/icons/${size}x${size}.png" ]; then
            install -Dm644 "${pkgdir}/opt/anime-haber/icons/${size}x${size}.png" \
                "${pkgdir}/usr/share/icons/hicolor/${size}x${size}/apps/anime-haber.png"
        fi
    done
    if [ -f "${pkgdir}/opt/anime-haber/icon.png" ]; then
        install -Dm644 "${pkgdir}/opt/anime-haber/icon.png" "${pkgdir}/usr/share/pixmaps/anime-haber.png"
    fi
}
