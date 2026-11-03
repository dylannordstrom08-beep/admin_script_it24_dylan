# admin_script_it24_namn

Ett admin-skript för Windows 11 med en meny där man kan logga datorinformation, skapa lokala användare och installera mjukvara. Alla åtgärder loggas med datum, tid och vem som utförde dem.

**Författare:** Dylan Nordström (IT24)
**Datum:** 2026-11-03

## Vad gör skriptet?

Skriptet körs från PowerShell och startar en meny. Först anger man sitt namn (det skrivs in i alla loggar), därefter väljer man:

1. **Logga grundläggande information** – datum/tid, vem som kör, datornamn, Windows-användare, OS, arkitektur, CPU, RAM (totalt/ledigt), disk (totalt/ledigt), IP- och MAC-adress.
2. **Skapa ny Windows-användare** – frågar efter användarnamn och lösenord och skapar ett lokalt konto.
3. **Installera mjukvara** – antingen enligt grupp (`grupp_1`, `grupp_2`, `grupp_3`) eller ett enskilt program, via `winget`.

## Installation / förberedelser

Dependencies:

| Vad | Varför |
|---|---|
| **Python 3.8 eller senare** | Skriptet är skrivet i Python. Kontrollera med `python --version`. |
| **Git** | För att klona repot. |
| **winget** (App Installer) | Ingår i Windows 11. Används för att ladda ner och installera program. |
| Internetanslutning | Krävs vid mjukvaruinstallation. |

Inga externa Python-bibliotek behövs, endast standardbiblioteket används (`pip install` behövs inte).

### Klona repot

```powershell
git clone https://github.com/dylannordstrom08-beep/admin_script_it24_dylan
cd admin_script_it24_namn
```

## Hur man kör programmet

Starta **PowerShell som administratör** (högerklicka på PowerShell → *Kör som administratör*) och kör:

```powershell
python main.py
```

Exempel:

```
Ange ditt namn (vem som kör skriptet): Dylan
 1. Logga grundläggande information
 2. Skapa ny Windows-användare
 3. Installera mjukvara
 0. Avsluta
Välj ett alternativ: 1
```

### Testläge (utan att ändra datorn)

Vill du prova menyn utan att skapa användare eller installera något, sätt en miljövariabel innan du kör:

```powershell
$env:ADMIN_SCRIPT_DRYRUN = "1"
python main.py
```

Ta bort testläget med `Remove-Item Env:ADMIN_SCRIPT_DRYRUN`.

## Struktur

```
admin_script_it24_namn/
├── main.py                     # Startfil: användarnamn + meny
├── config/
│   └── software.json          # Program och grupper (kan redigeras)
├── functions/
│   ├── logger.py              # Gemensam loggfunktion
│   ├── log_base_info.py       # Loggar grundinformation om datorn
│   ├── create_user.py         # Skapar Windows-användare
│   └── install_software.py    # Installerar mjukvara (grupp/individuellt)
├── logs/                      # Loggfiler (ignoreras av git)
├── .gitignore
└── README.md
```

| Fil | Beskrivning |
|---|---|
| `main.py` | Frågar efter vem som kör skriptet, visar menyn och anropar funktionerna. |
| `functions/logger.py` | Skriver alla loggposter enligt samma format. |
| `functions/log_base_info.py` | Samlar in system-, hårdvaru- och nätverksinformation. |
| `functions/create_user.py` | Frågar efter användarnamn/lösenord, skapar kontot med `New-LocalUser`. |
| `functions/install_software.py` | Läser `software.json`, visar meny och kör `winget install`. |
| `config/software.json` | Lista över program och vilka grupper de tillhör. |

## Loggar

Loggfiler sparas under `logs/` enligt:

```
logs/<ÅÅÅÅ_MM>/<kategori>_<ÅÅÅÅ_MM_DD>.log
exempel: logs/2026_11/mjukvara_2026_11_03.log
```

**Motivering:** en mapp per månad håller antalet filer per mapp lågt, och en fil per kategori och dag gör det enkelt att hitta rätt information. Flera körningar samma dag läggs till i samma fil – inget skrivs över.

| Kategori | Innehåll |
|---|---|
| `session` | När skriptet startades/avslutades och av vem |
| `grundinfo` | Datorinformation (alternativ 1) |
| `skapa_anvandare` | Skapade konton (alternativ 2) |
| `mjukvara` | Installerade program (alternativ 3) |

Varje post har tydliga etiketter, t.ex.:

```
============================================================
Datum: 2026-11-03
Tid: 14:02:11
Utfört av: Anna
Åtgärd: Grundläggande systeminformation loggad
Datornamn: DESKTOP-123ABC
```

Att tänka på:
- Logg-mappen skapas automatiskt. Loggfiler **laddas aldrig upp till GitHub** (`.gitignore` ignorerar `logs/*`).
- Loggfilerna rensas inte automatiskt, ta bort gamla månadsmappar manuellt vid behov.

## Hur man uppdaterar mjukvara och grupper

All mjukvara ligger i `config/software.json` – koden behöver inte ändras.

**Lägga till ett nytt program** i `"programs"`. Hitta winget-id med `winget search <namn>`:

```json
"gimp": {"name": "GIMP", "winget_id": "GIMP.GIMP"}
```

Programmet dyker då upp i listan för individuell installation.

**Lägga till program i en grupp** – lägg till nyckeln i gruppens `"programs"`-lista:

```json
"grupp_1": {"description": "Bas", "programs": ["7zip", "firefox", "vlc", "gimp"]}
```

**Skapa en ny grupp** (t.ex. `elev`, `lärare`, `admin`):

```json
"elev": {"description": "Elevdator", "programs": ["7zip", "firefox"]}
```

Tänk på kommatecken mellan poster; en trasig JSON-fil ger felmeddelande i menyn.

## Behörigheter

- PowerShell måste köras **som administratör** för att skapa användare och installera program.
- Datorn behöver internet för mjukvaruinstallation.
- Skriptet är gjort för **Windows 11** (`create_user` och `install_software` fungerar inte på andra OS).

## Säkerhet och kända brister

- **Lösenordet sparas OKRYPTERAT (i klartext) i loggfilen** för användarskapande. Detta är ett medvetet val för skolprojektet och får inte användas i skarp miljö. Skydda `logs/`-mappen och lägg aldrig upp loggar på GitHub.
- Lösenordet matas in dolt och skickas till PowerShell via miljövariabler (inte som kommandoradsargument), men finns kortvarigt i minnet som text.
- Användare skapas som vanliga användare (gruppen *Users*), inte administratörer.
- Ingen inloggning till skriptet: namnet som anges i början är bara en text och verifieras inte.
- Loggarna är vanliga textfiler som kan ändras av vem som helst med filåtkomst.
- Installerade program styrs av `software.json`; den som kan ändra filen kan ändra vad som installeras.

## Krav för godkännande (checklista)

- [x] Inlämning som länk till GitHub-repo
- [x] Minst 5 commits med beskrivning
- [x] Funktionerna är kommenterade
- [x] Komplett dokumentation (denna fil)
