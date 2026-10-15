"""
Command-Line Interface for BT-DualBoot Tools.
Provides dry-run preview, atomic key synchronization, backup, and rollback capabilities.
"""

import os
import sys
import argparse
from typing import List, Optional

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

if __package__ is None or __package__ == "":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bt_dualboot import __version__
from bt_dualboot.core.registry import parse_export_json, BluetoothAdapter
from bt_dualboot.core.bluez import plan_device_sync, apply_device_sync, restart_bluetooth_service, check_connected_devices
from bt_dualboot.utils.backup import create_backup, list_backups, rollback_backup


class Style:
    """Terminal styling helper respecting NO_COLOR environment variable and --no-color flag."""

    def __init__(self, disabled: bool = False):
        no_color_env = bool(os.environ.get("NO_COLOR"))
        self.disabled = disabled or no_color_env
        self.CYAN = "" if self.disabled else "\033[96m"
        self.GREEN = "" if self.disabled else "\033[92m"
        self.YELLOW = "" if self.disabled else "\033[93m"
        self.RED = "" if self.disabled else "\033[91m"
        self.BOLD = "" if self.disabled else "\033[1m"
        self.DIM = "" if self.disabled else "\033[2m"
        self.RESET = "" if self.disabled else "\033[0m"


def mask_key(key: Optional[str], show_full: bool = False) -> str:
    """Masks cryptographic key to avoid shoulder-surfing and accidental log exposure."""
    if not key:
        return ""
    if show_full or len(key) <= 8:
        return key
    return f"{key[:4]}...{key[-4:]}"


def print_banner(style: Style):
    banner = f"""{style.CYAN}{style.BOLD}
+--------------------------------------------------------------+
|                BT-DualBoot Tools v{__version__}                         |
|   Seamless Bluetooth Key Sync Between Windows and Linux (BlueZ)|
+--------------------------------------------------------------+{style.RESET}
"""
    print(banner)


def print_novice_guidance(style: Style, reason: str = ""):
    """Prints friendly, foolproof guidance for users who have not yet exported keys from Windows."""
    border = "=" * 70
    print(f"\n{style.YELLOW}{border}{style.RESET}")
    print(f" {style.BOLD}🛑 HENÜZ WINDOWS'TAN 'btkeys.json' ALINMAMIŞ VEYA BOŞ GÖRÜNÜYOR!{style.RESET}")
    print(f"{style.YELLOW}{border}{style.RESET}")
    if reason:
        print(f" {style.RED}Neden:{style.RESET} {reason}\n")
    print(f" {style.CYAN}ℹ️  Bluetooth anahtarları 128-bit donanım şifreleridir, ELLE YAZILAMAZ.{style.RESET}")
    print("    Bu anahtarları Windows ve Linux eşleşme anında kendisi üretir.\n")
    print(f" {style.BOLD}👉 2 DAKİKADA ÇÖZÜM (Ne Yapmalısınız?):{style.RESET}")
    print("  1. Bilgisayarınızı yeniden başlatıp WINDOWS'a geçin.")
    print("  2. Klavyenizi veya farenizi Windows Bluetooth ayarlarından eşleştirin.")
    print(f"  3. Projedeki {style.BOLD}'Export-Keys.bat'{style.RESET} (veya windows\\Export-Keys.bat) dosyasına çift tıklayın.")
    print("     -> Klasörde otomatik olarak 'btkeys.json' oluşacaktır.")
    print("  4. Bu 'btkeys.json' dosyasını bir USB belleğe atın.")
    print("  5. Tekrar Linux'a geçip:")
    print("     - Ya 'btkeys.json' dosyasını bu proje klasörüne kopyalayın,")
    print(f"     - Ya da 'sudo python sync.py' çalıştırıp dosyayı {style.BOLD}fareyle terminale sürükleyin!{style.RESET}")
    print(f"{style.YELLOW}{border}{style.RESET}\n")


def check_privileges(base_path: str, dry_run: bool, style: Style) -> bool:
    """Checks if running as root on Linux when writing to default system path."""
    if dry_run:
        return True

    if base_path == "/var/lib/bluetooth":
        if os.name != "nt" and os.geteuid() != 0:
            print(f"{style.RED}[ERROR] Root privileges required to write to /var/lib/bluetooth.{style.RESET}")
            print(f"{style.YELLOW}Please run with: sudo bt-dualboot <arguments>{style.RESET}\n")
            return False
    return True


