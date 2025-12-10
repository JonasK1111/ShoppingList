"""
persistence.py
------------------------------------------------------------------------------
Persistenz-Layer (Speichern & Laden).

Konzepte:
- Interface Segregation / Abstraktion: 'FileHandler' definiert den Vertrag.
- Strategy Pattern: 'TxtFileHandler' ist EINE mögliche Strategie.
- Robustness: Fehlerbehandlung (Try/Except) beim Dateizugriff.
------------------------------------------------------------------------------
"""

from abc import ABC, abstractmethod
from typing import List
from models import ShoppingItem, WeightedItem
from factories import ItemFactory


# Das Interface (Abstrakte Basisklasse)
# Die GUI kennt NUR diese Klasse, nicht die konkrete Implementierung darunter.
# Das erfüllt das Dependency Inversion Principle (DIP).
class FileHandler(ABC):
    @abstractmethod
    def save(self, items: List[ShoppingItem], filename: str) -> None:
        pass

    @abstractmethod
    def load(self, filename: str) -> List[ShoppingItem]:
        pass


# Die konkrete Implementierung für Textdateien
class TxtFileHandler(FileHandler):
    """
    Speichert Items in einem Pipe-getrennten Format:
    TYP|NAME|MENGE|PREIS
    Beispiel: W|Bananen|1.5|2.99
    """

    def save(self, items: List[ShoppingItem], filename: str) -> None:
        try:
            # 'w' mode überschreibt die Datei. 'encoding=utf-8' für Sonderzeichen (€).
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("Typ|Name|Menge|Einzelpreis\n")  # Kopfzeile für Lesbarkeit

                for item in items:
                    # Wir müssen prüfen, welcher Typ es ist, um das Kürzel (W/C) zu setzen.
                    if isinstance(item, WeightedItem):
                        # W für Weighted
                        line = f"W|{item.name}|{item.weight}|{item.price_per_unit}"
                    else:
                        # C für Counted. Fallback: Duck Typing prüfen
                        qty = item.quantity if hasattr(item, 'quantity') else 0
                        line = f"C|{item.name}|{qty}|{item.price_per_unit}"

                    f.write(line + "\n")

        except IOError as e:
            # Fehler protokollieren und weiterwerfen, damit die GUI eine Messagebox zeigen kann
            print(f"Fehler beim Speichern: {e}")
            raise

    def load(self, filename: str) -> List[ShoppingItem]:
        items = []
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()[1:]  # [1:] überspringt die Kopfzeile

                for line in lines:
                    if not line.strip(): continue  # Leere Zeilen ignorieren

                    parts = line.strip().split('|')
                    # Validierung: Haben wir alle 4 Teile?
                    if len(parts) != 4: continue

                    type_char, name, amount_str, price_str = parts

                    # Robustness & Usability:
                    # Benutzer nutzen oft Kommas statt Punkte in Textdateien.
                    # Wir ersetzen das hier, damit float() nicht abstürzt.
                    amount_val = float(amount_str.replace(',', '.'))
                    price_val = float(price_str.replace(',', '.'))

                    is_weighted = (type_char == 'W')

                    # WICHTIG: Wir nutzen die Factory auch hier!
                    # So vermeiden wir doppelten Code für die Objekterstellung.
                    item = ItemFactory.create_item(name, is_weighted, amount_val, price_val)
                    items.append(item)

        except (IOError, ValueError) as e:
            print(f"Fehler beim Laden: {e}")
            raise

        return items
