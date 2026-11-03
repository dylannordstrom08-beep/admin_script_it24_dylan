"""
install_software.py - Laddar ner och installerar mjukvara med winget.

Program och grupper läses från config/software.json, så man kan ändra
vilken mjukvara som finns utan att ändra i koden (se README.md).
Loggas i logs/ÅÅÅÅ_MM/mjukvara_ÅÅÅÅ_MM_DD.log
"""

import json
import os
import shutil
import subprocess

from functions.logger import PROJECT_ROOT, write_log

CONFIG_FILE = os.path.join(PROJECT_ROOT, "config", "software.json")

# Sätt miljövariabeln ADMIN_SCRIPT_DRYRUN=1 för att testa utan att installera
DRY_RUN = os.environ.get("ADMIN_SCRIPT_DRYRUN") == "1"


def _load_config():
    """Läser software.json. Returnerar None med felmeddelande om filen är trasig."""
    try:
        with open(CONFIG_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError) as error:
        print(f"Kunde inte läsa {CONFIG_FILE}: {error}")
        return None


def _install_one(program):
    """Installerar ett program via winget. Returnerar (lyckades, meddelande)."""
    if DRY_RUN:
        print(f"  [DRY RUN] Skulle installera {program['name']}")
        return True, "Testkörning (DRY RUN) - inget installerades"

    if shutil.which("winget") is None:
        return False, "winget hittades inte på datorn"

    # -e = exakt id-matchning, --silent = ingen installationsdialog
    result = subprocess.run(
        ["winget", "install", "--id", program["winget_id"], "-e", "--silent",
         "--accept-package-agreements", "--accept-source-agreements"],
        text=True)
    if result.returncode == 0:
        return True, "Installationen lyckades"
    return False, f"winget avslutades med felkod {result.returncode}"


def _install_and_log(keys, programs, run_by, mode, group_name=None):
    """Installerar en lista program (nycklar i config) och loggar varje resultat."""
    for key in keys:
        program = programs.get(key)
        if program is None:
            print(f"  Hoppar över okänt program '{key}' (finns inte i software.json)")
            continue
        print(f"\nInstallerar {program['name']}...")
        success, message = _install_one(program)
        print(f"  {'OK' if success else 'MISSLYCKADES'}: {message}")

        details = {"Installationstyp": mode,
                   "Program": program["name"],
                   "winget-id": program["winget_id"],
                   "Resultat": message}
        if group_name:
            details["Grupp"] = group_name
        write_log("mjukvara", run_by,
                  "Mjukvara nedladdad och installerad" if success else "Installation misslyckades",
                  details)


def _choose(prompt, options):
    """Visar en numrerad lista och returnerar vald nyckel (eller None vid avbryt)."""
    for i, (_, label) in enumerate(options, start=1):
        print(f"  {i}. {label}")
    print("  0. Tillbaka")
    choice = input(prompt).strip()
    if choice.isdigit() and 1 <= int(choice) <= len(options):
        return options[int(choice) - 1][0]
    return None


def install_software(run_by):
    """Meny: installera enligt grupp eller individuellt program."""
    config = _load_config()
    if config is None:
        return
    programs, groups = config.get("programs", {}), config.get("groups", {})

    print("\n--- Installera mjukvara ---")
    print("  1. Installera enligt grupp")
    print("  2. Installera individuellt program")
    print("  0. Tillbaka")
    choice = input("Välj: ").strip()

    if choice == "1":
        options = [(name, f"{name} - {g.get('description', '')}") for name, g in groups.items()]
        group = _choose("Välj grupp: ", options)
        if group is None:
            return
        keys = groups[group].get("programs", [])
        names = ", ".join(programs[k]["name"] for k in keys if k in programs)
        if input(f"Installera {names}? (j/n): ").strip().lower() != "j":
            print("Avbrutet.")
            return
        _install_and_log(keys, programs, run_by, "Grupp", group_name=group)

    elif choice == "2":
        options = [(key, f"{p['name']} ({p['winget_id']})") for key, p in programs.items()]
        key = _choose("Välj program: ", options)
        if key is None:
            return
        _install_and_log([key], programs, run_by, "Individuellt")
