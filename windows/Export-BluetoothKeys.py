# Export-BluetoothKeys.py
# Part of BT DualBoot Tools
#
# Description: Python wrapper that triggers the PowerShell export script on Windows.
#
# Usage: python Export-BluetoothKeys.py

import os
import sys
import subprocess
import ctypes

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_powershell_script():
    # Verify we are on Windows
    if sys.platform != 'win32':
        print("[ERROR] This script is only meant to be run on Windows.")
        sys.exit(1)

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ps_script_path = os.path.join(script_dir, "Export-BluetoothKeys.ps1")

    if not os.path.exists(ps_script_path):
        print(f"[ERROR] Could not find the PowerShell script at: {ps_script_path}")
        sys.exit(1)

    # PowerShell command to run our script
    cmd = [
        "powershell.exe",
        "-NoProfile",
        "-ExecutionPolicy", "Bypass",
        "-File", ps_script_path
    ]

    print("[*] Executing PowerShell export script...")
    try:
        # Run and stream the output to the console
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] PowerShell script exited with error: {e}")
        return e.returncode
    except Exception as e:
        print(f"[ERROR] Failed to run PowerShell: {e}")
        return 1

if __name__ == "__main__":
    if not is_admin():
        print("[*] Re-running script as Administrator...")
        # Re-run the script with admin rights
        # lpFile = sys.executable, lpParameters = current script path + arguments
        script = os.path.abspath(sys.argv[0])
        params = f'"{script}"'
        try:
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
            if int(ret) <= 32:
                print("[ERROR] User refused Administrator elevation.")
                sys.exit(1)
        except Exception as e:
            print(f"[ERROR] Failed to elevate: {e}")
            sys.exit(1)
    else:
        # We are admin, execute the PS script
        code = run_powershell_script()
        sys.exit(code)
