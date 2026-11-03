"""
create_user.py - Skapar en lokal användare i Windows 11.

Kräver att PowerShell körs som administratör.
Loggas i logs/ÅÅÅÅ_MM/skapa_anvandare_ÅÅÅÅ_MM_DD.log

!!! SÄKERHETSVARNING !!!
Lösenordet sparas i KLARTEXT (okrypterat) i loggfilen. Det är ett medvetet
beslut för detta skolprojekt, men får aldrig användas i en skarp miljö.
"""

import getpass
import os
import subprocess

from functions.logger import write_log

# Sätt miljövariabeln ADMIN_SCRIPT_DRYRUN=1 för att testa utan att ändra systemet
DRY_RUN = os.environ.get("ADMIN_SCRIPT_DRYRUN") == "1"


def _is_admin():
    """Returnerar True om skriptet körs med administratörsrättigheter."""
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


def create_user(run_by):
    """Frågar efter användarnamn och lösenord, skapar kontot och loggar det."""
    print("\n--- Skapa ny Windows-användare ---")

    if not DRY_RUN and not _is_admin():
        print("Fel: Du måste starta PowerShell som administratör för att skapa användare.")
        return

    username = input("Användarnamn: ").strip()
    if not username:
        print("Användarnamn får inte vara tomt.")
        return

    # getpass döljer lösenordet medan man skriver
    password = getpass.getpass("Lösenord: ")
    if not password:
        print("Lösenord får inte vara tomt.")
        return
    if password != getpass.getpass("Upprepa lösenord: "):
        print("Lösenorden matchar inte. Ingen användare skapades.")
        return

    # Användarnamn och lösenord skickas som miljövariabler till PowerShell,
    # så att specialtecken inte tolkas som kod (skyddar mot kommandoinjektion).
    ps_command = (
        "New-LocalUser -Name $env:NEW_USER "
        "-Password (ConvertTo-SecureString $env:NEW_PASS -AsPlainText -Force) "
        "-PasswordNeverExpires:$false -ErrorAction Stop | Out-Null; "
        "Add-LocalGroupMember -SID 'S-1-5-32-545' -Member $env:NEW_USER -ErrorAction Stop"
    )

    if DRY_RUN:
        print("[DRY RUN] Skulle ha skapat användaren (inget ändrades).")
        success, message = True, "Testkörning (DRY RUN) - ingen användare skapades på riktigt"
    else:
        env = dict(os.environ, NEW_USER=username, NEW_PASS=password)
        result = subprocess.run(["powershell", "-NoProfile", "-Command", ps_command],
                                env=env, capture_output=True, text=True)
        success = result.returncode == 0
        message = "Användaren skapades" if success else result.stderr.strip()

    if success:
        print(f"Användaren '{username}' skapades.")
        write_log(
            "skapa_anvandare", run_by, "Nytt konto skapat",
            {"Nytt användarnamn": username,
             "Lösenord": f"{password} (OKRYPTERAT)",
             "Resultat": message},
            warning="Lösenordet är sparat i klartext i denna loggfil.")
    else:
        print(f"Kunde inte skapa användaren: {message}")
        write_log("skapa_anvandare", run_by, "Misslyckades att skapa konto",
                  {"Försökt användarnamn": username, "Felmeddelande": message})

