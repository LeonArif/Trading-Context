"""Comprehensive tests for domain exceptions"""

import pytest

from trading.domain.exceptions import (
    TradingDomainException,
    OrderException,
    OrderNotFoundException,
    InvalidOrderOperationException,
    OrderValidationException,
    InsufficientBalanceException,
    BalanceLockException,
    InvalidTradingPairException,
    TradingPairNotActiveException,
    InvalidPriceException,
    PriceOutOfRangeException,
    InvalidQuantityException,
    QuantityBelowMinimumException,
    QuantityAboveMaximumException,
    UnauthorizedOrderAccessException,
    KYCRequiredException,
    TradeException,
    TradeNotFoundException,
    InvalidTradeException,
    MatchingEngineException,
    OrderMatchingFailedException,
    OrderBookFullException,
)


# ============= Base Exceptions =============
def test_trading_domain_exception():
    exc = TradingDomainException("Test error")
    assert str(exc) == "Test error"
    assert isinstance(exc, Exception)


def test_order_exception():
    exc = OrderException("Order error")
    assert str(exc) == "Order error"
    assert isinstance(exc, TradingDomainException)


def test_trade_exception():
    exc = TradeException("Trade error")
    assert str(exc) == "Trade error"
    assert isinstance(exc, TradingDomainException)


def test_matching_engine_exception():
    exc = MatchingEngineException("Matching error")
    assert str(exc) == "Matching error"
    assert isinstance(exc, TradingDomainException)


# ============= Order Exceptions =============
def test_order_not_found_exception():
    exc = OrderNotFoundException("ORD-123")
    assert exc.order_id == "ORD-123"
    assert "Order not found: ORD-123" in str(exc)
    assert isinstance(exc, OrderException)


def test_invalid_order_operation_exception():
    exc = InvalidOrderOperationException("Cannot cancel filled order")
    assert "Cannot cancel filled order" in str(exc)
    assert isinstance(exc, OrderException)


def test_order_validation_exception():
    exc = OrderValidationException("Invalid order data")
    assert "Invalid order data" in str(exc)
    assert isinstance(exc, OrderException)


# ============= Balance Exceptions =============
def test_insufficient_balance_exception():
    exc = InsufficientBalanceException("user123", "USDT", "1000", "500")
    assert exc.user_id == "user123"
    assert exc.currency == "USDT"
    assert exc.required == "1000"
    assert exc.available == "500"
    assert "Insufficient balance for user user123" in str(exc)
    assert "Required: 1000 USDT" in str(exc)
    assert "Available: 500 USDT" in str(exc)
    assert isinstance(exc, TradingDomainException)


def test_balance_lock_exception():
    exc = BalanceLockException("Cannot lock balance")
    assert "Cannot lock balance" in str(exc)
    assert isinstance(exc, TradingDomainException)


# ============= Trading Pair Exceptions =============
def test_invalid_trading_pair_exception_without_reason():
    exc = InvalidTradingPairException("BTC/USD")
    assert exc.symbol == "BTC/USD"
    assert "Invalid trading pair: BTC/USD" in str(exc)
    assert isinstance(exc, TradingDomainException)


def test_invalid_trading_pair_exception_with_reason():
    exc = InvalidTradingPairException("BTC/USD", "Symbol not supported")
    assert exc.symbol == "BTC/USD"
    assert "Invalid trading pair: BTC/USD" in str(exc)
    assert "Reason: Symbol not supported" in str(exc)


def test_trading_pair_not_active_exception():
    exc = TradingPairNotActiveException("ETH/BTC")
    assert exc.symbol == "ETH/BTC"
    assert "Trading pair not active: ETH/BTC" in str(exc)
    assert isinstance(exc, TradingDomainException)


# ============= Price Exceptions =============
def test_invalid_price_exception():
    exc = InvalidPriceException("0", "Price must be greater than 0")
    assert exc.price == "0"
    assert "Invalid price 0" in str(exc)
    assert "Price must be greater than 0" in str(exc)
    assert isinstance(exc, TradingDomainException)


def test_price_out_of_range_exception():
    exc = PriceOutOfRangeException("150000", "10000", "100000")
    assert exc.price == "150000"
    assert exc.min_price == "10000"
    assert exc.max_price == "100000"
    assert "Price 150000 out of range" in str(exc)
    assert "Allowed range: 10000 - 100000" in str(exc)
    assert isinstance(exc, TradingDomainException)


# ============= Quantity Exceptions =============
def test_invalid_quantity_exception():
    exc = InvalidQuantityException("0", "Quantity must be positive")
    assert exc.quantity == "0"
    assert "Invalid quantity 0" in str(exc)
    assert "Quantity must be positive" in str(exc)
    assert isinstance(exc, TradingDomainException)


def test_quantity_below_minimum_exception():
    exc = QuantityBelowMinimumException("0.0001", "0.001")
    assert exc.quantity == "0.0001"
    assert "Invalid quantity 0.0001" in str(exc)
    assert "Quantity must be at least 0.001" in str(exc)
    assert isinstance(exc, InvalidQuantityException)


def test_quantity_above_maximum_exception():
    exc = QuantityAboveMaximumException("2000000", "1000000")
    assert exc.quantity == "2000000"
    assert "Invalid quantity 2000000" in str(exc)
    assert "Quantity must not exceed 1000000" in str(exc)
    assert isinstance(exc, InvalidQuantityException)


# ============= Authorization Exceptions =============
def test_unauthorized_order_access_exception():
    exc = UnauthorizedOrderAccessException("user123", "ORD-456")
    assert exc.user_id == "user123"
    assert exc.order_id == "ORD-456"
    assert "User user123 not authorized to access order ORD-456" in str(exc)
    assert isinstance(exc, TradingDomainException)


def test_kyc_required_exception():
    exc = KYCRequiredException("user123", "TIER_2")
    assert exc.user_id == "user123"
    assert exc.required_tier == "TIER_2"
    assert "KYC verification required" in str(exc)
    assert "User user123 needs tier: TIER_2" in str(exc)
    assert isinstance(exc, TradingDomainException)


# ============= Trade Exceptions =============
def test_trade_not_found_exception():
    exc = TradeNotFoundException("TRD-789")
    assert exc.trade_id == "TRD-789"
    assert "Trade not found: TRD-789" in str(exc)
    assert isinstance(exc, TradeException)


def test_invalid_trade_exception():
    exc = InvalidTradeException("Invalid trade data")
    assert "Invalid trade data" in str(exc)
    assert isinstance(exc, TradeException)


# ============= Matching Engine Exceptions =============
def test_order_matching_failed_exception():
    exc = OrderMatchingFailedException("No matching orders found")
    assert "No matching orders found" in str(exc)
    assert isinstance(exc, MatchingEngineException)


def test_order_book_full_exception():
    exc = OrderBookFullException("BTC/USDT")
    assert exc.symbol == "BTC/USDT"
    assert "Orderbook full for BTC/USDT" in str(exc)
    assert isinstance(exc, MatchingEngineException)
