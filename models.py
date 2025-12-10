"""
models.py
------------------------------------------------------------------------------
Datenmodelle (Model Layer).

Hier definieren wir, was ein "Einkaufsartikel" überhaupt ist.
Wir nutzen Objektorientierte Programmierung (OOP), um Redundanz zu vermeiden.

Konzepte:
- Abstraktion (Abstract Base Class): ShoppingItem kann nicht selbst erstellt werden.
- Vererbung: CountedItem und WeightedItem erben Eigenschaften von ShoppingItem.
- Polymorphismus: Beide Unterklassen haben die GLEICHEN Methoden (calculate_total),
  verhalten sich aber unterschiedlich. Das erlaubt der GUI, sie gleich zu behandeln.
------------------------------------------------------------------------------
"""

from abc import ABC, abstractmethod

# Wir erben von ABC (Abstract Base Class), um ShoppingItem als abstrakt zu markieren.
class ShoppingItem(ABC):
    """
    Abstrakte Basisklasse. Sie definiert den "Bauplan", den alle Artikel einhalten müssen.
    """
    def __init__(self, name: str, price_per_unit: float):
        # Diese Attribute haben alle Artikel gemeinsam.
        # Wir setzen sie hier zentral (DRY - Don't Repeat Yourself).
        self.name = name
        self.price_per_unit = price_per_unit

    # @abstractmethod zwingt die Unterklassen, diese Methode zu implementieren.
    # Das garantiert das Liskov Substitution Principle (LSP):
    # Jede Unterklasse KANN anstelle der Basisklasse verwendet werden.
    @abstractmethod
    def calculate_total(self) -> float:
        """Berechnet den Gesamtpreis (Menge * Einzelpreis)."""
        pass

    @abstractmethod
    def get_details(self) -> str:
        """Gibt einen formatierten String mit Menge und Einheit zurück."""
        pass

    @abstractmethod
    def add_amount(self, amount: float) -> None:
        """
        Erhöht die Menge des Items.
        Wichtig für die Merge-Logik (wenn ein Item schon existiert).
        """
        pass


class CountedItem(ShoppingItem):
    """
    Konkrete Klasse für Artikel mit Stückzahl (z.B. 3 Gurken).
    """
    def __init__(self, name: str, price_per_unit: float, quantity: int):
        # super().__init__ ruft den Konstruktor der Basisklasse auf,
        # damit 'name' und 'price_per_unit' dort gesetzt werden.
        super().__init__(name, price_per_unit)
        self.quantity = quantity

    def calculate_total(self) -> float:
        # Hier implementieren wir die Logik spezifisch für Stückzahlen.
        return self.quantity * self.price_per_unit

    def get_details(self) -> str:
        return f"{self.quantity} Stk. x {self.price_per_unit:.2f}€"

    def add_amount(self, amount: float) -> None:
        # Die GUI liefert 'amount' oft als float. Da Stückzahl int ist, casten wir hier.
        self.quantity += int(amount)


class WeightedItem(ShoppingItem):
    """
    Konkrete Klasse für Artikel nach Gewicht (z.B. 2.5 kg Äpfel).
    """
    def __init__(self, name: str, price_per_unit: float, weight: float):
        super().__init__(name, price_per_unit)
        self.weight = weight

    def calculate_total(self) -> float:
        # Hier ist die Logik anders als bei CountedItem (Gewicht statt Stück).
        return self.weight * self.price_per_unit

    def get_details(self) -> str:
        # Formatierung auf 3 Nachkommastellen für kg
        return f"{self.weight:.3f} kg x {self.price_per_unit:.2f}€/kg"

    def add_amount(self, amount: float) -> None:
        self.weight += amount
