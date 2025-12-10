from sqlalchemy.orm import Session
from typing import Optional

from trading.infrastructure.repository import OrderRepository
from . dto import OrderListResponse, OrderResponse


class ListOrdersUseCase:
    def __init__(self, db: Session):
        self.order_repo = OrderRepository(db)
    
    def execute(self, user_id: str, symbol: Optional[str] = None) -> OrderListResponse:
        orders = self.order_repo.find_by_user_id(user_id)
        
        if symbol:
            orders = [o for o in orders if o.trading_pair.symbol == symbol]
        
        order_responses = [
            OrderResponse(
                order_id=o.order_id,
                user_id=o.user_id,
                symbol=o.trading_pair.symbol,
                side=o.side.value,
                order_type=o.order_type.value,
                price=o.price.amount,
                quantity=o.quantity,
                filled_quantity=o.filled_quantity,
                status=o.status.value,
                created_at=o.created_at,
                updated_at=o.updated_at
            )
            for o in orders
        ]
        
        return OrderListResponse(
            total=len(order_responses),
            orders=order_responses
        )