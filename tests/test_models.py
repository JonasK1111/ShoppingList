from shopping_list.models import CountedItem, WeightedItem


def test_counted_total():
    item = CountedItem("Gurke", 1.5, 2)
    assert item.calculate_total() == 3.0


def test_weighted_total():
    item = WeightedItem("Äpfel", 2.0, 1.25)
    assert abs(item.calculate_total() - 2.5) < 1e-9
