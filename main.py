"""
main.py
------------------------------------------------------------------------------
Einstiegspunkt der Anwendung (Entry Point).

Aufgaben dieser Datei:
1. Initialisierung des GUI-Frameworks (tkinter).
2. "Zusammenstecken" der Anwendungskomponenten (Dependency Injection).
3. Starten der Hauptschleife (Mainloop).

Prinzipien:
- Separation of Concerns: Diese Datei enthält keine Logik, nur Konfiguration.
- Dependency Injection: Wir entscheiden hier, welche Speicherstrategie genutzt wird.
------------------------------------------------------------------------------
"""

import tkinter as tk
from gui import ShoppingListApp
from persistence import TxtFileHandler

def main():
    # 1. Erstellen des Hauptfensters (Root Widget)
    # Das ist das Fundament jeder tkinter-Anwendung.
    root = tk.Tk()

    # 2. Auswahl der Speicherstrategie (Design Pattern: Strategy)
    # Wir erstellen eine Instanz von TxtFileHandler.
    # WICHTIG: Wir könnten hier stattdessen auch einen "JsonFileHandler" oder
    # "DatabaseFileHandler" erstellen. Da die App nur das Interface erwartet,
    # würde sie ohne Code-Änderung weiter funktionieren (Open/Closed Principle).
    file_strategy = TxtFileHandler()

    # 3. Initialisierung der App-Steuerung (Controller)
    # Wir übergeben das Fenster und die gewählte Strategie an die App.
    # Das nennt man "Dependency Injection": Die App erstellt den Handler nicht selbst,
    # sondern bekommt ihn "injiziert".
    app = ShoppingListApp(root, file_strategy)

    # 4. Starten der Event-Schleife
    # Ab hier wartet das Programm auf Maus-Klicks und Tastatureingaben.
    # Ohne diesen Befehl würde sich das Fenster sofort wieder schließen.
    root.mainloop()

# Dieser Block stellt sicher, dass main() nur ausgeführt wird, wenn man
# die Datei direkt startet (nicht wenn man sie importiert).
if __name__ == "__main__":
    main()
