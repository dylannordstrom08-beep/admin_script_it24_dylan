"""
main.py - Startpunkt för admin-skriptet. Kör med: python main.py

Frågar efter vem som kör skriptet (loggas i alla loggar) och visar en meny
där alla funktioner i mappen "functions" kan väljas.
"""

from functions.create_user import create_user
from functions.install_software import install_software
from functions.log_base_info import log_base_info
from functions.logger import write_log


def ask_for_user():
    """Frågar efter namn tills något har skrivits in."""
    while True:
        name = input("Ange ditt namn (vem som kör skriptet): ").strip()
        if name:
            return name
        print("Namn får inte vara tomt.")


def show_menu(user):
    """Skriver ut huvudmenyn."""
    print("\n" + "=" * 40)
    print(f" ADMIN-SKRIPT   (användare: {user})")
    print("=" * 40)
    print(" 1. Logga grundläggande information")
    print(" 2. Skapa ny Windows-användare")
    print(" 3. Installera mjukvara")
    print(" 0. Avsluta")


def main():
    user = ask_for_user()
    write_log("session", user, "Skriptet startades")

    # Kopplar menyval till funktion, lätt att bygga ut med fler val
    actions = {"1": log_base_info, "2": create_user, "3": install_software}

    while True:
        show_menu(user)
        choice = input("Välj ett alternativ: ").strip()
        if choice == "0":
            write_log("session", user, "Skriptet avslutades")
            print("Hej då!")
            break
        elif choice in actions:
            actions[choice](user)
        else:
            print("Ogiltigt val, försök igen.")


if __name__ == "__main__":
    main()
