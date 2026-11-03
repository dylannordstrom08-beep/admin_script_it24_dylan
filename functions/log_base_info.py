"""
log_base_info.py - Loggar grundläggande information om datorn.

Använder endast Pythons standardbibliotek (inga externa paket behövs).
Resultatet sparas via logger.write_log i logs/ÅÅÅÅ_MM/grundinfo_ÅÅÅÅ_MM_DD.log
"""

import getpass
import os
import platform
import shutil
import socket
import subprocess
import uuid

from functions.logger import write_log


def _format_bytes(num_bytes):
    """Gör om bytes till läsbar text, t.ex. 15.9 GB."""
    return f"{num_bytes / (1024 ** 3):.1f} GB"


def _get_cpu_name():
    """Hämtar processorns namn. Använder PowerShell på Windows, annars platform."""
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "(Get-CimInstance Win32_Processor | Select-Object -First 1).Name"],
                capture_output=True, text=True, timeout=15)
            name = result.stdout.strip()
            if name:
                return name
        except (OSError, subprocess.SubprocessError):
            pass
    return platform.processor() or "Okänd"


def _get_ram():
    """Returnerar (totalt, ledigt) RAM i bytes, eller (None, None) om det inte går."""
    if platform.system() == "Windows":
        # Windows-API:t GlobalMemoryStatusEx via ctypes (inget extra paket krävs)
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        status = MEMORYSTATUSEX()
        status.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
        return status.ullTotalPhys, status.ullAvailPhys

    # Linux (används bara vid test): läs /proc/meminfo
    try:
        info = {}
        with open("/proc/meminfo") as f:
            for line in f:
                key, value = line.split(":")
                info[key] = int(value.split()[0]) * 1024
        return info["MemTotal"], info["MemAvailable"]
    except (OSError, KeyError, ValueError):
        return None, None


def _get_ip():
    """Hämtar datorns IP-adress (den som används mot nätverket)."""
    try:
        # UDP-socket skickar ingen data, används bara för att se vilken IP som väljs
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "Ingen nätverksanslutning hittades"


def _get_mac():
    """Hämtar MAC-adress formaterad som AA:BB:CC:DD:EE:FF."""
    mac = f"{uuid.getnode():012X}"
    return ":".join(mac[i:i + 2] for i in range(0, 12, 2))


def log_base_info(run_by):
    """Samlar in och loggar systemets grunddata. run_by = namn angivet i main."""
    print("\nSamlar in information om datorn...")

    ram_total, ram_free = _get_ram()
    # Minne = lagringsutrymme på systemdisken (C:\ på Windows)
    disk_path = os.path.abspath(os.sep)
    disk = shutil.disk_usage(disk_path)

    details = {
        "--- SYSTEM ---": "",
        "Datornamn": socket.gethostname(),
        "Inloggad Windows-användare": getpass.getuser(),
        "Operativsystem": f"{platform.system()} {platform.release()} ({platform.version()})",
        "Arkitektur": platform.machine(),
        "--- HÅRDVARA ---": "",
        "CPU": _get_cpu_name(),
        "RAM totalt": _format_bytes(ram_total) if ram_total else "Okänt",
        "RAM ledigt": _format_bytes(ram_free) if ram_free else "Okänt",
        f"Minne (disk {disk_path}) totalt": _format_bytes(disk.total),
        f"Minne (disk {disk_path}) ledigt": _format_bytes(disk.free),
        "--- NÄTVERK ---": "",
        "IP-adress": _get_ip(),
        "MAC-adress": _get_mac(),
    }

    log_file = write_log("grundinfo", run_by, "Grundläggande systeminformation loggad", details)

    for label, value in details.items():
        print(f"  {label} {value}".rstrip())
    print(f"\nLoggat i: {log_file}")
