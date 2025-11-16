from decimal import Decimal
from database import SessionLocal, Base, engine
from trading.application.place_order import PlaceOrderUseCase
from trading.application.cancel_order import CancelOrderUseCase
from trading.application.get_order import GetOrderUseCase
from trading.application.list_orders import ListOrdersUseCase
from trading.application.dto import PlaceOrderRequest, CancelOrderRequest

Base.metadata.create_all(bind=engine)

print("Testing Application Layer...")
print("=" * 60)

db = SessionLocal()

try:
    place_order_uc = PlaceOrderUseCase(db)
    
    print("\n1. Testing Place LIMIT Order:")
    request = PlaceOrderRequest(
        user_id="user123",
        symbol="BTC/USDT",
        side="BUY",
        order_type="LIMIT",
        price=Decimal("65000"),
        quantity=Decimal("0.5")
    )
    response = place_order_uc.execute(request)
    print(f"   ✅ Order created: {response.order_id}")
    print(f"   ✅ Status: {response.status}")
    
    order_id = response.order_id
    
    print("\n2. Testing Get Order:")
    get_order_uc = GetOrderUseCase(db)
    detail = get_order_uc.execute(order_id, "user123")
    print(f"   ✅ Order detail: {detail.order_id}")
    print(f"   ✅ Total value: {detail.total_value}")
    print(f"   ✅ Remaining: {detail.remaining_quantity}")
    
    print("\n3. Testing Place MARKET Order:")
    market_request = PlaceOrderRequest(
        user_id="user123",
        symbol="ETH/USDT",
        side="SELL",
        order_type="MARKET",
        quantity=Decimal("2.0")
    )
    market_response = place_order_uc.execute(market_request)
    print(f"   ✅ Market order: {market_response.order_id}")
    
    print("\n4. Testing List Orders:")
    list_orders_uc = ListOrdersUseCase(db)
    orders_list = list_orders_uc.execute("user123")
    print(f"   ✅ Total orders: {orders_list.total}")
    
    print("\n5. Testing Cancel Order:")
    cancel_uc = CancelOrderUseCase(db)
    cancel_request = CancelOrderRequest(
        order_id=order_id,
        user_id="user123"
    )
    cancelled = cancel_uc.execute(cancel_request)
    print(f"   ✅ Order cancelled: {cancelled.status}")
    
    print("\n" + "=" * 60)
    print("🎉 All application tests passed!")
    print("=" * 60)
    
finally:
    db.close()