def list_devices_cmd(adapters: List[BluetoothAdapter], show_keys: bool, style: Style):
    """Displays all adapters and devices contained in the JSON file."""
    print(f"{style.BOLD}Found {len(adapters)} Bluetooth Adapter(s) in export:{style.RESET}\n")
    for a in adapters:
        print(f" {style.CYAN}* Adapter:{style.RESET} {style.BOLD}{a.adapter_mac}{style.RESET}")
        for d in a.devices:
            print(f"   |-- Device: {style.BOLD}{d.name}{style.RESET}")
            print(f"   |   MAC:    {d.mac}")
            if d.key:
                key_display = d.key if show_keys else mask_key(d.key)
                print(f"   |   Classic Key: {style.DIM}{key_display}{style.RESET}")
            if d.ble:
                ltk_disp = d.ble.ltk if show_keys else mask_key(d.ble.ltk)
                print(f"   |   BLE LTK:     {style.DIM}{ltk_disp}{style.RESET}")
                print(f"   |   BLE Rand:    {d.ble.rand} (Reversed from: {d.ble.erand_raw})")
                print(f"   |   BLE EDiv:    {d.ble.ediv}")
        print()


def handle_rollback(backup_arg: str, target_dir: str, style: Style) -> int:
    """Executes a rollback operation to restore a previous BlueZ configuration."""
    print_banner(style)
    if backup_arg == "latest":
        backups = list_backups(os.path.dirname(os.path.abspath(target_dir)))
        if not backups:
            print(f"{style.RED}[ERROR] No backups found to roll back.{style.RESET}")
            return 1
        target_backup = backups[0]
    else:
        target_backup = backup_arg

    print(f"{style.YELLOW}[*] Restoring BlueZ configuration from: {target_backup}{style.RESET}")
    success = rollback_backup(target_backup, target_dir)
    if success:
        print(f"{style.GREEN}[SUCCESS] Rollback completed successfully.{style.RESET}")
        restart_bluetooth_service()
        return 0
    else:
        print(f"{style.RED}[ERROR] Failed to restore backup.{style.RESET}")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="BT-DualBoot Tools: Sync Windows Bluetooth pairing keys with Linux BlueZ.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "json_path",
        nargs="?",
        default="btkeys.json",
        help="Path to btkeys.json file (default: ./btkeys.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the sync process without modifying any system files.",
    )
    parser.add_argument(
        "--bluez-path",
        default="/var/lib/bluetooth",
        help="Path to BlueZ storage directory (default: /var/lib/bluetooth).",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip automatic BlueZ configuration backup.",
    )
    parser.add_argument(
        "--no-restart",
        action="store_true",
        help="Skip restarting the bluetooth daemon after update.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List devices and keys inside the JSON file without applying anything.",
    )
    parser.add_argument(
        "--show-keys",
        action="store_true",
        help="Display full unmasked cryptographic keys in terminal outputs.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colors in terminal output (NO_COLOR compliance).",
    )
    parser.add_argument(
        "--rollback",
        nargs="?",
        const="latest",
        help="Restore previous BlueZ backup ('latest' or specific directory path).",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"BT-DualBoot Tools {__version__}",
    )

    args = parser.parse_args(argv)
    style = Style(disabled=args.no_color)

    # Handle rollback
    if args.rollback:
        return handle_rollback(args.rollback, args.bluez_path, style)

    print_banner(style)

    # Check Windows notice
    if os.name == "nt" and args.bluez_path == "/var/lib/bluetooth" and not args.dry_run and not args.list:
        print(f"{style.YELLOW}[NOTE] You are running on Windows.{style.RESET}")
        print(
            "To EXPORT keys from Windows, run PowerShell as Administrator:\n"
            f"  {style.CYAN}.\\windows\\Export-BluetoothKeys.ps1{style.RESET}\n"
        )
        print("To test the synchronization logic on Windows, use `--dry-run` or specify `--bluez-path`.\n")

    # Load JSON
    if not os.path.exists(args.json_path):
        print(f"{style.RED}[ERROR] Key export file not found: {args.json_path}{style.RESET}")
        print_novice_guidance(style, f"'{args.json_path}' dosyası bulunamadı.")
        return 1

    try:
        if os.path.isfile(args.json_path) and os.path.getsize(args.json_path) == 0:
            print(f"{style.RED}[ERROR] Key export file is empty: {args.json_path}{style.RESET}")
            print_novice_guidance(style, f"'{args.json_path}' dosyası tamamen boş (0 byte).")
            return 1
    except OSError:
        pass

    try:
        adapters = parse_export_json(args.json_path)
    except Exception as e:
        print(f"{style.RED}[ERROR] Failed to parse {args.json_path}: {e}{style.RESET}")
        print_novice_guidance(style, f"'{args.json_path}' geçerli bir Bluetooth anahtar formatında değil (Elle şifre yazılmamalıdır).")
        return 1

    if not adapters:
        print(f"{style.YELLOW}[WARNING] No valid Bluetooth adapters or paired devices found in {args.json_path}.{style.RESET}")
        print_novice_guidance(style, f"'{args.json_path}' içinde eşleşmiş geçerli cihaz/anahtar bulunamadı.")
        return 1

    if args.list:
        list_devices_cmd(adapters, show_keys=args.show_keys, style=style)
        return 0

    # Check root privileges if actually applying
    if not check_privileges(args.bluez_path, args.dry_run, style):
        return 2

    if args.dry_run:
        print(f"{style.YELLOW}{style.BOLD}>>> SIMULATION MODE (--dry-run): No files will be modified <<<{style.RESET}\n")

    # Step 1: Inspection & Planning
    plans = []
    for adapter in adapters:
        for device in adapter.devices:
            plan = plan_device_sync(
                base_path=args.bluez_path,
                adapter_mac=adapter.adapter_mac,
                device_mac=device.mac,
                device_name=device.name,
                new_key=device.key,
                ble_data=device.ble,
            )
            plans.append(plan)

    # Print Inspection Table
    print(f"{style.BOLD}Synchronization Plan:{style.RESET}")
    print(f"{'Device Name':<24} {'Device MAC':<18} {'Status':<18} {'Details'}")
    print("-" * 75)

    will_update_count = 0
    synced_count = 0
    missing_count = 0

    for p in plans:
        if p.status == "WILL_UPDATE":
            status_str = f"{style.YELLOW}WILL UPDATE{style.RESET}"
            will_update_count += 1
        elif p.status == "ALREADY_SYNCED":
            status_str = f"{style.GREEN}IN SYNC{style.RESET}"
            synced_count += 1
        else:
            status_str = f"{style.RED}{p.status}{style.RESET}"
            missing_count += 1

        details = p.message
        if p.status == "WILL_UPDATE" and p.old_key:
            old_k = p.old_key if args.show_keys else mask_key(p.old_key)
            new_k = p.new_key if args.show_keys else mask_key(p.new_key)
            details = f"Key: {old_k} -> {new_k}"
        elif p.status == "WILL_UPDATE" and not p.old_key:
            details = "New [LinkKey] section"

        print(f"{p.device_name[:23]:<24} {p.device_mac:<18} {status_str:<27} {details}")

    print("-" * 75)
    print(
        f"Summary: {style.GREEN}{synced_count} already synced{style.RESET}, "
        f"{style.YELLOW}{will_update_count} to update{style.RESET}, "
        f"{style.RED}{missing_count} not found in Linux{style.RESET}\n"
    )

    if will_update_count == 0:
        print(f"{style.GREEN}[SUCCESS] All found devices are already synchronized! Nothing to do.{style.RESET}\n")
        return 0

    if args.dry_run:
        print(f"{style.YELLOW}[DRY-RUN COMPLETE] Run without --dry-run to apply these updates.{style.RESET}\n")
        return 0

    # Step 2: Automated Snapshot Backup
    if not args.no_backup:
        print("[*] Creating automatic BlueZ configuration backup...")
        backup_dir = create_backup(args.bluez_path)
        if backup_dir:
            print(f"{style.GREEN}[SUCCESS] Snapshot saved to: {backup_dir}{style.RESET}")
        else:
            print(f"{style.YELLOW}[WARNING] Could not create snapshot backup. Proceeding with caution...{style.RESET}")

    # Step 3: Apply Updates
    applied_count = 0
    for p in plans:
        if p.status == "WILL_UPDATE":
            if apply_device_sync(p):
                applied_count += 1
                print(f" {style.GREEN}[OK]{style.RESET} Updated {style.BOLD}{p.device_name}{style.RESET} ({p.device_mac})")
            else:
                print(f" {style.RED}[X]{style.RESET} Failed to update {style.BOLD}{p.device_name}{style.RESET}")

    # Step 4: Daemon Restart
    if applied_count > 0 and not args.no_restart:
        print("\n[*] Reloading Bluetooth service...")
        ok, msg = restart_bluetooth_service()
        if ok:
            print(f"{style.GREEN}[SUCCESS] {msg}{style.RESET}")
            # Step 5: Live Connection Verification (Linux)
            if os.name != "nt":
                import time
                time.sleep(1)
                connected_macs = check_connected_devices()
                print(f"\n{style.BOLD}Canlı Bağlantı Durumu:{style.RESET}")
                for p in plans:
                    if p.status == "WILL_UPDATE":
                        norm_m = p.device_mac.lower()
                        if any(norm_m == c for c in connected_macs):
                            print(f" {style.GREEN}✔ {p.device_name} -> ANINDA BAĞLANDI! 🎉{style.RESET}")
                        else:
                            print(f" {style.CYAN}⚡ {p.device_name} -> Anahtar hazır (Cihaz açıldığında otomatik bağlanacak){style.RESET}")
        else:
            print(f"{style.YELLOW}[WARNING] {msg}{style.RESET}")

    print(f"\n{style.GREEN}{style.BOLD}[DONE] Successfully synchronized {applied_count} device(s)!{style.RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
