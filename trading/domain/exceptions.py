class TradingDomainException(Exception):
    pass


class OrderException(TradingDomainException):
    pass


class OrderNotFoundException(OrderException):
    def __init__(self, order_id: str):
        self.order_id = order_id
        super().__init__(f"Order not found: {order_id}")


class InvalidOrderOperationException(OrderException):
    pass


class OrderValidationException(OrderException):
    pass


class InsufficientBalanceException(TradingDomainException):
    def __init__(self, user_id: str, currency: str, required: str, available: str):
        self.user_id = user_id
        self.currency = currency
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient balance for user {user_id}. "
            f"Required: {required} {currency}, Available: {available} {currency}"
        )


class BalanceLockException(TradingDomainException):
    pass


class InvalidTradingPairException(TradingDomainException):
    def __init__(self, symbol: str, reason: str = None):
        self.symbol = symbol
        message = f"Invalid trading pair: {symbol}"
        if reason:
            message += f". Reason: {reason}"
        super().__init__(message)


class TradingPairNotActiveException(TradingDomainException):
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Trading pair not active: {symbol}")


class InvalidPriceException(TradingDomainException):
    def __init__(self, price: str, reason: str):
        self.price = price
        super().__init__(f"Invalid price {price}: {reason}")


class PriceOutOfRangeException(TradingDomainException):
    def __init__(self, price: str, min_price: str, max_price: str):
        self.price = price
        self.min_price = min_price
        self.max_price = max_price
        super().__init__(
            f"Price {price} out of range. "
            f"Allowed range: {min_price} - {max_price}"
        )


class InvalidQuantityException(TradingDomainException):
    def __init__(self, quantity: str, reason: str):
        self.quantity = quantity
        super().__init__(f"Invalid quantity {quantity}: {reason}")


class QuantityBelowMinimumException(InvalidQuantityException):
    def __init__(self, quantity: str, minimum: str):
        super().__init__(
            quantity,
            f"Quantity must be at least {minimum}"
        )


class QuantityAboveMaximumException(InvalidQuantityException):
    def __init__(self, quantity: str, maximum: str):
        super().__init__(
            quantity,
            f"Quantity must not exceed {maximum}"
        )


class UnauthorizedOrderAccessException(TradingDomainException):
    def __init__(self, user_id: str, order_id: str):
        self.user_id = user_id
        self.order_id = order_id
        super().__init__(
            f"User {user_id} not authorized to access order {order_id}"
        )


class KYCRequiredException(TradingDomainException):
    def __init__(self, user_id: str, required_tier: str):
        self.user_id = user_id
        self.required_tier = required_tier
        super().__init__(
            f"KYC verification required. "
            f"User {user_id} needs tier: {required_tier}"
        )


class TradeException(TradingDomainException):
    pass


class TradeNotFoundException(TradeException):
    def __init__(self, trade_id: str):
        self.trade_id = trade_id
        super().__init__(f"Trade not found: {trade_id}")


class InvalidTradeException(TradeException):
    pass


class MatchingEngineException(TradingDomainException):
    pass


class OrderMatchingFailedException(MatchingEngineException):
    pass


class OrderBookFullException(MatchingEngineException):
    def __init__(self, symbol: str):
        self.symbol = symbol
        super().__init__(f"Orderbook full for {symbol}")