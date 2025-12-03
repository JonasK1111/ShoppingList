"""
models.py
Dieses Modul enthält die Datenmodelle der Anwendung.
Es demonstriert Vererbung, Abstraktion und Polymorphismus.
"""

from abc import ABC, abstractmethod

# Basisklasse (Abstraktion)
class ShoppingItem(ABC):
    """
    Abstrakte Basisklasse für alle Einkaufsartikel.
    Definiert die Schnittstelle, die alle Unterklassen implementieren müssen.
    """
    def __init__(self, name: str, price_per_unit: float):
        self.name = name
        self.price_per_unit = price_per_unit

    @abstractmethod
    def calculate_total(self) -> float:
        """Berechnet den Gesamtpreis des Items."""
        pass

    @abstractmethod
    def get_details(self) -> str:
        """Gibt Details (Menge/Gewicht) als String zurück."""
        pass

    @abstractmethod
    def add_amount(self, amount: float) -> None:
        """Erhöht die Menge/das Gewicht des Items (für Merge-Logik)."""
        pass

# Konkrete Klasse 1 (Stückzahl)
class CountedItem(ShoppingItem):
    """
    Repräsentiert Artikel, die nach Stückzahl berechnet werden (z.B. Gurken).
    """
    def __init__(self, name: str, price_per_unit: float, quantity: int):
        super().__init__(name, price_per_unit)
        self.quantity = quantity

    def calculate_total(self) -> float:
        return self.quantity * self.price_per_unit

    def get_details(self) -> str:
        return f"{self.quantity} Stk. x {self.price_per_unit:.2f}€"

    def add_amount(self, amount: float) -> None:
        self.quantity += int(amount)

# Konkrete Klasse 2 (Gewicht)
class WeightedItem(ShoppingItem):
    """
    Repräsentiert Artikel, die nach Gewicht berechnet werden (z.B. Bananen).
    """
    def __init__(self, name: str, price_per_unit: float, weight: float):
        super().__init__(name, price_per_unit)
        self.weight = weight

    def calculate_total(self) -> float:
        return self.weight * self.price_per_unit

    def get_details(self) -> str:
        return f"{self.weight:.3f} kg x {self.price_per_unit:.2f}€/kg"

    def add_amount(self, amount: float) -> None:
        self.weight += amount
