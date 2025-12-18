"""persistence.py
------------------------------------------------------------------------------
Persistenz-Layer (Speichern & Laden).
------------------------------------------------------------------------------
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from .models import ShoppingItem, WeightedItem
from .factories import ItemFactory


class FileHandler(ABC):
    """Abstraktes Interface für Speichern/Laden (Strategy)."""

    @abstractmethod
    def save(self, items: List[ShoppingItem], filename: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self, filename: str) -> List[ShoppingItem]:
        raise NotImplementedError


class TxtFileHandler(FileHandler):
    """Speichert Items in einem Pipe-getrennten Format: TYP|NAME|MENGE|PREIS.
    Zusätzlich wird eine Footer-Zeile mit dem Gesamtpreis geschrieben:
    # Gesamtpreis|<wert>
    """

    def save(self, items: List[ShoppingItem], filename: str) -> None:
        try:
            total_sum = sum(item.calculate_total() for item in items)

            # Spaltenbreiten (kannst du anpassen)
            type_w = 3
            name_w = 25
            amount_w = 10
            price_w = 12

            with open(filename, "w", encoding="utf-8") as f:
                header = (
                    f"{'Typ':<{type_w}}|"
                    f"{'Name':<{name_w}}|"
                    f"{'Menge':>{amount_w}}|"
                    f"{'Einzelpreis':>{price_w}}"
                )
                f.write(header + "\n")

                for item in items:
                    if isinstance(item, WeightedItem):
                        typ = "W"
                        amount = f"{item.weight:.3f}"
                        price = f"{item.price_per_unit:.2f}"
                    else:
                        typ = "C"
                        qty = item.quantity if hasattr(item, "quantity") else 0
                        amount = f"{qty:d}"
                        price = f"{item.price_per_unit:.2f}"

                    line = (
                        f"{typ:<{type_w}}|"
                        f"{item.name:<{name_w}}|"
                        f"{amount:>{amount_w}}|"
                        f"{price:>{price_w}}"
                    )
                    f.write(line + "\n")

                f.write(f"# Gesamtpreis|{total_sum:.2f}\n")

        except IOError as e:
            print(f"Fehler beim Speichern: {e}")
            raise

    def load(self, filename: str) -> List[ShoppingItem]:
        items: List[ShoppingItem] = []
        try:
            with open(filename, "r", encoding="utf-8") as f:
                for raw in f:
                    line = raw.strip()
                    if not line:
                        continue

                    # Kopfzeile / Footer / Kommentare ignorieren
                    if line.startswith("Typ|"):
                        continue
                    if line.startswith("#"):
                        continue

                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) != 4:
                        continue

                    type_char, name, amount_str, price_str = parts
                    amount_val = float(amount_str.replace(",", "."))
                    price_val = float(price_str.replace(",", "."))
                    is_weighted = type_char.upper() == "W"

                    item = ItemFactory.create_item(name, is_weighted, amount_val, price_val)
                    items.append(item)

        except (IOError, ValueError) as e:
            print(f"Fehler beim Laden: {e}")
            raise

        return items
