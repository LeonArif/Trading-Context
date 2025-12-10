from datetime import datetime
from decimal import Decimal
from uuid import uuid4
from typing import Optional

from .value_objects import Money, TradingPair, OrderSide, OrderType, OrderStatus
from .exceptions import (
    InvalidOrderOperationException,
    OrderValidationException,
    InvalidPriceException,
    InvalidQuantityException,
    QuantityBelowMinimumException
)


class Order:
    MIN_QUANTITY = Decimal("0.00000001")
    MAX_QUANTITY = Decimal("1000000")
    MIN_PRICE = Decimal("0.01")
    MAX_PRICE = Decimal("1000000000")
    
    def __init__(
        self,
        order_id: str,
        user_id: str,
        trading_pair: TradingPair,
        side: OrderSide,
        order_type: OrderType,
        price: Money,
        quantity:  Decimal,
        status: OrderStatus = OrderStatus.PENDING,
        filled_quantity: Decimal = Decimal("0"),
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.order_id = order_id
        self.user_id = user_id
        self.trading_pair = trading_pair
        self.side = side
        self.order_type = order_type
        self.price = price
        self. quantity = quantity
        self.status = status
        self.filled_quantity = filled_quantity
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
    
    @classmethod
    def create(
        cls,
        user_id: str,
        trading_pair: TradingPair,
        side: OrderSide,
        order_type: OrderType,
        price:  Money,
        quantity: Decimal,
    ) -> 'Order':
        """Factory method untuk membuat order baru (generic)"""
        order_id = f"ORD-{uuid4().hex[:12].upper()}"
        
        order = cls(
            order_id=order_id,
            user_id=user_id,
            trading_pair=trading_pair,
            side=side,
            order_type=order_type,
            price=price,
            quantity=quantity,
            status=OrderStatus.PENDING,
            filled_quantity=Decimal("0")
        )
        
        # Validasi sesuai order type
        if order_type == OrderType.LIMIT:
            order._validate()
        elif order_type == OrderType.MARKET:
            order._validate_quantity()
        
        return order
    
    @staticmethod
    def place_limit_order(
        user_id: str,
        symbol: str,
        side: OrderSide,
        price: Decimal,
        quantity: Decimal
    ) -> 'Order':
        order_id = f"ORD-{uuid4().hex[:12].upper()}"
        trading_pair = TradingPair.from_symbol(symbol)
        price_money = Money(price, trading_pair.quote_currency)
        
        order = Order(
            order_id=order_id,
            user_id=user_id,
            trading_pair=trading_pair,
            side=side,
            order_type=OrderType.LIMIT,
            price=price_money,
            quantity=quantity,
            status=OrderStatus.PENDING,
            filled_quantity=Decimal("0")
        )
        
        order._validate()
        return order
    
    @staticmethod
    def place_market_order(
        user_id: str,
        symbol: str,
        side: OrderSide,
        quantity: Decimal
    ) -> 'Order':
        order_id = f"ORD-{uuid4().hex[:12].upper()}"
        trading_pair = TradingPair.from_symbol(symbol)
        price_money = Money(Decimal("0"), trading_pair.quote_currency)
        
        order = Order(
            order_id=order_id,
            user_id=user_id,
            trading_pair=trading_pair,
            side=side,
            order_type=OrderType.MARKET,
            price=price_money,
            quantity=quantity,
            status=OrderStatus.PENDING,
            filled_quantity=Decimal("0")
        )
        
        order._validate_quantity()
        return order
    
    def open(self):
        if self.status != OrderStatus.PENDING: 
            raise InvalidOrderOperationException(
                f"Cannot open order with status {self.status}. Expected: PENDING"
            )
        
        self.status = OrderStatus.OPEN
        self. updated_at = datetime.utcnow()
    
    def fill(self, filled_quantity:  Decimal, execution_price: Optional[Money] = None):
        if self.status not in [OrderStatus.OPEN, OrderStatus. PARTIAL_FILLED]:
            raise InvalidOrderOperationException(
                f"Cannot fill order with status {self.status}"
            )
        
        if filled_quantity <= 0:
            raise InvalidQuantityException(
                str(filled_quantity),
                "Filled quantity must be greater than 0"
            )
        
        new_filled_quantity = self. filled_quantity + filled_quantity
        
        if new_filled_quantity > self.quantity:
            raise InvalidQuantityException(
                str(filled_quantity),
                f"Cannot fill {filled_quantity}. "
                f"Remaining quantity: {self.remaining_quantity}"
            )
        
        self.filled_quantity = new_filled_quantity
        
        if execution_price:
            self.price = execution_price
        
        if self.filled_quantity >= self.quantity:
            self.status = OrderStatus.FILLED
        else:
            self. status = OrderStatus.PARTIAL_FILLED
        
        self. updated_at = datetime.utcnow()
    
    def cancel(self):
        if self.status not in [OrderStatus. OPEN, OrderStatus.PARTIAL_FILLED]:
            raise InvalidOrderOperationException(
                f"Cannot cancel order with status {self.status}. "
                f"Only OPEN or PARTIAL_FILLED orders can be cancelled."
            )
        
        self. status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
    
    def reject(self, reason: str):
        if self.status != OrderStatus.PENDING: 
            raise InvalidOrderOperationException(
                f"Cannot reject order with status {self.status}.  Expected: PENDING"
            )
        
        self.status = OrderStatus.REJECTED
        self.updated_at = datetime.utcnow()
    
    @property
    def remaining_quantity(self) -> Decimal:
        return self.quantity - self. filled_quantity
    
    @property
    def filled_percentage(self) -> Decimal:
        if self.quantity == 0:
            return Decimal("0")
        return (self.filled_quantity / self.quantity) * Decimal("100")
    
    @property
    def total_value(self) -> Money:
        total_amount = self.price. amount * self.quantity
        return Money(total_amount, self. price.currency)
    
    @property
    def filled_value(self) -> Money:
        filled_amount = self.price. amount * self.filled_quantity
        return Money(filled_amount, self.price.currency)
    
    @property
    def is_open(self) -> bool:
        return self.status in [OrderStatus.OPEN, OrderStatus.PARTIAL_FILLED]
    
    @property
    def is_closed(self) -> bool:
        return self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus. REJECTED]
    
    def _validate(self):
        self._validate_price()
        self._validate_quantity()
    
    def _validate_price(self):
        if self.order_type == OrderType.MARKET: 
            return
        
        if self.price.amount <= 0:
            raise InvalidPriceException(
                str(self. price.amount),
                "Price must be greater than 0"
            )
        
        if self.price.amount < self.MIN_PRICE:
            raise InvalidPriceException(
                str(self.price.amount),
                f"Price must be at least {self.MIN_PRICE}"
            )
        
        if self.price.amount > self. MAX_PRICE:
            raise InvalidPriceException(
                str(self.price.amount),
                f"Price must not exceed {self.MAX_PRICE}"
            )
        
        if self.price.currency != self. trading_pair.quote_currency:
            raise OrderValidationException(
                f"Price currency {self.price.currency} does not match "
                f"quote currency {self.trading_pair.quote_currency}"
            )
    
    def _validate_quantity(self):
        if self.quantity <= 0:
            raise InvalidQuantityException(
                str(self.quantity),
                "Quantity must be greater than 0"
            )
        
        if self.quantity < self.MIN_QUANTITY:
            raise QuantityBelowMinimumException(
                str(self.quantity),
                str(self.MIN_QUANTITY)
            )
        
        if self.quantity > self.MAX_QUANTITY:
            raise InvalidQuantityException(
                str(self.quantity),
                f"Quantity must not exceed {self.MAX_QUANTITY}"
            )
    
    def __str__(self):
        return (
            f"Order({self. order_id}, "
            f"{self.side.value} {self.quantity} {self.trading_pair.symbol} "
            f"@ {self.price}, status={self.status.value})"
        )
    
    def __repr__(self):
        return (
            f"Order(order_id='{self.order_id}', "
            f"user_id='{self. user_id}', "
            f"trading_pair={self. trading_pair}, "
            f"side={self.side}, "
            f"type={self. order_type}, "
            f"price={self.price}, "
            f"quantity={self. quantity}, "
            f"status={self.status})"
        )