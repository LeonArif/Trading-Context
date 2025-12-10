from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from trading. domain.order import Order
from trading.domain.value_objects import (
    Money, TradingPair, OrderSide, OrderType, OrderStatus
)
from trading.domain.exceptions import OrderNotFoundException
from .models import OrderModel, OrderSideDB, OrderTypeDB, OrderStatusDB


class OrderRepository: 
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def save(self, order: Order) -> None:
        order_model = self._domain_to_model(order)
        self.db.merge(order_model)
        # Don't flush() or commit() here - let the endpoint handle transaction
    
    def find_by_id(self, order_id: str) -> Order:
        order_model = self.db.query(OrderModel).filter_by(
            order_id=order_id
        ).first()
        
        if not order_model:
            raise OrderNotFoundException(order_id)
        
        return self._model_to_domain(order_model)
    
    def find_by_user_id(self, user_id:  str) -> List[Order]:
        order_models = self.db.query(OrderModel).filter_by(
            user_id=user_id
        ).order_by(OrderModel.created_at.desc()).all()
        
        return [self._model_to_domain(om) for om in order_models]
    
    def find_by_symbol(self, symbol: str) -> List[Order]:
        order_models = self.db.query(OrderModel).filter_by(
            symbol=symbol
        ).order_by(OrderModel.created_at. desc()).all()
        
        return [self._model_to_domain(om) for om in order_models]
    
    def find_open_orders(self, user_id: Optional[str] = None) -> List[Order]:
        query = self.db. query(OrderModel).filter(
            OrderModel.status.in_([
                OrderStatusDB. OPEN,
                OrderStatusDB. PARTIAL_FILLED
            ])
        )
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        order_models = query. order_by(OrderModel.created_at.desc()).all()
        
        return [self._model_to_domain(om) for om in order_models]
    
    def find_by_status(self, status: OrderStatus, user_id: Optional[str] = None) -> List[Order]:
        status_db = OrderStatusDB[status.value]
        
        query = self.db. query(OrderModel).filter_by(status=status_db)
        
        if user_id: 
            query = query.filter_by(user_id=user_id)
        
        order_models = query.order_by(OrderModel.created_at.desc()).all()
        
        return [self._model_to_domain(om) for om in order_models]
    
    def delete(self, order_id: str) -> None:
        order_model = self.db.query(OrderModel).filter_by(
            order_id=order_id
        ).first()
        
        if order_model:
            self.db.delete(order_model)
    
    def _domain_to_model(self, order: Order) -> OrderModel:
        return OrderModel(
            order_id=order.order_id,
            user_id=order.user_id,
            symbol=order.trading_pair.symbol,
            side=OrderSideDB[order. side.value],
            type=OrderTypeDB[order.order_type.value],
            price=order.price.amount,
            quantity=order.quantity,
            filled_quantity=order.filled_quantity,
            status=OrderStatusDB[order.status.value],
            created_at=order. created_at,
            updated_at=order.updated_at
        )
    
    def _model_to_domain(self, order_model: OrderModel) -> Order:
        trading_pair = TradingPair.from_symbol(order_model.symbol)
        
        price = Money(
            amount=Decimal(str(order_model.price)),
            currency=trading_pair.quote_currency
        )
        
        return Order(
            order_id=order_model.order_id,
            user_id=order_model.user_id,
            trading_pair=trading_pair,
            side=OrderSide[order_model.side. value],
            order_type=OrderType[order_model.type.value],
            price=price,
            quantity=Decimal(str(order_model.quantity)),
            status=OrderStatus[order_model.status.value],
            filled_quantity=Decimal(str(order_model.filled_quantity)),
            created_at=order_model.created_at,
            updated_at=order_model.updated_at
        )
    

class TradeRepository:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def save(self, trade) -> None:
        pass
    
    def find_by_id(self, trade_id: str):
        pass
    
    def find_by_symbol(self, symbol: str):
        pass