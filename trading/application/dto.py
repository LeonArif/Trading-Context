from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional


class PlaceOrderRequest(BaseModel):
    user_id: str
    symbol: str
    side: str
    order_type: str
    price: Optional[Decimal] = None
    quantity: Decimal = Field(gt=0)
    
    @validator('side')
    def validate_side(cls, v):
        if v not in ['BUY', 'SELL']:
            raise ValueError('side must be BUY or SELL')
        return v
    
    @validator('order_type')
    def validate_order_type(cls, v):
        if v not in ['LIMIT', 'MARKET']:
            raise ValueError('order_type must be LIMIT or MARKET')
        return v
    
    @validator('price')
    def validate_price(cls, v, values):
        if values.get('order_type') == 'LIMIT' and (v is None or v <= 0):
            raise ValueError('price is required and must be > 0 for LIMIT order')
        return v


class OrderResponse(BaseModel):
    order_id: str
    user_id: str
    symbol: str
    side: str
    order_type: str
    price: Decimal
    quantity: Decimal
    filled_quantity: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CancelOrderRequest(BaseModel):
    order_id: str
    user_id: str


class OrderDetailResponse(OrderResponse):
    remaining_quantity: Decimal
    filled_percentage: Decimal
    total_value: Decimal
    is_open: bool
    is_closed: bool


class OrderListResponse(BaseModel):
    total: int
    orders: list[OrderResponse]


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None