from decimal import Decimal
import pytest
from trading.domain.value_objects import OrderSide, OrderType, OrderStatus, TradingPair, Money
from trading.domain.exceptions import InvalidPriceException, InvalidQuantityException

def test_order_side_enum():
    assert OrderSide.BUY. value == "BUY"
    assert OrderSide.SELL.value == "SELL"

def test_order_type_enum():
    assert OrderType. LIMIT.value == "LIMIT"
    assert OrderType.MARKET.value == "MARKET"

def test_order_status_enum():
    assert OrderStatus. OPEN.value == "OPEN"
    assert OrderStatus.CANCELLED.value == "CANCELLED"

def test_trading_pair():
    pair = TradingPair. from_symbol("BTC/USDT")
    assert pair.base_currency == "BTC"
    assert pair.quote_currency == "USDT"

def test_money():
    money = Money(Decimal("100.5"), "USDT")
    assert money.amount == Decimal("100.5")
    assert money.currency == "USDT"