"""Comprehensive tests for value objects"""
from decimal import Decimal
import pytest

from trading.domain.value_objects import (
    OrderSide, OrderType, OrderStatus, TradingPair, Money, create_money
)


# ============= OrderSide Tests =============
def test_order_side_buy():
    assert OrderSide.BUY.value == "BUY"


def test_order_side_sell():
    assert OrderSide.SELL.value == "SELL"


def test_order_side_from_string():
    assert OrderSide("BUY") == OrderSide.BUY
    assert OrderSide("SELL") == OrderSide.SELL


# ============= OrderType Tests =============
def test_order_type_limit():
    assert OrderType.LIMIT.value == "LIMIT"


def test_order_type_market():
    assert OrderType.MARKET.value == "MARKET"


def test_order_type_stop_loss():
    assert OrderType.STOP_LOSS.value == "STOP_LOSS"


def test_order_type_from_string():
    assert OrderType("LIMIT") == OrderType.LIMIT
    assert OrderType("MARKET") == OrderType.MARKET
    assert OrderType("STOP_LOSS") == OrderType.STOP_LOSS


# ============= OrderStatus Tests =============
def test_order_status_pending():
    assert OrderStatus.PENDING.value == "PENDING"


def test_order_status_open():
    assert OrderStatus.OPEN.value == "OPEN"


def test_order_status_partial_filled():
    assert OrderStatus.PARTIAL_FILLED.value == "PARTIAL_FILLED"


def test_order_status_filled():
    assert OrderStatus.FILLED.value == "FILLED"


def test_order_status_cancelled():
    assert OrderStatus.CANCELLED.value == "CANCELLED"


def test_order_status_rejected():
    assert OrderStatus.REJECTED.value == "REJECTED"


def test_order_status_from_string():
    assert OrderStatus("OPEN") == OrderStatus.OPEN
    assert OrderStatus("FILLED") == OrderStatus.FILLED


# ============= Money Tests =============
def test_money_creation():
    money = Money(Decimal("100.5"), "USDT")
    assert money.amount == Decimal("100.5")
    assert money.currency == "USDT"


def test_money_creation_from_int():
    money = Money(100, "BTC")
    assert money.amount == Decimal("100")
    assert money.currency == "BTC"


def test_money_creation_from_float():
    money = Money(100.5, "ETH")
    assert money.amount == Decimal("100.5")
    assert money.currency == "ETH"


def test_money_negative_amount_raises_error():
    with pytest.raises(ValueError, match="Amount cannot be negative"):
        Money(Decimal("-10"), "USDT")


def test_money_empty_currency_raises_error():
    with pytest.raises(ValueError, match="Currency is required"):
        Money(Decimal("100"), "")


def test_money_whitespace_currency_raises_error():
    with pytest.raises(ValueError, match="Currency is required"):
        Money(Decimal("100"), "   ")


def test_money_add_same_currency():
    money1 = Money(Decimal("100"), "USDT")
    money2 = Money(Decimal("50"), "USDT")
    result = money1.add(money2)
    assert result.amount == Decimal("150")
    assert result.currency == "USDT"


def test_money_add_different_currency_raises_error():
    money1 = Money(Decimal("100"), "USDT")
    money2 = Money(Decimal("50"), "BTC")
    with pytest.raises(ValueError, match="Cannot add different currencies"):
        money1.add(money2)


def test_money_subtract_same_currency():
    money1 = Money(Decimal("100"), "USDT")
    money2 = Money(Decimal("30"), "USDT")
    result = money1.subtract(money2)
    assert result.amount == Decimal("70")
    assert result.currency == "USDT"


def test_money_subtract_different_currency_raises_error():
    money1 = Money(Decimal("100"), "USDT")
    money2 = Money(Decimal("50"), "BTC")
    with pytest.raises(ValueError, match="Cannot subtract different currencies"):
        money1.subtract(money2)


def test_money_multiply():
    money = Money(Decimal("100"), "USDT")
    result = money.multiply(Decimal("2"))
    assert result.amount == Decimal("200")
    assert result.currency == "USDT"


def test_money_multiply_with_int():
    money = Money(Decimal("100"), "USDT")
    result = money.multiply(2)
    assert result.amount == Decimal("200")


