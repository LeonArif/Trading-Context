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
│       └── ci. yml                      # CI/CD workflow
│
├── trading/                            # Main application package
│   ├── __init__.py                     # Package initializer (kemungkinan kosong)
│   │
│   ├── domain/                         # Domain Layer (Business Logic)
│   │   ├── __init__.py
│   │   ├── exceptions. py               # Custom domain exceptions
│   │   ├── order. py                    # Order aggregate/entity
│   │   └── value_objects.py            # Value objects (Money, TradingPair, Enums)
│   │
│   ├── infrastructure/                 # Infrastructure Layer (Persistence)
│   │   ├── __init__.py
│   │   ├── models. py                   # SQLAlchemy ORM models
│   │   └── repository.py               # Repository pattern implementation
│   │
│   ├── application/                    # Application Layer (Use Cases)
│   │   ├── __init__.py
│   │   ├── dto. py                      # Data Transfer Objects (Pydantic models)
│   │   ├── place_order.py              # Place order use case
│   │   ├── cancel_order.py             # Cancel order use case
│   │   ├── get_order.py                # Get order use case
│   │   └── list_orders.py              # List orders use case
│   │
│   └── api/                            # API Layer (Presentation)
│       ├── __init__.py
│       ├── auth.py                     # Authentication logic (JWT, Argon2)
│       ├── auth_routes.py              # Authentication endpoints (/api/token)
│       └── routes.py                   # Order endpoints (/api/orders/*)
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures & test configuration
│   ├── test_auth.py                    # Authentication tests
│   ├── test_domain.py                  # Domain model tests (basic)
│   ├── test_exceptions.py              # Exception handling tests
│   ├── test_list_orders_use_case.py    # List orders use case tests
│   ├── test_order_domain.py            # Comprehensive order domain tests
│   ├── test_orders. py                  # API integration tests
│   ├── test_repository.py              # Repository tests
│   ├── test_routes_extended.py         # Extended API routes tests
│   └── test_value_objects.py           # Value objects tests
│
├── __pycache__/                        # Python bytecode cache (gitignored)
│
├── .coverage                           # Coverage data file
├── .gitignore                          # Git ignore rules
├── database.py                         # Database configuration & session management
├── main.py                             # FastAPI application entry point
├── pytest.ini                          # Pytest configuration
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── test. py                             # Standalone test script (optional)
└── trading. db                          # SQLite database file (gitignored recommended)

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
