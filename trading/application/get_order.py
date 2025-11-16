from sqlalchemy.orm import Session

from trading.domain.exceptions import UnauthorizedOrderAccessException
from trading.infrastructure.repository import OrderRepository
from .dto import OrderDetailResponse


class GetOrderUseCase:
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.order_repo = OrderRepository(db_session)
    
    def execute(self, order_id: str, user_id: str) -> OrderDetailResponse:
        
        order = self.order_repo.find_by_id(order_id)
        
        if order.user_id != user_id:
            raise UnauthorizedOrderAccessException(user_id, order_id)
        
        return OrderDetailResponse(
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
            updated_at=order.updated_at,
            remaining_quantity=order.remaining_quantity,
            filled_percentage=order.filled_percentage,
            total_value=order.total_value.amount,
            is_open=order.is_open,
            is_closed=order.is_closed
        )