from decimal import Decimal
from enum import Enum
from dataclasses import dataclass


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError(f"Amount cannot be negative: {self.amount}")

        if not self.currency or not self.currency.strip():
            raise ValueError("Currency is required")

        if not isinstance(self.amount, Decimal):
            object.__setattr__(self, "amount", Decimal(str(self.amount)))

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot add different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount + other.amount, self.currency)

    def subtract(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError(
                f"Cannot subtract different currencies: {self.currency} and {other.currency}"
            )
        return Money(self.amount - other.amount, self.currency)

    def multiply(self, factor: Decimal) -> "Money":
        if not isinstance(factor, Decimal):
            factor = Decimal(str(factor))
        return Money(self.amount * factor, self.currency)

    def is_greater_than(self, other: "Money") -> bool:
        if self.currency != other.currency:
            raise ValueError("Cannot compare different currencies")
        return self.amount > other.amount

    def is_zero(self) -> bool:
        return self.amount == Decimal("0")

    def __str__(self):
        return f"{self.amount} {self.currency}"

    def __repr__(self):
        return f"Money(amount={self.amount}, currency='{self.currency}')"


@dataclass(frozen=True)
class TradingPair:
    base_currency: str
    quote_currency: str

    def __post_init__(self):
        if not self.base_currency or not self.base_currency.strip():
            raise ValueError("Base currency is required")

        if not self.quote_currency or not self.quote_currency.strip():
            raise ValueError("Quote currency is required")

        object.__setattr__(self, "base_currency", self.base_currency.upper())
        object.__setattr__(self, "quote_currency", self.quote_currency.upper())

    @property
    def symbol(self) -> str:
        return f"{self.base_currency}/{self.quote_currency}"

    @staticmethod
    def from_symbol(symbol: str) -> "TradingPair":
        if "/" in symbol:
            parts = symbol.split("/")
        elif "-" in symbol:
            parts = symbol.split("-")
        else:
            raise ValueError(
                f"Invalid symbol format: {symbol}. Expected format: BTC/USDT or BTC-USDT"
            )

        if len(parts) != 2:
            raise ValueError(f"Invalid symbol format: {symbol}")

        return TradingPair(parts[0].strip(), parts[1].strip())

    def __str__(self):
        return self.symbol

    def __repr__(self):
        return f"TradingPair('{self.base_currency}', '{self.quote_currency}')"


def create_money(amount: float | Decimal | str, currency: str) -> Money:
    if isinstance(amount, str):
        amount = Decimal(amount)
    elif isinstance(amount, float):
        amount = Decimal(str(amount))

    return Money(amount, currency)
