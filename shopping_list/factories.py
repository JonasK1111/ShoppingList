"""factories.py
------------------------------------------------------------------------------
Fabrik-Muster (Factory Pattern).

Problem:
Die GUI sammelt Rohdaten (Strings aus Textfeldern, Booleans aus Checkboxen).
Sie weiß aber nicht im Detail, wie man daraus komplexe Objekte baut,
und sie soll auch nicht wissen, welche konkreten Klassen (Weighted vs Counted) es gibt.

Lösung:
Die Factory übernimmt diese Entscheidung. Das entkoppelt die GUI von den Modellen.
------------------------------------------------------------------------------
"""

from __future__ import annotations

from .models import ShoppingItem, CountedItem, WeightedItem


class ItemFactory:
    """Erzeugungslogik für ShoppingItem-Objekte."""

    @staticmethod
    def create_item(name: str, is_weighted: bool, amount: float, price: float) -> ShoppingItem:
        """Erzeugt ein Item abhängig von der Art (Gewicht vs. Stück).

        Args:
            name: Name des Artikels
            is_weighted: True = Gewichtsartikel, False = Stückartikel
            amount: Menge (Stück) oder Gewicht (kg)
            price: Preis pro Einheit

        Returns:
            Ein Objekt vom Typ ShoppingItem (bzw. einer Unterklasse).
        """
        if is_weighted:
            return WeightedItem(name=name, price_per_unit=float(price), weight=float(amount))
        return CountedItem(name=name, price_per_unit=float(price), quantity=int(amount))
