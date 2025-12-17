"""gui.py
------------------------------------------------------------------------------
Grafische Benutzeroberfläche (View & Controller).

Features:
- Multi-Tab Support
- Validierung von Eingaben (Menge > 0)
- Komma-Support (2,5 -> 2.5)
- Intelligentes Importieren (Merge bei Duplikaten)
- Userfreundliche Fehlermeldungen bei ungültigen Zahleneingaben
------------------------------------------------------------------------------
"""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, filedialog, ttk, simpledialog
from typing import List

from .models import ShoppingItem, WeightedItem
from .factories import ItemFactory
from .persistence import FileHandler


class ShoppingListTab(tk.Frame):
    """Ein Tab repräsentiert eine einzelne Einkaufsliste."""

    def __init__(self, parent, file_handler: FileHandler):
        super().__init__(parent)
        self.file_handler = file_handler
        self.items: List[ShoppingItem] = []
        self._setup_layout()

    def _setup_layout(self) -> None:
        """Erstellt das Grid-Layout: Links Buttons, Rechts Liste."""
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        control_frame = tk.Frame(self, padx=10, pady=10, bg="#f0f0f0")
        control_frame.grid(row=0, column=0, sticky="ns")

        tk.Button(control_frame, text="Item hinzufügen", command=self._show_add_popup, width=15).pack(pady=5)
        tk.Button(control_frame, text="Item entfernen", command=self._remove_selected_item, width=15).pack(pady=5)

        tk.Frame(control_frame, height=20, bg="#f0f0f0").pack()

        tk.Button(control_frame, text="Exportieren", command=self._export_list, width=15).pack(pady=5)
        tk.Button(control_frame, text="Importieren", command=self._import_list, width=15).pack(pady=5)

        right_column = tk.Frame(self, padx=10, pady=10)
        right_column.grid(row=0, column=1, sticky="nsew")
        right_column.rowconfigure(0, weight=1)
        right_column.columnconfigure(0, weight=1)

        list_frame = tk.Frame(right_column)
        list_frame.grid(row=0, column=0, sticky="nsew")

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(list_frame, font=("Courier", 10), yscrollcommand=scrollbar.set)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        ttk.Separator(right_column, orient="horizontal").grid(row=1, column=0, sticky="ew", pady=(10, 5))

        total_frame = tk.Frame(right_column, bg="#e0e0e0", padx=5, pady=5)
        total_frame.grid(row=2, column=0, sticky="ew")

        self.lbl_total_price = tk.Label(
            total_frame, text="Gesamtpreis: 0.00 €", font=("Arial", 12, "bold"), bg="#e0e0e0"
        )
        self.lbl_total_price.pack(anchor="e")

    def _refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        total_sum = 0.0

        for item in self.items:
            price = item.calculate_total()
            total_sum += price
            display_text = f"{item.name.ljust(20)} | {item.get_details().ljust(25)} | {price:>6.2f}€"
            self.listbox.insert(tk.END, display_text)

        self.lbl_total_price.config(text=f"Gesamtpreis: {total_sum:.2f} €")

    def _show_add_popup(self) -> None:
        popup = tk.Toplevel(self)
        popup.title("Neues Item")
        popup.geometry("300x250")

        var_name = tk.StringVar()
        var_is_weighted = tk.BooleanVar(value=False)
        var_amount = tk.StringVar()
        var_price = tk.StringVar()

        tk.Label(popup, text="Name:").pack(pady=2)
        tk.Entry(popup, textvariable=var_name).pack()

        def update_label() -> None:
            if var_is_weighted.get():
                lbl_amount.config(text="Gewicht (kg):")
                lbl_price.config(text="Preis pro kg (€):")
            else:
                lbl_amount.config(text="Anzahl (Stück):")
                lbl_price.config(text="Preis pro Stück (€):")

        tk.Checkbutton(popup, text="Ist Gewichtsartikel?", variable=var_is_weighted, command=update_label).pack(pady=5)

        lbl_amount = tk.Label(popup, text="Anzahl (Stück):")
        lbl_amount.pack(pady=2)
        tk.Entry(popup, textvariable=var_amount).pack()

        lbl_price = tk.Label(popup, text="Preis pro Stück (€):")
        lbl_price.pack(pady=2)
        tk.Entry(popup, textvariable=var_price).pack()

        # Userfreundliche Fehlermeldungen für Zahleneingaben
        def submit() -> None:
            name = var_name.get().strip()
            if not name:
                messagebox.showerror("Eingabefehler", "Bitte gib einen Namen für den Artikel ein.")
                return

            amount_raw = var_amount.get().strip()
            price_raw = var_price.get().strip()

            if not amount_raw:
                messagebox.showerror("Eingabefehler", "Bitte gib eine Menge ein (z.B. 2 oder 2,5).")
                return
            if not price_raw:
                messagebox.showerror("Eingabefehler", "Bitte gib einen Preis ein (z.B. 1,99).")
                return

            # Menge parsen
            try:
                amount = float(amount_raw.replace(",", "."))
            except ValueError:
                field_name = "Gewicht (kg)" if var_is_weighted.get() else "Anzahl"
                example = "2,5" if var_is_weighted.get() else "2"
                messagebox.showerror(
                    "Eingabefehler",
                    f"Bitte gib bei „{field_name}“ nur eine Zahl ein (z.B. {example}).\n"
                    "Buchstaben oder andere Zeichen sind hier nicht erlaubt."
                )
                return

            # Preis parsen
            try:
                price = float(price_raw.replace(",", "."))
            except ValueError:
                messagebox.showerror(
                    "Eingabefehler",
                    "Bitte gib beim „Preis“ nur eine Zahl ein (z.B. 1,99).\n"
                    "Buchstaben oder andere Zeichen sind hier nicht erlaubt."
                )
                return

            # Werte prüfen
            if amount <= 0:
                field_name = "Gewicht (kg)" if var_is_weighted.get() else "Anzahl"
                messagebox.showerror("Eingabefehler", f"„{field_name}“ muss größer als 0 sein.")
                return

            # Preis darf auch negativ sein (Rabatt). 0 ist ebenfalls erlaubt.
            # Keine zusätzliche Prüfung nötig.
            

            # Item erstellen und hinzufügen
            new_item = ItemFactory.create_item(name, var_is_weighted.get(), amount, price)
            self._merge_and_add_items([new_item])

            self._refresh_list()
            popup.destroy()

        tk.Button(popup, text="Hinzufügen", command=submit).pack(pady=15)

    def _remove_selected_item(self) -> None:
        selection = self.listbox.curselection()
        if not selection:
            return
        index = selection[0]
        del self.items[index]
        self._refresh_list()

    def _export_list(self) -> None:
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if not filename:
            return
        try:
            self.file_handler.save(self.items, filename)
            messagebox.showinfo("Erfolg", "Exportiert.")
        except Exception as e:
            messagebox.showerror("Fehler", str(e))

    def _import_list(self) -> None:
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filename:
            return
        try:
            loaded_items = self.file_handler.load(filename)
            self._merge_and_add_items(loaded_items)
            self._refresh_list()
            messagebox.showinfo("Erfolg", f"{len(loaded_items)} Items verarbeitet.")
        except Exception as e:
            messagebox.showerror("Fehler", f"Import fehlgeschlagen: {e}")

    def _merge_and_add_items(self, new_items: List[ShoppingItem]) -> None:
        for new_item in new_items:
            merged = False

            for existing_item in self.items:
                is_same_name = existing_item.name == new_item.name
                is_same_price = abs(existing_item.price_per_unit - new_item.price_per_unit) < 0.001
                is_same_type = type(existing_item) == type(new_item)

                if is_same_name and is_same_price and is_same_type:
                    if isinstance(new_item, WeightedItem):
                        amount_to_add = new_item.weight
                    else:
                        amount_to_add = new_item.quantity  # type: ignore[attr-defined]
                    existing_item.add_amount(amount_to_add)
                    merged = True
                    break

            if not merged:
                self._handle_name_collision(new_item)
                self.items.append(new_item)

    def _handle_name_collision(self, new_item: ShoppingItem) -> None:
        existing_names = [i.name for i in self.items]
        if new_item.name not in existing_names:
            return

        base_name = new_item.name
        counter = 2
        new_name = f"{base_name} #{counter}"

        while new_name in existing_names:
            counter += 1
            new_name = f"{base_name} #{counter}"

        new_item.name = new_name


