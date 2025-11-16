from sqlalchemy import Column, String, Numeric, DateTime, Enum as SQLEnum
from database import Base
import enum


class OrderSideDB(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderTypeDB(str, enum.Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"


class OrderStatusDB(str, enum.Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    PARTIAL_FILLED = "PARTIAL_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


class OrderModel(Base):
    __tablename__ = "orders"
    
    order_id = Column(String(50), primary_key=True, index=True)
    user_id = Column(String(50), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(SQLEnum(OrderSideDB), nullable=False)
    type = Column(SQLEnum(OrderTypeDB), nullable=False)
    price = Column(Numeric(precision=20, scale=8), nullable=False)
    quantity = Column(Numeric(precision=20, scale=8), nullable=False)
    filled_quantity = Column(Numeric(precision=20, scale=8), nullable=False, default=0)
    status = Column(SQLEnum(OrderStatusDB), nullable=False, default=OrderStatusDB.PENDING, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    
    def __repr__(self):
        return (
            f"<OrderModel(order_id={self.order_id}, "
            f"user_id={self.user_id}, "
            f"symbol={self.symbol}, "
            f"side={self.side}, "
            f"status={self.status})>"
        )


class TradeModel(Base):
    __tablename__ = "trades"
    
    trade_id = Column(String(50), primary_key=True, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    buy_order_id = Column(String(50), nullable=False, index=True)
    sell_order_id = Column(String(50), nullable=False, index=True)
    buyer_user_id = Column(String(50), nullable=False, index=True)
    seller_user_id = Column(String(50), nullable=False, index=True)
    price = Column(Numeric(precision=20, scale=8), nullable=False)
    quantity = Column(Numeric(precision=20, scale=8), nullable=False)
    buyer_fee = Column(Numeric(precision=20, scale=8), nullable=False, default=0)
    seller_fee = Column(Numeric(precision=20, scale=8), nullable=False, default=0)
    executed_at = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self):
        return (
            f"<TradeModel(trade_id={self.trade_id}, "
            f"symbol={self.symbol}, "
            f"price={self.price}, "
            f"quantity={self.quantity})>"
        )