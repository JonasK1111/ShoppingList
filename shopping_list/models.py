"""models.py
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

from __future__ import annotations

from abc import ABC, abstractmethod


class ShoppingItem(ABC):
    """Abstrakte Basisklasse für Einkaufsartikel."""

    def __init__(self, name: str, price_per_unit: float):
        self.name = name
        self.price_per_unit = price_per_unit

    @abstractmethod
    def calculate_total(self) -> float:
        """Berechnet den Gesamtpreis (Menge * Einzelpreis)."""
        raise NotImplementedError

    @abstractmethod
    def get_details(self) -> str:
        """Gibt einen formatierten String mit Menge und Einheit zurück."""
        raise NotImplementedError

    @abstractmethod
    def add_amount(self, amount: float) -> None:
        """Erhöht die Menge des Items (für Merge/Import)."""
        raise NotImplementedError


class CountedItem(ShoppingItem):
    """Konkrete Klasse für Artikel mit Stückzahl (z.B. 3 Gurken)."""

    def __init__(self, name: str, price_per_unit: float, quantity: int):
        super().__init__(name, price_per_unit)
        self.quantity = quantity

    def calculate_total(self) -> float:
        return self.quantity * self.price_per_unit

    def get_details(self) -> str:
        return f"{self.quantity} Stk. x {self.price_per_unit:.2f}€"

    def add_amount(self, amount: float) -> None:
        self.quantity += int(amount)


class WeightedItem(ShoppingItem):
    """Konkrete Klasse für Artikel nach Gewicht (z.B. 2.5 kg Äpfel)."""

    def __init__(self, name: str, price_per_unit: float, weight: float):
        super().__init__(name, price_per_unit)
        self.weight = weight

    def calculate_total(self) -> float:
        return self.weight * self.price_per_unit

    def get_details(self) -> str:
        return f"{self.weight:.3f} kg x {self.price_per_unit:.2f}€/kg"

    def add_amount(self, amount: float) -> None:
        self.weight += float(amount)
