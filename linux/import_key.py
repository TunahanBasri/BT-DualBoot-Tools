# import_key.py
# Part of BT DualBoot Tools
#
# Description: Imports Bluetooth keys from btkeys.json into BlueZ configuration files.
#
# Usage: sudo python import_key.py [path_to_btkeys.json]
#
# Requirements: Must be run as root (sudo).

import os
import sys
import json
import subprocess
from backup import create_backup

def check_root():
    if os.name == 'nt':
        print("[ERROR] This script is designed for Linux systems only.")
        sys.exit(1)
    if os.geteuid() != 0:
        print("[ERROR] This script must be run as root (sudo).")
        sys.exit(1)

def find_device_dir(adapter_path, device_mac):
    device_mac_lower = device_mac.lower().replace(":", "")
    # Format MAC with colons if needed, e.g. 54:46:6b:00:09:fb
    formatted_mac = ":".join(device_mac_lower[i:i+2] for i in range(0, 12, 2))
    
    if not os.path.exists(adapter_path):
        return None
        
    for entry in os.listdir(adapter_path):
        entry_lower = entry.lower()
        # Match either 54:46:6b:00:09:fb or 54466b0009fb
        if entry_lower == formatted_mac or entry_lower == device_mac_lower or entry_lower.startswith(formatted_mac):
            return os.path.join(adapter_path, entry)
    return None

def update_info_file(info_path, device_data):
    if not os.path.exists(info_path):
        print(f"[WARNING] Info file does not exist: {info_path}. Skipping.")
        return False
        
    with open(info_path, 'r') as f:
        lines = f.readlines()
        
    new_lines = []
    current_section = None
    sections_present = set()
    
    # Track existing sections
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            sections_present.add(stripped[1:-1])
            
    updated_fields = set() # Set of tuples (section, key)
    
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if stripped.startswith('[') and stripped.endswith(']'):
            current_section = stripped[1:-1]
            new_lines.append(line)
            i += 1
            continue
            
        if '=' in line and not stripped.startswith('#') and not stripped.startswith(';'):
            key, val = line.split('=', 1)
            key = key.strip()
            
            if current_section == 'LinkKey' and device_data['type'] == 'Classic' and key == 'Key':
                new_lines.append(f"Key={device_data['key']}\n")
                updated_fields.add(('LinkKey', 'Key'))
                i += 1
                continue
                
            if current_section == 'LongTermKey' and device_data['type'] == 'LE':
                if key == 'Key' and 'ltk' in device_data:
                    new_lines.append(f"Key={device_data['ltk']}\n")
                    updated_fields.add(('LongTermKey', 'Key'))
                    i += 1
                    continue
                elif key == 'EDiv' and 'ediv' in device_data:
                    new_lines.append(f"EDiv={device_data['ediv']}\n")
                    updated_fields.add(('LongTermKey', 'EDiv'))
                    i += 1
                    continue
                elif key == 'Rand' and 'rand' in device_data:
                    new_lines.append(f"Rand={device_data['rand']}\n")
                    updated_fields.add(('LongTermKey', 'Rand'))
                    i += 1
                    continue
                    
            if current_section == 'IdentityResolvingKey' and device_data['type'] == 'LE' and key == 'Key' and 'irk' in device_data:
                new_lines.append(f"Key={device_data['irk']}\n")
                updated_fields.add(('IdentityResolvingKey', 'Key'))
                i += 1
                continue
                
            if current_section == 'LocalSignatureKey' and device_data['type'] == 'LE' and key == 'Key' and 'csrk' in device_data:
                new_lines.append(f"Key={device_data['csrk']}\n")
                updated_fields.add(('LocalSignatureKey', 'Key'))
                i += 1
                continue
                
        new_lines.append(line)
        i += 1

    # Append sections that were missing entirely
    if device_data['type'] == 'Classic':
        if 'LinkKey' not in sections_present:
            new_lines.append("\n[LinkKey]\n")
            new_lines.append(f"Key={device_data['key']}\n")
            new_lines.append("Type=0\n")
            new_lines.append("PINLength=0\n")
            
    elif device_data['type'] == 'LE':
        if 'LongTermKey' not in sections_present:
            new_lines.append("\n[LongTermKey]\n")
            new_lines.append(f"Key={device_data['ltk']}\n")
            if 'ediv' in device_data:
                new_lines.append(f"EDiv={device_data['ediv']}\n")
            if 'rand' in device_data:
                new_lines.append(f"Rand={device_data['rand']}\n")
            new_lines.append("Authenticated=0\n")
            new_lines.append("EncSize=16\n")
            
        if 'irk' in device_data and 'IdentityResolvingKey' not in sections_present:
            new_lines.append("\n[IdentityResolvingKey]\n")
            new_lines.append(f"Key={device_data['irk']}\n")
            
        if 'csrk' in device_data and 'LocalSignatureKey' not in sections_present:
            new_lines.append("\n[LocalSignatureKey]\n")
            new_lines.append(f"Key={device_data['csrk']}\n")

    # Write the updated config back
    with open(info_path, 'w') as f:
        f.writelines(new_lines)
    return True

