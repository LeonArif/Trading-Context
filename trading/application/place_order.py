from decimal import Decimal
from sqlalchemy.orm import Session

from trading.domain.order import Order
from trading.domain.value_objects import OrderSide, OrderType
from trading.infrastructure.repository import OrderRepository
from .dto import PlaceOrderRequest, OrderResponse


class PlaceOrderUseCase:
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.order_repo = OrderRepository(db_session)
    
    def execute(self, request: PlaceOrderRequest) -> OrderResponse:
        
        side = OrderSide[request.side]
        order_type = OrderType[request.order_type]
        
        if order_type == OrderType.LIMIT:
            order = Order.place_limit_order(
                user_id=request.user_id,
                symbol=request.symbol,
                side=side,
                price=request.price,
                quantity=request.quantity
            )
        else:
            order = Order.place_market_order(
                user_id=request.user_id,
                symbol=request.symbol,
                side=side,
                quantity=request.quantity
            )
        
        order.open()
        
        self.order_repo.save(order)
        
        return self._to_response(order)
    
    def _to_response(self, order: Order) -> OrderResponse:
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