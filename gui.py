"""
gui.py
Die grafische Benutzeroberfläche (GUI) mit tkinter.
"""

import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from typing import List

from models import ShoppingItem, WeightedItem
from factories import ItemFactory
from persistence import FileHandler


class ShoppingListApp:
    def __init__(self, root: tk.Tk, file_handler: FileHandler):
        self.root = root
        self.root.title("Smarte Einkaufsliste")
        self.root.geometry("600x500")

        self.file_handler = file_handler
        self.items: List[ShoppingItem] = []

        self._setup_layout()

    def _setup_layout(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # --- Linke Spalte ---
        control_frame = tk.Frame(self.root, padx=10, pady=10, bg="#f0f0f0")
        control_frame.grid(row=0, column=0, sticky="ns")

        btn_add = tk.Button(control_frame, text="Item hinzufügen", command=self._show_add_popup, width=15)
        btn_add.pack(pady=5)
        btn_remove = tk.Button(control_frame, text="Item entfernen", command=self._remove_selected_item, width=15)
        btn_remove.pack(pady=5)

        tk.Frame(control_frame, height=20, bg="#f0f0f0").pack()  # Spacer

        btn_export = tk.Button(control_frame, text="Exportieren", command=self._export_list, width=15)
        btn_export.pack(pady=5)
        btn_import = tk.Button(control_frame, text="Importieren", command=self._import_list, width=15)
        btn_import.pack(pady=5)

        # --- Rechte Spalte ---
        right_column = tk.Frame(self.root, padx=10, pady=10)
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.rowconfigure(0, weight=1)
        right_column.columnconfigure(0, weight=1)

        # 1. Liste
        list_frame = tk.Frame(right_column)
        list_frame.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, font=("Courier", 10), yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        # 2. Trennlinie
        separator = ttk.Separator(right_column, orient='horizontal')
        separator.grid(row=1, column=0, sticky="ew", pady=(10, 5))

        # 3. Gesamtpreis
        total_frame = tk.Frame(right_column, bg="#e0e0e0", padx=5, pady=5)
        total_frame.grid(row=2, column=0, sticky="ew")

        self.lbl_total_price = tk.Label(total_frame, text="Gesamtpreis: 0.00 €", font=("Arial", 12, "bold"),
                                        bg="#e0e0e0")
        self.lbl_total_price.pack(anchor="e")

    def _refresh_list(self):
        """Aktualisiert die Listbox und den Gesamtpreis."""
        self.listbox.delete(0, tk.END)
        total_sum = 0.0
        for item in self.items:
            price = item.calculate_total()
            total_sum += price
            display_text = f"{item.name.ljust(20)} | {item.get_details().ljust(25)} | {price:>6.2f}€"
            self.listbox.insert(tk.END, display_text)

        self.lbl_total_price.config(text=f"Gesamtpreis: {total_sum:.2f} €")

    def _show_add_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Neues Item")
        popup.geometry("300x250")

        var_name = tk.StringVar()
        var_is_weighted = tk.BooleanVar(value=False)
        var_amount = tk.StringVar()
        var_price = tk.StringVar()

        tk.Label(popup, text="Name:").pack(pady=2)
        tk.Entry(popup, textvariable=var_name).pack()

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

        def submit():
            try:
                name = var_name.get()
                if not name: raise ValueError("Name fehlt.")

                # --- HIER IST DER KOMMA-FIX ---
                # Wir ersetzen Kommas durch Punkte, bevor wir zu float konvertieren
                amount_str = var_amount.get().replace(',', '.')
                price_str = var_price.get().replace(',', '.')

                amount = float(amount_str)
                price = float(price_str)

                new_item = ItemFactory.create_item(name, var_is_weighted.get(), amount, price)

                # Nutze die Merge-Logik auch hier
                self._merge_and_add_items([new_item])

                self._refresh_list()
                popup.destroy()
            except ValueError:
                messagebox.showerror("Fehler", "Bitte gültige Zahlen eingeben (z.B. 2,5 oder 2.5).")

        tk.Button(popup, text="Hinzufügen", command=submit).pack(pady=15)

    def _remove_selected_item(self):
        selection = self.listbox.curselection()
        if not selection: return

        index = selection[0]
        del self.items[index]
        self._refresh_list()

    def _export_list(self):
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if filename:
            try:
                self.file_handler.save(self.items, filename)
                messagebox.showinfo("Erfolg", "Exportiert.")
            except Exception as e:
                messagebox.showerror("Fehler", str(e))

    def _import_list(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filename:
            try:
                loaded_items = self.file_handler.load(filename)
                self._merge_and_add_items(loaded_items)
                self._refresh_list()
                messagebox.showinfo("Erfolg", f"{len(loaded_items)} Items verarbeitet.")
            except Exception as e:
                messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def _merge_and_add_items(self, new_items: List[ShoppingItem]):
        """
        Logik zum Zusammenführen: Erhöht Menge bei gleichen Items,
        benennt um bei Namenskonflikten mit anderem Preis.
        """
        for new_item in new_items:
            merged = False
            for existing_item in self.items:
                # Prüfung auf Identität (Name, Preis, Typ)
                if (existing_item.name == new_item.name and
                        abs(existing_item.price_per_unit - new_item.price_per_unit) < 0.001 and
                        type(existing_item) == type(new_item)):
                    amount_to_add = new_item.weight if isinstance(new_item, WeightedItem) else new_item.quantity
                    existing_item.add_amount(amount_to_add)
                    merged = True
                    break

            if not merged:
                # Prüfung auf Namenskonflikt (Gleicher Name, anderer Preis)
                self._handle_name_collision(new_item)
                self.items.append(new_item)

    def _handle_name_collision(self, new_item: ShoppingItem):
        existing_names = [i.name for i in self.items]
        if new_item.name in existing_names:
            base_name = new_item.name
            counter = 2
            new_name = f"{base_name} #{counter}"
            while new_name in existing_names:
                counter += 1
                new_name = f"{base_name} #{counter}"
            new_item.name = new_name
