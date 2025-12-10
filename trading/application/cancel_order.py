from sqlalchemy.orm import Session

from trading.domain.exceptions import UnauthorizedOrderAccessException
from trading.infrastructure.repository import OrderRepository
from . dto import CancelOrderRequest, OrderResponse


class CancelOrderUseCase:
    def __init__(self, db:  Session):
        self. order_repo = OrderRepository(db)
    
    def execute(self, request: CancelOrderRequest) -> OrderResponse:
        order = self.order_repo.find_by_id(request.order_id)
        
        if order.user_id != request. user_id:
            raise UnauthorizedOrderAccessException(request. user_id, request.order_id)
        
        order. cancel()
        self.order_repo.save(order)
        
        return OrderResponse(
            order_id=order.order_id,
            user_id=order.user_id,
            symbol=order.trading_pair.symbol,
            side=order.side.value,
            order_type=order.order_type.value,
            price=order.price.amount,  
            quantity=order.quantity,        
            filled_quantity=order.filled_quantity,  
            status=order.status.value,
            created_at=order.created_at,  
            updated_at=order.updated_at        
        )