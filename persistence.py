"""
persistence.py
Handhabung von Datei-Operationen (Export/Import).
"""

from abc import ABC, abstractmethod
from typing import List
from models import ShoppingItem, WeightedItem
from factories import ItemFactory


class FileHandler(ABC):
    @abstractmethod
    def save(self, items: List[ShoppingItem], filename: str) -> None:
        pass

    @abstractmethod
    def load(self, filename: str) -> List[ShoppingItem]:
        pass


class TxtFileHandler(FileHandler):
    """
    Speichert und lädt Items.
    Format: TYP|NAME|MENGE|PREIS
    """

    def save(self, items: List[ShoppingItem], filename: str) -> None:
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Typ|Name|Menge|Einzelpreis\n")  # Header
                for item in items:
                    if isinstance(item, WeightedItem):
                        line = f"W|{item.name}|{item.weight}|{item.price_per_unit}"
                    else:
                        qty = item.quantity if hasattr(item, 'quantity') else 0
                        line = f"C|{item.name}|{qty}|{item.price_per_unit}"
                    f.write(line + "\n")
        except IOError as e:
            print(f"Fehler beim Speichern: {e}")
            raise

    def load(self, filename: str) -> List[ShoppingItem]:
        items = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()[1:]  # Header überspringen
                for line in lines:
                    if not line.strip(): continue

                    parts = line.strip().split('|')
                    if len(parts) != 4: continue

                    type_char, name, amount_str, price_str = parts

                    # Robustness: Kommas durch Punkte ersetzen, falls manuell editiert wurde
                    amount_val = float(amount_str.replace(',', '.'))
                    price_val = float(price_str.replace(',', '.'))

                    is_weighted = (type_char == 'W')
                    item = ItemFactory.create_item(name, is_weighted, amount_val, price_val)
                    items.append(item)
        except (IOError, ValueError) as e:
            print(f"Fehler beim Laden: {e}")
            raise

        return items
