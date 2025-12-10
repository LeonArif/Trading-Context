# Trading Platform API - DDD Implementation

RESTful API untuk trading platform dengan arsitektur Domain-Driven Design (DDD).

---

## Tech Stack

- Python 3.11+
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Uvicorn

---

## Architecture

```
Trading-Context/
│
├── . github/
│   └── workflows/
│       └── ci. yml                    
│
├── trading/                          
│   ├── __init__.py                    
│   │
│   ├── domain/                     
│   │   ├── __init__.py
│   │   ├── exceptions. py              
│   │   ├── order. py                   
│   │   └── value_objects.py           
│   │
│   ├── infrastructure/                 
│   │   ├── __init__.py
│   │   ├── models. py               
│   │   └── repository.py               
│   │
│   ├── application/                    
│   │   ├── __init__.py
│   │   ├── dto. py                 
│   │   ├── place_order.py            
│   │   ├── cancel_order.py             
│   │   ├── get_order.py                
│   │   └── list_orders.py              
│   │
│   └── api/                          
│       ├── __init__.py
│       ├── auth.py                     
│       ├── auth_routes.py             
│       └── routes.py                   
│
├── tests/                              
│   ├── __init__.py
│   ├── conftest.py                     
│   ├── test_auth.py                    
│   ├── test_domain.py                  
│   ├── test_exceptions.py              
│   ├── test_list_orders_use_case.py   
│   ├── test_order_domain.py            
│   ├── test_orders. py                  
│   ├── test_repository.py             
│   ├── test_routes_extended.py         
│   └── test_value_objects.py           
│
├── __pycache__/                        
│
├── .coverage                           
├── .gitignore                          
├── Dockerfile     
├── .dockerignore       
├── database.py                         
├── main.py                            
├── pytest.ini                         
├── README.md                          
├── requirements.txt                    
├── test. py                            
└── trading. db   


```

---

## DDD Principles

- Aggregate Root: Order
- Value Objects: Money, TradingPair, Enums
- Repository Pattern: OrderRepository
- Application Layer: Use Cases
- Domain Exceptions: Custom error hierarchy
- Clean Architecture: Separation by concern

---

## Install & Run

1. **Clone repo**  
   ```bash
   git clone https://github.com/LeonArif/trading-platform-api.git
   cd trading-platform-api
   ```

2. **Virtual environment**  
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Run server**  
   ```bash
   uvicorn main:app --reload
   ```

5. **Swagger Docs**  
   http://localhost:8000/docs

---

## API Endpoints (Examples)

### Place Order

`POST /api/orders/`
```json
{
  "user_id": "user123",
  "symbol": "BTC/USDT",
  "side": "BUY",
  "order_type": "LIMIT",
  "price": 65000,
  "quantity": 0.5
}
```

Response:
```json
{
  "order_id": "ORD-XXXXXXXXXXXX",
  "user_id": "user123",
  "symbol": "BTC/USDT",
  "side": "BUY",
  "order_type": "LIMIT",
  "price": 65000,
  "quantity": 0.5,
  "filled_quantity": 0,
  "status": "OPEN",
  "created_at": "...",
  "updated_at": "..."
}
```

---

### Get Order Detail

`GET /api/orders/{order_id}?user_id=user123`

---

### List User Orders

`GET /api/orders/?user_id=user123`

---

### Cancel Order

`DELETE /api/orders/{order_id}?user_id=user123`

---

### Place MARKET Order
`POST /api/orders/`
```json
{
  "user_id": "user123",
  "symbol": "ETH/USDT",
  "side": "SELL",
  "order_type": "MARKET",
  "quantity": 2
}
```

---

## Error Response Example

```json
{
  "detail": "Invalid price 0: Price must be greater than 0"
}
```

---

## Order Status Lifecycle

```
PENDING → OPEN → PARTIAL_FILLED → FILLED
              ↘ CANCELLED
              ↘ REJECTED
```

## Fitur

- Place LIMIT & MARKET order
- Lihat detail order
- List order by user (and by symbol)
- Cancel order
- Validasi bisnis order
- Clean architecture & repository
- Exception handling

---

## Not Implemented

- Order matching engine & real trading
- Trade history
- Balance/wallet management
- Auth (JWT)
- Orderbook, real-time update

---


**MIT License**
