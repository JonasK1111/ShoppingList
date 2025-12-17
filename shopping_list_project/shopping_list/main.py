"""main.py
------------------------------------------------------------------------------
Einstiegspunkt der Anwendung (Entry Point).

Aufgaben dieser Datei:
1. Initialisierung des GUI-Frameworks (tkinter).
2. "Zusammenstecken" der Anwendungskomponenten (Dependency Injection).
3. Starten der Hauptschleife (Mainloop).
------------------------------------------------------------------------------
"""

from __future__ import annotations

import tkinter as tk

from .gui import ShoppingListApp
from .persistence import TxtFileHandler


def main() -> None:
    root = tk.Tk()
    file_strategy = TxtFileHandler()
    ShoppingListApp(root, file_strategy)
    root.mainloop()


if __name__ == "__main__":
    main()
