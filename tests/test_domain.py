from trading.domain.value_objects import OrderSide, OrderType, OrderStatus
import pytest

def test_order_side_enum():
    assert OrderSide.BUY.value == "BUY"
    assert OrderSide.SELL.value == "SELL"

def test_order_type_enum():
    assert OrderType.LIMIT.value == "LIMIT"
    assert OrderType.MARKET.value == "MARKET"

def test_order_status_enum():
    assert OrderStatus.OPEN.value == "OPEN"
    assert OrderStatus.CANCELLED.value == "CANCELLED"
    assert OrderStatus.FILLED.value == "FILLED"

def test_invalid_side():
    with pytest.raises(ValueError):
        OrderSide("INVALID")