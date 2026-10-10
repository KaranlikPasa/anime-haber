# Masaüstüne Anime Haber kısayolu oluşturur
$WshShell = New-Object -ComObject WScript.Shell
$Desktop = [System.Environment]::GetFolderPath('Desktop')
$ShortcutPath = Join-Path -Path $Desktop -ChildPath "Anime Haber.lnk"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

$ProjectDir = "D:\projeler\anime haber"
$Shortcut.TargetPath = Join-Path -Path $ProjectDir -ChildPath "arkaplanda_baslat.vbs"
$Shortcut.WorkingDirectory = $ProjectDir
$Shortcut.Description = "Anime Haber - Nyaa.si Yeni Bölüm Takipçisi"
$Shortcut.Save()

Write-Host "Masaüstüne kısayol başarıyla oluşturuldu: $ShortcutPath" -ForegroundColor Green
