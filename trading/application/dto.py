from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List


class PlaceOrderRequest(BaseModel):
    user_id: str
    symbol: str
    side: str
    order_type: str
    price: Optional[Decimal] = None
    quantity: Decimal = Field(gt=0)

    @field_validator("side")
    @classmethod
    def validate_side(cls, v):
        if v not in ["BUY", "SELL"]:
            raise ValueError("side must be BUY or SELL")
        return v

    @field_validator("order_type")
    @classmethod
    def validate_order_type(cls, v):
        if v not in ["LIMIT", "MARKET"]:
            raise ValueError("order_type must be LIMIT or MARKET")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v, info):
        order_type = info.data.get("order_type")
        if order_type == "LIMIT" and (v is None or v <= 0):
            raise ValueError("price is required and must be > 0 for LIMIT order")
        return v


class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    orders: List[OrderResponse]


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[dict] = None
