from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from . auth import get_current_user
from trading.application.place_order import PlaceOrderUseCase
from trading.application.cancel_order import CancelOrderUseCase
from trading.application.get_order import GetOrderUseCase
from trading.application.list_orders import ListOrdersUseCase
from trading.application.dto import (
    PlaceOrderRequest,
    CancelOrderRequest,
    OrderResponse,
    OrderDetailResponse,
    OrderListResponse,
)
from trading.domain.exceptions import (
    OrderNotFoundException,
    InvalidOrderOperationException,
    OrderValidationException,
    InvalidPriceException,
    InvalidQuantityException,
    UnauthorizedOrderAccessException,
    TradingDomainException
)

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=201)
def place_order(
    request:  PlaceOrderRequest,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        if request.user_id != current_user["username"]:
            raise HTTPException(status_code=403, detail="Cannot place order for another user")
        
        use_case = PlaceOrderUseCase(db)
        result = use_case.execute(request)
        db.commit()  # ✅ TAMBAHKAN commit di sini
        return result
    
    except (InvalidPriceException, InvalidQuantityException, OrderValidationException) as e:
        db.rollback()  # ✅ TAMBAHKAN rollback jika error
        raise HTTPException(status_code=400, detail=str(e))
    
    except TradingDomainException as e:
        db. rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: str,
    user_id: str = Query(... ),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        if user_id != current_user["username"]:
            raise HTTPException(status_code=403, detail="Cannot access another user's order")
        
        use_case = GetOrderUseCase(db)
        return use_case.execute(order_id, user_id)
    
    except OrderNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    except UnauthorizedOrderAccessException as e: 
        raise HTTPException(status_code=403, detail=str(e))
    
    except TradingDomainException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=OrderListResponse)
def list_orders(
    user_id: str = Query(...),
    symbol: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        if user_id != current_user["username"]: 
            raise HTTPException(status_code=403, detail="Cannot access another user's orders")
        
        use_case = ListOrdersUseCase(db)
        return use_case.execute(user_id, symbol)
    
    except TradingDomainException as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{order_id}", response_model=OrderResponse)
def cancel_order(
    order_id: str,
    user_id: str = Query(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    try:
        if user_id != current_user["username"]:
            raise HTTPException(status_code=403, detail="Cannot cancel another user's order")
        
        request = CancelOrderRequest(order_id=order_id, user_id=user_id)
        use_case = CancelOrderUseCase(db)
        result = use_case.execute(request)
        db.commit()  # ✅ TAMBAHKAN commit di sini
        return result
    
    except OrderNotFoundException as e:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(e))
    
    except UnauthorizedOrderAccessException as e:
        db.rollback()
        raise HTTPException(status_code=403, detail=str(e))
    
    except InvalidOrderOperationException as e: 
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    
    except TradingDomainException as e: 
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))