def main():
    check_root()
    
    # 1. Parse JSON path
    json_path = 'btkeys.json'
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        
    if not os.path.exists(json_path):
        print(f"[ERROR] JSON file not found at: {json_path}")
        print("Usage: sudo python import_key.py [path_to_btkeys.json]")
        sys.exit(1)
        
    with open(json_path, 'r') as f:
        try:
            adapters_data = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON: {e}")
            sys.exit(1)
            
    # Handle single object vs list in root
    if isinstance(adapters_data, dict):
        adapters_data = [adapters_data]

    # 2. Run Backup
    backup_path = create_backup()
    if not backup_path:
        print("[ERROR] Aborting key import due to backup failure.")
        sys.exit(1)
        
    # 3. Update configurations
    success_count = 0
    fail_count = 0
    
    for adapter_obj in adapters_data:
        adapter_mac = adapter_obj.get('adapter')
        devices = adapter_obj.get('devices', [])
        
        if not adapter_mac or not devices:
            continue
            
        adapter_path = os.path.join('/var/lib/bluetooth', adapter_mac.lower())
        if not os.path.exists(adapter_path):
            # Try matching adapter MAC case insensitively
            found_adapter = None
            if os.path.exists('/var/lib/bluetooth'):
                for entry in os.listdir('/var/lib/bluetooth'):
                    if entry.lower() == adapter_mac.lower():
                        found_adapter = os.path.join('/var/lib/bluetooth', entry)
                        break
            if found_adapter:
                adapter_path = found_adapter
            else:
                print(f"[WARNING] Bluetooth adapter path not found: {adapter_path}")
                print("Make sure this Bluetooth adapter is configured on Linux.")
                continue

        print(f"\n[*] Processing adapter: {adapter_mac}")
        
        for dev in devices:
            dev_mac = dev.get('mac')
            dev_name = dev.get('name', 'Unknown')
            dev_type = dev.get('type')
            
            if not dev_mac:
                continue
                
            device_dir = find_device_dir(adapter_path, dev_mac)
            if not device_dir:
                print(f"  [SKIP] Device {dev_name} ({dev_mac}) directory not found under {adapter_path}")
                print(f"         Please pair the device in Linux first to generate config folders.")
                fail_count += 1
                continue
                
            info_file = os.path.join(device_dir, 'info')
            if not os.path.exists(info_file):
                print(f"  [SKIP] info file not found for {dev_name} at: {info_file}")
                fail_count += 1
                continue
                
            print(f"  [*] Updating {dev_name} ({dev_mac}) [{dev_type}]...")
            if update_info_file(info_file, dev):
                print(f"  [SUCCESS] Updated keys for {dev_name}")
                success_count += 1
            else:
                print(f"  [FAILED] Failed to update {dev_name}")
                fail_count += 1

    # 4. Restart Bluetooth Service
    if success_count > 0:
        print("\n[*] Restarting bluetooth systemd service to apply keys...")
        try:
            subprocess.run(["systemctl", "restart", "bluetooth"], check=True)
            print("[SUCCESS] Bluetooth service restarted successfully.")
        except Exception as e:
            print(f"[WARNING] Failed to restart bluetooth service: {e}")
            print("Please restart it manually with: sudo systemctl restart bluetooth")
            
    print(f"\n[DONE] Synchronization completed. Success: {success_count}, Failed/Skipped: {fail_count}")

if __name__ == "__main__":
    main()
