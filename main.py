"""
main.py
Einstiegspunkt der Anwendung.
"""

import tkinter as tk
from gui import ShoppingListApp
from persistence import TxtFileHandler

def main():
    root = tk.Tk()
    file_strategy = TxtFileHandler()
    app = ShoppingListApp(root, file_strategy)
    root.mainloop()

if __name__ == "__main__":
    main()
