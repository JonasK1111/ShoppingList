"""
factories.py
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

from models import ShoppingItem, CountedItem, WeightedItem


class ItemFactory:
    """
    Stellt eine statische Methode bereit, um Items zu erzeugen.
    """

    @staticmethod
    def create_item(name: str, is_weighted: bool, amount: float, price: float) -> ShoppingItem:
        """
        Entscheidet anhand von 'is_weighted', welche Klasse instanziiert wird.

        Args:
            name: Name des Artikels
            is_weighted: True = Gewichtsartikel, False = Stückartikel
            amount: Der Wert für Menge oder Gewicht
            price: Preis pro Einheit

        Returns:
            Ein Objekt vom Typ ShoppingItem (bzw. einer Unterklasse).
        """
        if is_weighted:
            # Erstelle ein gewogenes Item. 'amount' wird als Gewicht interpretiert.
            return WeightedItem(name, price, float(amount))
        else:
            # Erstelle ein gezähltes Item. 'amount' wird zu int konvertiert.
            return CountedItem(name, price, int(amount))