class ShoppingListApp:
    """Haupt-Controller: Fenster + Notebook."""

    def __init__(self, root: tk.Tk, file_handler: FileHandler):
        self.root = root
        self.root.title("Smarte Einkaufsliste (Multi-Tab)")
        self.root.geometry("700x600")
        self.file_handler = file_handler

        top_bar = tk.Frame(self.root, bg="#e8e8e8", padx=5, pady=5, relief=tk.RAISED, bd=1)
        top_bar.pack(side=tk.TOP, fill=tk.X)

        btn_style = {"bg": "white", "padx": 5, "pady": 2}

        tk.Button(top_bar, text="+ Neue Liste", command=self.ask_new_tab, **btn_style).pack(side=tk.LEFT, padx=5)
        tk.Button(top_bar, text="Tab umbenennen", command=self.rename_current_tab, **btn_style).pack(side=tk.LEFT, padx=5)

        tk.Frame(top_bar, width=20, bg="#e8e8e8").pack(side=tk.LEFT)

        tk.Button(top_bar, text="x Tab schließen", command=self.close_current_tab, fg="red", **btn_style).pack(
            side=tk.LEFT, padx=5
        )

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self._create_menu()
        self.add_new_tab("Meine Liste")

    def _create_menu(self) -> None:
        menubar = tk.Menu(self.root)
        list_menu = tk.Menu(menubar, tearoff=0)
        list_menu.add_command(label="Neue Liste erstellen", command=self.ask_new_tab)
        list_menu.add_command(label="Aktuellen Tab umbenennen", command=self.rename_current_tab)
        list_menu.add_separator()
        list_menu.add_command(label="Aktuellen Tab schließen", command=self.close_current_tab)
        menubar.add_cascade(label="Optionen", menu=list_menu)
        self.root.config(menu=menubar)

    def ask_new_tab(self) -> None:
        name = simpledialog.askstring("Neue Liste", "Name der Liste:")
        if name:
            self.add_new_tab(name)

    def add_new_tab(self, name: str) -> None:
        new_tab = ShoppingListTab(self.notebook, self.file_handler)
        self.notebook.add(new_tab, text=name)
        self.notebook.select(new_tab)

    def close_current_tab(self) -> None:
        if self.notebook.index("end") <= 1:
            if not messagebox.askyesno(
                "Warnung",
                "Das ist die letzte Liste. Wirklich schließen?\n(Das Programm bleibt dann leer)."
            ):
                return

        selected_tab_id = self.notebook.select()
        if selected_tab_id:
            self.notebook.forget(selected_tab_id)

    def rename_current_tab(self) -> None:
        selected_tab_id = self.notebook.select()
        if not selected_tab_id:
            return

        current_name = self.notebook.tab(selected_tab_id, "text")
        new_name = simpledialog.askstring("Umbenennen", "Neuer Name:", initialvalue=current_name)
        if new_name:
            self.notebook.tab(selected_tab_id, text=new_name)
