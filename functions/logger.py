"""
logger.py - Gemensam loggfunktion för hela projektet.

LOGGLOGIK
---------
Alla loggar sparas under logs/ i en mapp per månad:

    logs/<ÅÅÅÅ_MM>/<kategori>_<ÅÅÅÅ_MM_DD>.log
    t.ex. logs/2026_11/skapa_anvandare_2026_11_03.log

Motivering: en mapp per månad håller antalet filer i varje mapp lågt, och en
fil per kategori och dag gör att man snabbt hittar rätt information. Flera
körningar samma dag läggs till i samma fil (append), aldrig skrivs över.

Varje loggpost är ett block med tydliga etiketter ("Datornamn: ..."), så att
den går att läsa utan förkunskaper.
"""

import os
from datetime import datetime

# Projektets rotmapp (mappen ovanför "functions") och logs-mappen
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")


def write_log(category, user, action, details=None, warning=None):
    """Skriver en loggpost och returnerar sökvägen till loggfilen.

    category: filnamnsprefix, t.ex. "grundinfo" eller "skapa_anvandare"
    user:     vem som kör skriptet (anges i main)
    action:   kort beskrivning av vad som hänt
    details:  dict med etikett -> värde, skrivs som "Etikett: värde"
    warning:  valfri varningstext som skrivs ut sist i posten
    """
    now = datetime.now()

    # Skapar månadsmappen (t.ex. logs/2026_11) om den inte finns
    month_dir = os.path.join(LOGS_DIR, now.strftime("%Y_%m"))
    os.makedirs(month_dir, exist_ok=True)

    log_file = os.path.join(month_dir, f"{category}_{now.strftime('%Y_%m_%d')}.log")

    lines = [
        "=" * 60,
        f"Datum: {now.strftime('%Y-%m-%d')}",
        f"Tid: {now.strftime('%H:%M:%S')}",
        f"Utfört av: {user}",
        f"Åtgärd: {action}",
    ]
    for label, value in (details or {}).items():
        lines.append(f"{label}: {value}")
    if warning:
        lines.append(f"VARNING: {warning}")
    lines.append("")

    # "a" = append, tidigare poster bevaras. UTF-8 så å/ä/ö fungerar.
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    return log_file
