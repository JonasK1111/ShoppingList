"""
gui.py
------------------------------------------------------------------------------
Grafische Benutzeroberfläche (View & Controller).

Struktur & Konzepte:
1. ShoppingListTab (Component):
   - Repräsentiert EINE einzelne Einkaufsliste.
   - Erbt von tk.Frame -> Ist ein wiederverwendbares Widget.
   - Enthält die Logik für Button-Klicks, Liste aktualisieren, Popups.
   - Kapselung: Alle Daten (self.items) sind in der Instanz gekapselt.

2. ShoppingListApp (Main Controller):
   - Verwaltet das Hauptfenster und die Tabs (Notebook).
   - Enthält die globale Toolbar oben.
   - Steuert das Erstellen/Schließen von Tabs.

Features:
- Multi-Tab Support
- Validierung von Eingaben (Menge > 0)
- Komma-Support (2,5 -> 2.5)
- Intelligentes Importieren (Merge bei Duplikaten)
------------------------------------------------------------------------------
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
from typing import List

from models import ShoppingItem, WeightedItem, CountedItem
from factories import ItemFactory
from persistence import FileHandler


class ShoppingListTab(tk.Frame):
    """
    Diese Klasse ist das Herzstück einer einzelnen Liste.
    Jeder Tab im Programm ist eine eigene Instanz dieser Klasse.
    Dadurch kommen sich die Daten verschiedener Listen nicht in die Quere.
    """

    def __init__(self, parent, file_handler: FileHandler):
        # Initialisierung des tk.Frames
        super().__init__(parent)

        self.file_handler = file_handler
        # Diese Liste speichert die Items NUR für diesen Tab.
        self.items: List[ShoppingItem] = []

        # Aufbau der GUI-Elemente für diesen Tab
        self._setup_layout()

    def _setup_layout(self):
        """Erstellt das Grid-Layout: Links Buttons, Rechts Liste."""
        # Konfiguration: Spalte 1 (Liste) soll sich bei Fenstergröße ändern (weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        # --- Linke Spalte: Steuerungs-Buttons ---
        control_frame = tk.Frame(self, padx=10, pady=10, bg="#f0f0f0")
        control_frame.grid(row=0, column=0, sticky="ns")  # ns = North South (volle Höhe)

        # Die Buttons rufen Methoden dieser Klasse auf (self._show_add_popup etc.)
        btn_add = tk.Button(control_frame, text="Item hinzufügen", command=self._show_add_popup, width=15)
        btn_add.pack(pady=5)
        btn_remove = tk.Button(control_frame, text="Item entfernen", command=self._remove_selected_item, width=15)
        btn_remove.pack(pady=5)

        tk.Frame(control_frame, height=20, bg="#f0f0f0").pack()  # Leerraum (Spacer)

        btn_export = tk.Button(control_frame, text="Exportieren", command=self._export_list, width=15)
        btn_export.pack(pady=5)
        btn_import = tk.Button(control_frame, text="Importieren", command=self._import_list, width=15)
        btn_import.pack(pady=5)

        # --- Rechte Spalte: Listenanzeige & Gesamtpreis ---
        right_column = tk.Frame(self, padx=10, pady=10)
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.rowconfigure(0, weight=1)  # Listbox darf wachsen
        right_column.columnconfigure(0, weight=1)

        # 1. Der Listen-Bereich (Listbox mit Scrollbar)
        list_frame = tk.Frame(right_column)
        list_frame.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Monospace Font (Courier) sorgt dafür, dass die Spalten sauber untereinander stehen
        self.listbox = tk.Listbox(list_frame, font=("Courier", 10), yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # 2. Visuelle Trennlinie (Separator)
        separator = ttk.Separator(right_column, orient='horizontal')
        separator.grid(row=1, column=0, sticky="ew", pady=(10, 5))

        # 3. Bereich für den Gesamtpreis (immer sichtbar unten)
        total_frame = tk.Frame(right_column, bg="#e0e0e0", padx=5, pady=5)
        total_frame.grid(row=2, column=0, sticky="ew")  # sticky ew = East West (volle Breite)

        self.lbl_total_price = tk.Label(total_frame, text="Gesamtpreis: 0.00 €", font=("Arial", 12, "bold"),
                                        bg="#e0e0e0")
        self.lbl_total_price.pack(anchor="e")  # Rechtsbündig

    def _refresh_list(self):
        """
        Leert die Listbox und baut sie basierend auf self.items neu auf.
        Berechnet dabei auch den Gesamtpreis live neu.
        """
        self.listbox.delete(0, tk.END)  # Alte Einträge löschen
        total_sum = 0.0

        for item in self.items:
            # Polymorpher Aufruf: calculate_total() macht je nach Item-Typ das Richtige
            price = item.calculate_total()
            total_sum += price

            # String-Formatierung für saubere Spaltenoptik
            display_text = f"{item.name.ljust(20)} | {item.get_details().ljust(25)} | {price:>6.2f}€"
            self.listbox.insert(tk.END, display_text)

        # Label aktualisieren
        self.lbl_total_price.config(text=f"Gesamtpreis: {total_sum:.2f} €")

    def _show_add_popup(self):
        """Erzeugt ein modales Fenster (Toplevel) zur Dateneingabe."""
        popup = tk.Toplevel(self)
        popup.title("Neues Item")
        popup.geometry("300x250")

        # Tkinter-Variablen speichern die Eingaben des Nutzers
        var_name = tk.StringVar()
        var_is_weighted = tk.BooleanVar(value=False)
        var_amount = tk.StringVar()  # String statt Double, um leere Eingabe abzufangen
        var_price = tk.StringVar()

        tk.Label(popup, text="Name:").pack(pady=2)
        tk.Entry(popup, textvariable=var_name).pack()

        # Logik: Labels ändern sich, wenn Checkbox geklickt wird
        def update_label():
            if var_is_weighted.get():
                lbl_amount.config(text="Gewicht (kg):")
                lbl_price.config(text="Preis pro kg (€):")
            else:
                lbl_amount.config(text="Anzahl (Stück):")
                lbl_price.config(text="Preis pro Stück (€):")

        chk = tk.Checkbutton(popup, text="Ist Gewichtsartikel?", variable=var_is_weighted, command=update_label)
        chk.pack(pady=5)

        lbl_amount = tk.Label(popup, text="Anzahl (Stück):")
        lbl_amount.pack(pady=2)
        tk.Entry(popup, textvariable=var_amount).pack()

        lbl_price = tk.Label(popup, text="Preis pro Stück (€):")
        lbl_price.pack(pady=2)
        tk.Entry(popup, textvariable=var_price).pack()

        # Innere Funktion für den "Hinzufügen"-Button
        def submit():
            try:
                # 1. Validierung: Name vorhanden?
                name = var_name.get()
                if not name: raise ValueError("Name fehlt.")

                # 2. Konvertierung & Komma-Fix
                # Nutzer tippt oft "2,5". Python braucht "2.5".
                amount_str = var_amount.get().replace(',', '.')
                price_str = var_price.get().replace(',', '.')

                amount = float(amount_str)
                price = float(price_str)

                # 3. Logische Validierung (Negative Zahlen machen keinen Sinn)
                if amount <= 0:
                    raise ValueError("Menge muss größer als 0 sein.")
                if price <= 0:
                    raise ValueError("Preis muss größer als 0 sein.")

                # 4. Objekt erstellen via Factory
                new_item = ItemFactory.create_item(name, var_is_weighted.get(), amount, price)

                # 5. Zur Liste hinzufügen (mit intelligenter Merge-Logik)
                self._merge_and_add_items([new_item])

                self._refresh_list()
                popup.destroy()  # Fenster schließen

            except ValueError as e:
                # Fehler anzeigen (z.B. "Preis muss > 0 sein" oder "Konnte string nicht zu float wandeln")
                messagebox.showerror("Eingabefehler", str(e))

        tk.Button(popup, text="Hinzufügen", command=submit).pack(pady=15)

    def _remove_selected_item(self):
        """Löscht das aktuell markierte Item."""
        selection = self.listbox.curselection()
        if not selection: return
        index = selection[0]
        del self.items[index]
        self._refresh_list()

    def _export_list(self):
        """Exportiert die Liste via FileHandler."""
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filename:
            try:
                self.file_handler.save(self.items, filename)
                messagebox.showinfo("Erfolg", "Exportiert.")
            except Exception as e:
                messagebox.showerror("Fehler", str(e))

    def _import_list(self):
        """Importiert Liste und merged sie."""
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            try:
                loaded_items = self.file_handler.load(filename)

                # Hier nutzen wir die intelligente Merge-Funktion
                self._merge_and_add_items(loaded_items)

                self._refresh_list()
                messagebox.showinfo("Erfolg", f"{len(loaded_items)} Items verarbeitet.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def _merge_and_add_items(self, new_items: List[ShoppingItem]):
        """
        Kernlogik für den Import:
        1. Identisches Item gefunden? -> Menge erhöhen.
        2. Gleicher Name aber anderer Preis? -> Umbenennen (#2).
        3. Sonst -> Einfach hinzufügen.
        """
        for new_item in new_items:
            merged = False

            for existing_item in self.items:
                # Wir prüfen auf 'Gleichheit': Name gleich UND Preis gleich UND Typ gleich
                # abs(...) < 0.001 ist nötig, da Float-Vergleiche ungenau sein können.
                is_same_name = (existing_item.name == new_item.name)
                is_same_price = abs(existing_item.price_per_unit - new_item.price_per_unit) < 0.001
                is_same_type = (type(existing_item) == type(new_item))

                if is_same_name and is_same_price and is_same_type:
                    # Fall 1: Exaktes Duplikat gefunden -> Menge aufaddieren
                    # Wir müssen wissen, ob wir weight oder quantity holen müssen
                    if isinstance(new_item, WeightedItem):
                        amount_to_add = new_item.weight
                    else:
                        amount_to_add = new_item.quantity

                    # add_amount ist in models.py definiert
                    existing_item.add_amount(amount_to_add)
                    merged = True
                    break

            if not merged:
                # Fall 2 oder 3: Neu hinzufügen, aber vorher Namen checken
                self._handle_name_collision(new_item)
                self.items.append(new_item)

    def _handle_name_collision(self, new_item: ShoppingItem):
        """
        Löst Namenskonflikte auf (z.B. Brot für 2€ vs Brot für 3€).
        Benennt das neue Item in 'Brot #2' um.
        """
        existing_names = [i.name for i in self.items]

        if new_item.name in existing_names:
            base_name = new_item.name
            counter = 2
            new_name = f"{base_name} #{counter}"

            # Solange hochzählen, bis ein freier Name gefunden wurde
            while new_name in existing_names:
                counter += 1
                new_name = f"{base_name} #{counter}"

            new_item.name = new_name


class ShoppingListApp:
    """
    Der Haupt-Controller der Anwendung.
    Er verwaltet das Hauptfenster und den Tab-Container (Notebook).
    Er weiß nichts von der Logik innerhalb der Tabs (Items löschen, addieren etc.).
    """

    def __init__(self, root: tk.Tk, file_handler: FileHandler):
        self.root = root
        self.root.title("Smarte Einkaufsliste (Multi-Tab)")
        self.root.geometry("700x600")
        self.file_handler = file_handler

        # --- Globale Toolbar ganz oben (immer sichtbar) ---
        top_bar = tk.Frame(self.root, bg="#e8e8e8", padx=5, pady=5, relief=tk.RAISED, bd=1)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        # Style-Definition für die Toolbar-Buttons
        btn_style = {"bg": "white", "padx": 5, "pady": 2}

        # Buttons erstellen
        btn_new = tk.Button(top_bar, text="+ Neue Liste", command=self.ask_new_tab, **btn_style)
        btn_new.pack(side=tk.LEFT, padx=5)

        btn_rename = tk.Button(top_bar, text="Tab umbenennen", command=self.rename_current_tab, **btn_style)
        btn_rename.pack(side=tk.LEFT, padx=5)

        # Kleiner Abstandshalter vor dem Schließen-Button
        tk.Frame(top_bar, width=20, bg="#e8e8e8").pack(side=tk.LEFT)

        btn_close = tk.Button(top_bar, text="x Tab schließen", command=self.close_current_tab, fg="red", **btn_style)
        btn_close.pack(side=tk.LEFT, padx=5)

        # --- Container für die Tabs (Notebook) ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Fallback-Menü (oben in der Systemleiste)
        self._create_menu()

        # Wir starten direkt mit einem leeren Tab
        self.add_new_tab("Meine Liste")

    def _create_menu(self):
        """Erstellt das klassische Menü oben (Datei, Bearbeiten...)."""
        menubar = tk.Menu(self.root)
        list_menu = tk.Menu(menubar, tearoff=0)
        list_menu.add_command(label="Neue Liste erstellen", command=self.ask_new_tab)
        list_menu.add_command(label="Aktuellen Tab umbenennen", command=self.rename_current_tab)
        list_menu.add_separator()
        list_menu.add_command(label="Aktuellen Tab schließen", command=self.close_current_tab)
        menubar.add_cascade(label="Optionen", menu=list_menu)
        self.root.config(menu=menubar)

    def ask_new_tab(self):
        """Fragt den Nutzer nach einem Namen und erstellt neuen Tab."""
        name = simpledialog.askstring("Neue Liste", "Name der Liste:")
        if name:
            self.add_new_tab(name)

    def add_new_tab(self, name):
        """
        Erstellt eine Instanz von ShoppingListTab und fügt sie dem Notebook hinzu.
        Hier wird der FileHandler an den Tab weitergereicht.
        """
        new_tab = ShoppingListTab(self.notebook, self.file_handler)
        self.notebook.add(new_tab, text=name)
        # Den neuen Tab sofort fokussieren
        self.notebook.select(new_tab)

    def close_current_tab(self):
        """Schließt den aktuell ausgewählten Tab."""
        # Sicherheitsabfrage beim letzten Tab
        if self.notebook.index("end") <= 1:
            if not messagebox.askyesno("Warnung",
                                       "Das ist die letzte Liste. Wirklich schließen?\n(Das Programm bleibt dann leer)."):
                return

        selected_tab_id = self.notebook.select()
        if selected_tab_id:
            self.notebook.forget(selected_tab_id)  # Entfernt den Tab aus dem Notebook

    def rename_current_tab(self):
        """Benennt den aktiven Tab um."""
        selected_tab_id = self.notebook.select()
        if not selected_tab_id: return

        # Aktuellen Namen holen als Vorschlagswert
        current_name = self.notebook.tab(selected_tab_id, "text")
        new_name = simpledialog.askstring("Umbenennen", "Neuer Name:", initialvalue=current_name)

        if new_name:
            self.notebook.tab(selected_tab_id, text=new_name)
