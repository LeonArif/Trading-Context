"""Comprehensive tests for Order domain model"""
from decimal import Decimal
from datetime import datetime, timezone
import pytest

from trading.domain.order import Order
from trading.domain.value_objects import Money, TradingPair, OrderSide, OrderType, OrderStatus
from trading.domain.exceptions import (
    InvalidOrderOperationException,
    InvalidPriceException,
    InvalidQuantityException,
    QuantityBelowMinimumException,
    OrderValidationException,
)


# ============= Order Creation Tests =============
def test_order_creation():
    trading_pair = TradingPair("BTC", "USDT")
    price = Money(Decimal("50000"), "USDT")
    quantity = Decimal("1.5")
    
    order = Order(
        order_id="ORD-TEST",
        user_id="user123",
        trading_pair=trading_pair,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        price=price,
        quantity=quantity,
    )
    
    assert order.order_id == "ORD-TEST"
    assert order.user_id == "user123"
    assert order.trading_pair == trading_pair
    assert order.side == OrderSide.BUY
    assert order.order_type == OrderType.LIMIT
    assert order.price == price
    assert order.quantity == quantity
    assert order.status == OrderStatus.PENDING
    assert order.filled_quantity == Decimal("0")


def test_order_create_factory_method_limit():
    trading_pair = TradingPair("ETH", "USDT")
    price = Money(Decimal("3000"), "USDT")
    quantity = Decimal("2")
    
    order = Order.create(
        user_id="user123",
        trading_pair=trading_pair,
        side=OrderSide.SELL,
        order_type=OrderType.LIMIT,
        price=price,
        quantity=quantity
    )
    
    assert order.order_id.startswith("ORD-")
    assert order.user_id == "user123"
    assert order.status == OrderStatus.PENDING
    assert order.filled_quantity == Decimal("0")


def test_order_create_factory_method_market():
    trading_pair = TradingPair("BTC", "USDT")
    price = Money(Decimal("0"), "USDT")
    quantity = Decimal("0.5")
    
    order = Order.create(
        user_id="user456",
        trading_pair=trading_pair,
        side=OrderSide.BUY,
        order_type=OrderType.MARKET,
        price=price,
        quantity=quantity
    )
    
    assert order.order_type == OrderType.MARKET
    assert order.status == OrderStatus.PENDING


def test_place_limit_order():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    assert order.order_id.startswith("ORD-")
    assert order.user_id == "user123"
    assert order.trading_pair.symbol == "BTC/USDT"
    assert order.side == OrderSide.BUY
    assert order.order_type == OrderType.LIMIT
    assert order.price.amount == Decimal("50000")
    assert order.quantity == Decimal("1")


def test_place_market_order():
    order = Order.place_market_order(
        user_id="user456",
        symbol="ETH/USDT",
        side=OrderSide.SELL,
        quantity=Decimal("5")
    )
    
    assert order.order_id.startswith("ORD-")
    assert order.user_id == "user456"
    assert order.trading_pair.symbol == "ETH/USDT"
    assert order.side == OrderSide.SELL
    assert order.order_type == OrderType.MARKET
    assert order.quantity == Decimal("5")


# ============= Order State Transition Tests =============
def test_order_open():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    assert order.status == OrderStatus.PENDING
    order.open()
    assert order.status == OrderStatus.OPEN


def test_order_open_from_non_pending_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    with pytest.raises(InvalidOrderOperationException):
        order.open()


def test_order_fill_complete():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    order.fill(Decimal("1"))
    
    assert order.filled_quantity == Decimal("1")
    assert order.status == OrderStatus.FILLED


def test_order_partial_fill():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("2")
    )
    order.open()
    
    order.fill(Decimal("0.5"))
    
    assert order.filled_quantity == Decimal("0.5")
    assert order.status == OrderStatus.PARTIAL_FILLED
    assert order.remaining_quantity == Decimal("1.5")


def test_order_multiple_partial_fills():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("3")
    )
    order.open()
    
    order.fill(Decimal("1"))
    assert order.status == OrderStatus.PARTIAL_FILLED
    assert order.filled_quantity == Decimal("1")
    
    order.fill(Decimal("1"))
    assert order.status == OrderStatus.PARTIAL_FILLED
    assert order.filled_quantity == Decimal("2")
    
    order.fill(Decimal("1"))
    assert order.status == OrderStatus.FILLED
    assert order.filled_quantity == Decimal("3")


def test_order_fill_with_execution_price():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    execution_price = Money(Decimal("49500"), "USDT")
    order.fill(Decimal("1"), execution_price)
    
    assert order.price == execution_price
    assert order.price.amount == Decimal("49500")


def test_order_fill_zero_quantity_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    with pytest.raises(InvalidQuantityException, match="Filled quantity must be greater than 0"):
        order.fill(Decimal("0"))


