#!/usr/bin/env python3
"""
BT-DualBoot Tools - Tek Tıkla Bluetooth Senkronizasyonu (Sync Shortcut & Interactive Wizard)
Kullanım:
  sudo python sync.py              -> İnteraktif Kolay Menü
  sudo python sync.py --dry-run    -> Doğrudan Simülasyon Modu
"""

import os
import sys

# Ensure UTF-8 output encoding across Windows/Linux terminals without charmap errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure src/ is on python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(SCRIPT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from bt_dualboot.cli import main, Style, print_banner, print_novice_guidance


def find_default_json() -> str:
    """Attempts to locate btkeys.json in current or surrounding directories."""
    candidates = [
        "btkeys.json",
        os.path.join(SCRIPT_DIR, "btkeys.json"),
        os.path.join(SCRIPT_DIR, "windows", "btkeys.json"),
        os.path.join(os.path.dirname(SCRIPT_DIR), "btkeys.json"),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return "btkeys.json"


def is_valid_btkeys_file(path: str) -> bool:
    """Checks if the file exists, is non-empty, and contains parseable adapters."""
    if not path or not os.path.isfile(path):
        return False
    try:
        if os.path.getsize(path) == 0:
            return False
        from bt_dualboot.core.registry import parse_export_json
        adapters = parse_export_json(path)
        return len(adapters) > 0
    except Exception:
        return False


def clean_file_path(path_str: str) -> str:
    """Cleans up drag-and-dropped file paths from various terminal emulators."""
    s = path_str.strip()
    if s.startswith("&"):
        s = s[1:].strip()
    s = s.strip("'\"")
    return os.path.expanduser(s)


def interactive_wizard():
    style = Style()
    print_banner(style)

    default_json = find_default_json()
    has_valid_json = is_valid_btkeys_file(default_json)

    from bt_dualboot.core.bluez import list_installed_bluez_devices
    bluez_path = os.environ.get("BLUEZ_PATH", "/var/lib/bluetooth")
    installed_devices = list_installed_bluez_devices(bluez_path)

    border = "=" * 70

    if has_valid_json:
        # Durum 3: Anahtar Paketi Hazır -> Doğrudan Senkronizasyon Menüsü
        print(f"{style.BOLD}Hızlı İşlem Menüsü (Anahtar Paketi Hazır):{style.RESET}")
        print(f" {style.GREEN}✔ Windows anahtar paketi tespit edildi:{style.RESET} {default_json}")
        if installed_devices:
            print(f" {style.CYAN}ℹ Linux BlueZ:{style.RESET} {len(installed_devices)} eşleşmiş cihaz hazır.")
            for dev in installed_devices:
                print(f"   └─ {dev['name']} ({dev['device']})")
        print()

        print(f" {style.CYAN}[1]{style.RESET} ⚡ {style.BOLD}Tek Tıkla Senkronizasyon (Önerilen){style.RESET}")
        print("     -> btkeys.json'ı okur, otomatik BlueZ yedeği alır,")
        print("        Classic & BLE anahtarlarını dönüştürüp senkronize eder.\n")

        print(f" {style.CYAN}[2]{style.RESET} 🔍 {style.BOLD}Güvenli Simülasyon (--dry-run){style.RESET}")
        print("     -> Sisteme dokunmadan hangi cihaz ve anahtarların değişeceğini listeler.\n")

        print(f" {style.CYAN}[3]{style.RESET} 📋 {style.BOLD}Eşleşen Cihazları ve Anahtarları Listele{style.RESET}")
        print("     -> JSON içindeki klavye, fare ve kulaklıkları görüntüler.\n")

        print(f" {style.CYAN}[4]{style.RESET} 🔄 {style.BOLD}Geri Al (Son BlueZ Yedeğini Geri Yükle){style.RESET}")
        print("     -> En son alınan snapshot yedeğine geri döner.\n")

        print(f" {style.CYAN}[0]{style.RESET} 🚪 Çıkış\n")

        try:
            choice = input(f"Seçiminiz {style.BOLD}[1]{style.RESET} (veya dosyayı doğrudan buraya sürükleyin): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nİşlem iptal edildi.")
            return 0

        cleaned_choice = clean_file_path(choice)
        if os.path.isfile(cleaned_choice) or cleaned_choice.lower().endswith(".json"):
            print(f"\n{style.GREEN}✔ Sürükleyip bıraktığınız dosya algılandı:{style.RESET} {cleaned_choice}\n")
            return main([cleaned_choice])

        if choice in ("", "1"):
            return main([default_json])
        elif choice == "2":
            return main([default_json, "--dry-run"])
        elif choice == "3":
            return main([default_json, "--list"])
        elif choice == "4":
            return main(["--rollback", "latest"])
        elif choice == "0":
            print("Çıkış yapıldı.")
            return 0
        else:
            print(f"{style.RED}Geçersiz seçim.{style.RESET}")
            return 1

    else:
        # Durum 1 veya 2: Henüz btkeys.json yok -> Durum Farkındalıklı Yol Gösterici
        print(f"{style.YELLOW}{border}{style.RESET}")
        if installed_devices:
            print(f" {style.BOLD}🧭 DURUM: LINUX HAZIR ✔ | WINDOWS ANAHTARI BEKLENİYOR ⏳{style.RESET}")
            print(f"{style.YELLOW}{border}{style.RESET}")
            print(f"  • Linux'ta eşleştirilmiş cihazlarınız tespit edildi:")
            for dev in installed_devices:
                print(f"    └─ {style.BOLD}{dev['name']}{style.RESET} (MAC: {dev['device']})")
            print(f"\n {style.BOLD}👉 ŞİMDİ NE YAPMALISINIZ?:{style.RESET}")
            print("   1. Bilgisayarı yeniden başlatıp WINDOWS'a geçin.")
            print("   2. Yukarıdaki cihazı Windows Bluetooth ayarlarından da bağlayın.")
            print(f"   3. Projedeki {style.BOLD}'Export-Keys.bat'{style.RESET} dosyasına çift tıklayın.")
            print("   4. Oluşan 'btkeys.json' dosyasını USB bellek ile Linux'a getirip bu ekrana sürükleyin!")
        else:
            print(f" {style.BOLD}🧭 DURUM: SIFIRDAN BAŞLANGIÇ REHBERİ (Henüz Cihaz Bağlanmamış){style.RESET}")
            print(f"{style.YELLOW}{border}{style.RESET}")
            print("  • Linux BlueZ'de henüz eşleşmiş bir Bluetooth klavye/fare bulunamadı.")
            print("  • Henüz Windows 'btkeys.json' anahtar dosyası da bulunamadı.\n")
            print(f" {style.BOLD}👉 DOĞRU SIRALAMA İLE 3 ADIMDA ÇİFT İŞLETİM SİSTEMİ EŞLEŞTİRME:{style.RESET}")
            print(f"   {style.CYAN}1. ŞU AN (Linux):{style.RESET}   Linux Bluetooth Ayarlarını açıp cihazınızı 1 kez bağlayın.")
            print("                      (Bu işlem Linux'un cihaz kimliğini tanıması için zorunludur)")
            print(f"   {style.CYAN}2. SONRA (Windows):{style.RESET} Bilgisayarı Windows'la açıp aynı cihazı orada da eşleştirin.")
            print("                      (Windows en güncel kriptografik şifreyi üretir)")
            print(f"   {style.CYAN}3. BİTİRİRKEN:{style.RESET}     Windows'ta 'Export-Keys.bat' çalıştırın, 'btkeys.json'ı")
            print("                      bu terminal ekranına sürükleyip senkronize edin!")

        print(f"{style.YELLOW}{border}{style.RESET}\n")

        print(f" {style.CYAN}[1]{style.RESET} 📂 {style.BOLD}Dosyayı Sürükle-Bırak / Yol Belirt{style.RESET} (Zaten USB'de 'btkeys.json' varsa)")
        print(f" {style.CYAN}[2]{style.RESET} 🔄 Geri Al (Son BlueZ Yedeğini Geri Yükle)")
        print(f" {style.CYAN}[0]{style.RESET} 🚪 Çıkış (Cihazımı önce Bluetooth ayarlarından bağlayacağım)\n")

        try:
            choice = input(f"Seçiminiz {style.BOLD}[1]{style.RESET} (veya dosyayı doğrudan buraya sürükleyin): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nİşlem iptal edildi.")
            return 0

        cleaned_choice = clean_file_path(choice)
        if os.path.isfile(cleaned_choice) or cleaned_choice.lower().endswith(".json"):
            print(f"\n{style.GREEN}✔ Sürükleyip bıraktığınız dosya algılandı:{style.RESET} {cleaned_choice}\n")
            return main([cleaned_choice])

        if choice in ("", "1"):
            print(f"\n   Dosyayı fareyle {style.BOLD}BU TERMİNAL EKRANINA SÜRÜKLEYİP BIRAKIN{style.RESET} (veya tam yolunu yazın):")
            try:
                val = input(f"   Dosya Yolu (veya İptal için Enter): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nİşlem iptal edildi.")
                return 0
            val_clean = clean_file_path(val)
            if val_clean:
                return main([val_clean])
            else:
                print(f"\n{style.YELLOW}İşlem iptal edildi. Lütfen önce adımları uygulayın.{style.RESET}\n")
                return 1
        elif choice == "2":
            return main(["--rollback", "latest"])
        elif choice == "0":
            print("Çıkış yapıldı.")
            return 0
        else:
            print(f"{style.RED}Geçersiz seçim.{style.RESET}")
            return 1


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(main(sys.argv[1:]))
    else:
        sys.exit(interactive_wizard())
