from sqlalchemy.orm import Session
from decimal import Decimal

from trading.infrastructure.repository import OrderRepository
from trading.application.dto import PlaceOrderRequest, OrderResponse
from trading. domain.order import Order
from trading.domain.value_objects import TradingPair, OrderSide, OrderType, Money


class PlaceOrderUseCase: 
    def __init__(self, db: Session):
        self.order_repo = OrderRepository(db)
    
    def execute(self, request: PlaceOrderRequest) -> OrderResponse:
        trading_pair = TradingPair.from_symbol(request.symbol)
        price = Money(
            amount=Decimal(str(request.price)), 
            currency=trading_pair.quote_currency
        )
        
        order = Order. create(
            user_id=request.user_id,
            trading_pair=trading_pair,
            side=OrderSide[request.side],
            order_type=OrderType[request.order_type],
            price=price,
            quantity=Decimal(str(request.quantity))
        )
        
        # Transition order from PENDING to OPEN status
        order.open()
        
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
            updated_at=order. updated_at      
        )