def test_order_fill_negative_quantity_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    with pytest.raises(InvalidQuantityException):
        order.fill(Decimal("-0.5"))


def test_order_fill_exceeds_quantity_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    with pytest.raises(InvalidQuantityException, match="Cannot fill 2"):
        order.fill(Decimal("2"))


def test_order_fill_from_pending_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    with pytest.raises(InvalidOrderOperationException):
        order.fill(Decimal("1"))


def test_order_cancel_from_open():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    order.cancel()
    
    assert order.status == OrderStatus.CANCELLED


def test_order_cancel_from_partial_filled():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("2")
    )
    order.open()
    order.fill(Decimal("0.5"))
    
    order.cancel()
    
    assert order.status == OrderStatus.CANCELLED


def test_order_cancel_from_filled_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    order.fill(Decimal("1"))
    
    with pytest.raises(InvalidOrderOperationException):
        order.cancel()


def test_order_cancel_from_pending_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    with pytest.raises(InvalidOrderOperationException):
        order.cancel()


def test_order_reject():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    order.reject("Insufficient balance")
    
    assert order.status == OrderStatus.REJECTED


def test_order_reject_from_non_pending_raises_error():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    with pytest.raises(InvalidOrderOperationException):
        order.reject("Test reason")


# ============= Order Properties Tests =============
def test_order_remaining_quantity():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("3")
    )
    order.open()
    order.fill(Decimal("1"))
    
    assert order.remaining_quantity == Decimal("2")


def test_order_filled_percentage():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("2")
    )
    order.open()
    order.fill(Decimal("1"))
    
    assert order.filled_percentage == Decimal("50")


def test_order_filled_percentage_zero_quantity():
    order = Order(
        order_id="ORD-TEST",
        user_id="user123",
        trading_pair=TradingPair("BTC", "USDT"),
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        price=Money(Decimal("50000"), "USDT"),
        quantity=Decimal("0"),
    )
    
    assert order.filled_percentage == Decimal("0")


def test_order_total_value():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("2")
    )
    
    total_value = order.total_value
    assert total_value.amount == Decimal("100000")
    assert total_value.currency == "USDT"


def test_order_filled_value():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("2")
    )
    order.open()
    order.fill(Decimal("1"))
    
    filled_value = order.filled_value
    assert filled_value.amount == Decimal("50000")
    assert filled_value.currency == "USDT"


def test_order_is_open():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    assert not order.is_open
    
    order.open()
    assert order.is_open
    
    order.fill(Decimal("1"))
    assert not order.is_open


def test_order_is_closed():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order.open()
    
    assert not order.is_closed
    
    order.fill(Decimal("1"))
    assert order.is_closed


# ============= Order Validation Tests =============
def test_order_validation_negative_price_raises_error():
    # Negative price will fail at Money creation level
    with pytest.raises(ValueError):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("-1000"),
            quantity=Decimal("1")
        )


def test_order_validation_zero_price_raises_error():
    with pytest.raises(InvalidPriceException, match="Price must be greater than 0"):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("0"),
            quantity=Decimal("1")
        )


def test_order_validation_price_below_minimum_raises_error():
    with pytest.raises(InvalidPriceException, match="Price must be at least"):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("0.001"),
            quantity=Decimal("1")
        )


def test_order_validation_price_above_maximum_raises_error():
    with pytest.raises(InvalidPriceException, match="Price must not exceed"):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("2000000000"),
            quantity=Decimal("1")
        )


def test_order_validation_negative_quantity_raises_error():
    with pytest.raises(InvalidQuantityException, match="Quantity must be greater than 0"):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("50000"),
            quantity=Decimal("-1")
        )


def test_order_validation_zero_quantity_raises_error():
    with pytest.raises(InvalidQuantityException, match="Quantity must be greater than 0"):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("50000"),
            quantity=Decimal("0")
        )


def test_order_validation_quantity_below_minimum_raises_error():
    with pytest.raises(QuantityBelowMinimumException):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("50000"),
            quantity=Decimal("0.000000001")
        )


def test_order_validation_quantity_above_maximum_raises_error():
    with pytest.raises(InvalidQuantityException, match="Quantity must not exceed"):
        Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal("50000"),
            quantity=Decimal("2000000")
        )


def test_order_validation_currency_mismatch_raises_error():
    trading_pair = TradingPair("BTC", "USDT")
    price = Money(Decimal("50000"), "EUR")  # Wrong currency
    
    with pytest.raises(OrderValidationException, match="Price currency EUR does not match"):
        Order.create(
            user_id="user123",
            trading_pair=trading_pair,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            price=price,
            quantity=Decimal("1")
        )


# ============= Order String Representation Tests =============
def test_order_str():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    result = str(order)
    assert "BUY" in result
    assert "BTC/USDT" in result
    assert "50000" in result


def test_order_repr():
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    result = repr(order)
    assert "Order(" in result
    assert "user_id='user123'" in result
