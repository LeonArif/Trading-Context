"""Comprehensive tests for ListOrdersUseCase"""
from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from trading.infrastructure.repository import OrderRepository
from trading.infrastructure import models  # Import to register models
from trading.application.list_orders import ListOrdersUseCase
from trading.domain.order import Order
from trading.domain.value_objects import OrderSide


# Setup test database
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def list_orders_use_case(db_session):
    """Create a ListOrdersUseCase instance"""
    return ListOrdersUseCase(db_session)


@pytest.fixture
def order_repo(db_session):
    """Create an OrderRepository instance"""
    return OrderRepository(db_session)


# ============= List Orders Tests =============
def test_list_orders_empty(list_orders_use_case):
    """Test listing orders when user has no orders"""
    result = list_orders_use_case.execute("user123")
    
    assert result.total == 0
    assert result.orders == []


def test_list_orders_single_order(list_orders_use_case, order_repo, db_session):
    """Test listing a single order"""
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order_repo.save(order)
    db_session.commit()
    
    result = list_orders_use_case.execute("user123")
    
    assert result.total == 1
    assert len(result.orders) == 1
    assert result.orders[0].order_id == order.order_id
    assert result.orders[0].user_id == "user123"
    assert result.orders[0].symbol == "BTC/USDT"


def test_list_orders_multiple_orders(list_orders_use_case, order_repo, db_session):
    """Test listing multiple orders for a user"""
    orders = []
    for i in range(3):
        order = Order.place_limit_order(
            user_id="user123",
            symbol="BTC/USDT",
            side=OrderSide.BUY,
            price=Decimal(str(50000 + i * 100)),
            quantity=Decimal("1")
        )
        order_repo.save(order)
        orders.append(order)
    
    db_session.commit()
    
    result = list_orders_use_case.execute("user123")
    
    assert result.total == 3
    assert len(result.orders) == 3


def test_list_orders_filters_by_user(list_orders_use_case, order_repo, db_session):
    """Test that only orders for specified user are returned"""
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order2 = Order.place_limit_order(
        user_id="user456",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    order_repo.save(order1)
    order_repo.save(order2)
    db_session.commit()
    
    result = list_orders_use_case.execute("user123")
    
    assert result.total == 1
    assert result.orders[0].user_id == "user123"


def test_list_orders_with_symbol_filter(list_orders_use_case, order_repo, db_session):
    """Test listing orders filtered by symbol"""
    btc_order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    eth_order = Order.place_limit_order(
        user_id="user123",
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        price=Decimal("3000"),
        quantity=Decimal("2")
    )
    
    order_repo.save(btc_order)
    order_repo.save(eth_order)
    db_session.commit()
    
    result = list_orders_use_case.execute("user123", symbol="BTC/USDT")
    
    assert result.total == 1
    assert result.orders[0].symbol == "BTC/USDT"


def test_list_orders_with_symbol_filter_no_match(list_orders_use_case, order_repo, db_session):
    """Test listing orders with symbol filter that doesn't match"""
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order_repo.save(order)
    db_session.commit()
    
    result = list_orders_use_case.execute("user123", symbol="ETH/USDT")
    
    assert result.total == 0
    assert result.orders == []


def test_list_orders_without_symbol_filter(list_orders_use_case, order_repo, db_session):
    """Test listing all orders for user without symbol filter"""
    btc_order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    eth_order = Order.place_limit_order(
        user_id="user123",
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        price=Decimal("3000"),
        quantity=Decimal("2")
    )
    
    order_repo.save(btc_order)
    order_repo.save(eth_order)
    db_session.commit()
    
    result = list_orders_use_case.execute("user123")
    
    assert result.total == 2


def test_list_orders_response_format(list_orders_use_case, order_repo, db_session):
    """Test that response contains all required fields"""
    order = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    order_repo.save(order)
    db_session.commit()
    
    result = list_orders_use_case.execute("user123")
    
    assert hasattr(result, 'total')
    assert hasattr(result, 'orders')
    
    order_response = result.orders[0]
    assert hasattr(order_response, 'order_id')
    assert hasattr(order_response, 'user_id')
    assert hasattr(order_response, 'symbol')
    assert hasattr(order_response, 'side')
    assert hasattr(order_response, 'order_type')
    assert hasattr(order_response, 'price')
    assert hasattr(order_response, 'quantity')
    assert hasattr(order_response, 'filled_quantity')
    assert hasattr(order_response, 'status')
    assert hasattr(order_response, 'created_at')
    assert hasattr(order_response, 'updated_at')


def test_list_orders_various_statuses(list_orders_use_case, order_repo, db_session):
    """Test listing orders with various statuses"""
    # Pending order
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1")
    )
    
    # Open order
    order2 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("51000"),
        quantity=Decimal("1")
    )
    order2.open()
    
    # Cancelled order
    order3 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("52000"),
        quantity=Decimal("1")
    )
    order3.open()
    order3.cancel()
    
    order_repo.save(order1)
    order_repo.save(order2)
    order_repo.save(order3)
    db_session.commit()
    
    result = list_orders_use_case.execute("user123")
    
    assert result.total == 3
    statuses = [o.status for o in result.orders]
    assert "PENDING" in statuses
    assert "OPEN" in statuses
    assert "CANCELLED" in statuses
