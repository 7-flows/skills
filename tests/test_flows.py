from sevenflows import FLOWS


def test_flows_are_the_approved_seven_in_order() -> None:
    assert FLOWS == ("test", "sell", "earn", "gather", "choose", "make", "care")
