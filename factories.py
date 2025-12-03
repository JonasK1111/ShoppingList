"""
factories.py
Implementierung des Factory Patterns zur Objekterzeugung.
"""

from models import ShoppingItem, CountedItem, WeightedItem


class ItemFactory:
    """
    Factory-Klasse, die die Komplexität der Objekterzeugung kapselt.
    """

    @staticmethod
    def create_item(name: str, is_weighted: bool, amount: float, price: float) -> ShoppingItem:
        if is_weighted:
            return WeightedItem(name, price, float(amount))
        else:
            return CountedItem(name, price, int(amount))