def test_money_multiply_with_float():
    money = Money(Decimal("100"), "USDT")
    result = money.multiply(1.5)
    assert result.amount == Decimal("150")


def test_money_is_greater_than():
    money1 = Money(Decimal("100"), "USDT")
    money2 = Money(Decimal("50"), "USDT")
    assert money1.is_greater_than(money2)
    assert not money2.is_greater_than(money1)


def test_money_is_greater_than_different_currency_raises_error():
    money1 = Money(Decimal("100"), "USDT")
    money2 = Money(Decimal("50"), "BTC")
    with pytest.raises(ValueError, match="Cannot compare different currencies"):
        money1.is_greater_than(money2)


def test_money_is_zero():
    money = Money(Decimal("0"), "USDT")
    assert money.is_zero()


def test_money_is_not_zero():
    money = Money(Decimal("100"), "USDT")
    assert not money.is_zero()


def test_money_str():
    money = Money(Decimal("100.50"), "USDT")
    assert str(money) == "100.50 USDT"


def test_money_repr():
    money = Money(Decimal("100"), "BTC")
    assert repr(money) == "Money(amount=100, currency='BTC')"


# ============= TradingPair Tests =============
def test_trading_pair_creation():
    pair = TradingPair("BTC", "USDT")
    assert pair.base_currency == "BTC"
    assert pair.quote_currency == "USDT"
    assert pair.symbol == "BTC/USDT"


def test_trading_pair_uppercases_currencies():
    pair = TradingPair("btc", "usdt")
    assert pair.base_currency == "BTC"
    assert pair.quote_currency == "USDT"


def test_trading_pair_empty_base_currency_raises_error():
    with pytest.raises(ValueError, match="Base currency is required"):
        TradingPair("", "USDT")


def test_trading_pair_whitespace_base_currency_raises_error():
    with pytest.raises(ValueError, match="Base currency is required"):
        TradingPair("   ", "USDT")


def test_trading_pair_empty_quote_currency_raises_error():
    with pytest.raises(ValueError, match="Quote currency is required"):
        TradingPair("BTC", "")


def test_trading_pair_whitespace_quote_currency_raises_error():
    with pytest.raises(ValueError, match="Quote currency is required"):
        TradingPair("BTC", "   ")


def test_trading_pair_from_symbol_slash():
    pair = TradingPair.from_symbol("BTC/USDT")
    assert pair.base_currency == "BTC"
    assert pair.quote_currency == "USDT"


def test_trading_pair_from_symbol_dash():
    pair = TradingPair.from_symbol("ETH-USDT")
    assert pair.base_currency == "ETH"
    assert pair.quote_currency == "USDT"


def test_trading_pair_from_symbol_with_spaces():
    pair = TradingPair.from_symbol("BTC / USDT")
    assert pair.base_currency == "BTC"
    assert pair.quote_currency == "USDT"


def test_trading_pair_from_symbol_invalid_format_no_separator():
    with pytest.raises(ValueError, match="Invalid symbol format"):
        TradingPair.from_symbol("BTCUSDT")


def test_trading_pair_from_symbol_invalid_format_too_many_parts():
    with pytest.raises(ValueError, match="Invalid symbol format"):
        TradingPair.from_symbol("BTC/USDT/EUR")


def test_trading_pair_str():
    pair = TradingPair("BTC", "USDT")
    assert str(pair) == "BTC/USDT"


def test_trading_pair_repr():
    pair = TradingPair("ETH", "BTC")
    assert repr(pair) == "TradingPair('ETH', 'BTC')"


# ============= create_money() Tests =============
def test_create_money_from_decimal():
    money = create_money(Decimal("100.5"), "USDT")
    assert money.amount == Decimal("100.5")
    assert money.currency == "USDT"


def test_create_money_from_string():
    money = create_money("100.5", "BTC")
    assert money.amount == Decimal("100.5")
    assert money.currency == "BTC"


def test_create_money_from_float():
    money = create_money(100.5, "ETH")
    assert money.amount == Decimal("100.5")
    assert money.currency == "ETH"


def test_create_money_from_int():
    money = create_money(100, "USDT")
    assert money.amount == Decimal("100")
    assert money.currency == "USDT"
