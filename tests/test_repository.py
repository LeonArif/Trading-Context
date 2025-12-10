"""Comprehensive tests for repository"""

from decimal import Decimal
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base
from trading.infrastructure.repository import OrderRepository
from trading.infrastructure import models  # Import to register models
from trading.domain.order import Order
from trading.domain.value_objects import OrderSide, OrderType, OrderStatus
from trading.domain.exceptions import OrderNotFoundException


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
def order_repo(db_session):
    """Create an OrderRepository instance"""
    return OrderRepository(db_session)


@pytest.fixture
def sample_order():
    """Create a sample order for testing"""
    return Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )


# ============= Save Tests =============
def test_repository_save_order(order_repo, db_session, sample_order):
    order_repo.save(sample_order)
    db_session.commit()

    # Verify it was saved
    saved_order = order_repo.find_by_id(sample_order.order_id)
    assert saved_order.order_id == sample_order.order_id
    assert saved_order.user_id == sample_order.user_id


def test_repository_save_updates_existing_order(order_repo, db_session, sample_order):
    # Save initial order
    order_repo.save(sample_order)
    db_session.commit()

    # Update and save again
    sample_order.open()
    order_repo.save(sample_order)
    db_session.commit()

    # Verify update
    saved_order = order_repo.find_by_id(sample_order.order_id)
    assert saved_order.status == OrderStatus.OPEN


# ============= Find by ID Tests =============
def test_repository_find_by_id(order_repo, db_session, sample_order):
    order_repo.save(sample_order)
    db_session.commit()

    found_order = order_repo.find_by_id(sample_order.order_id)

    assert found_order.order_id == sample_order.order_id
    assert found_order.user_id == sample_order.user_id
    assert found_order.trading_pair.symbol == "BTC/USDT"
    assert found_order.side == OrderSide.BUY
    assert found_order.price.amount == Decimal("50000")
    assert found_order.quantity == Decimal("1")


def test_repository_find_by_id_not_found(order_repo):
    with pytest.raises(OrderNotFoundException, match="INVALID-ID"):
        order_repo.find_by_id("INVALID-ID")


# ============= Find by User ID Tests =============
def test_repository_find_by_user_id_single(order_repo, db_session, sample_order):
    order_repo.save(sample_order)
    db_session.commit()

    orders = order_repo.find_by_user_id("user123")

    assert len(orders) == 1
    assert orders[0].order_id == sample_order.order_id


def test_repository_find_by_user_id_multiple(order_repo, db_session):
    # Create multiple orders for same user
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )
    order2 = Order.place_limit_order(
        user_id="user123",
        symbol="ETH/USDT",
        side=OrderSide.SELL,
        price=Decimal("3000"),
        quantity=Decimal("2"),
    )

    order_repo.save(order1)
    order_repo.save(order2)
    db_session.commit()

    orders = order_repo.find_by_user_id("user123")

    assert len(orders) == 2
    order_ids = [o.order_id for o in orders]
    assert order1.order_id in order_ids
    assert order2.order_id in order_ids


def test_repository_find_by_user_id_empty(order_repo, db_session, sample_order):
    order_repo.save(sample_order)
    db_session.commit()

    orders = order_repo.find_by_user_id("nonexistent_user")

    assert len(orders) == 0


def test_repository_find_by_user_id_ordered_by_created_at(order_repo, db_session):
    # Create orders with slight delay
    import time

    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )
    order_repo.save(order1)
    db_session.commit()

    time.sleep(0.01)

    order2 = Order.place_limit_order(
        user_id="user123",
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        price=Decimal("3000"),
        quantity=Decimal("1"),
    )
    order_repo.save(order2)
    db_session.commit()

    orders = order_repo.find_by_user_id("user123")

    # Should be in descending order (newest first)
    assert orders[0].order_id == order2.order_id
    assert orders[1].order_id == order1.order_id


# ============= Find by Symbol Tests =============
def test_repository_find_by_symbol(order_repo, db_session):
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )
    order2 = Order.place_limit_order(
        user_id="user456",
        symbol="BTC/USDT",
        side=OrderSide.SELL,
        price=Decimal("51000"),
        quantity=Decimal("0.5"),
    )
    order3 = Order.place_limit_order(
        user_id="user123",
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        price=Decimal("3000"),
        quantity=Decimal("2"),
    )

    order_repo.save(order1)
    order_repo.save(order2)
    order_repo.save(order3)
    db_session.commit()

    btc_orders = order_repo.find_by_symbol("BTC/USDT")

    assert len(btc_orders) == 2
    order_ids = [o.order_id for o in btc_orders]
    assert order1.order_id in order_ids
    assert order2.order_id in order_ids


def test_repository_find_by_symbol_empty(order_repo, db_session, sample_order):
    order_repo.save(sample_order)
    db_session.commit()

    orders = order_repo.find_by_symbol("ETH/BTC")

    assert len(orders) == 0


# ============= Find Open Orders Tests =============
def test_repository_find_open_orders_all(order_repo, db_session):
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )
    order1.open()

    order2 = Order.place_limit_order(
        user_id="user456",
        symbol="BTC/USDT",
        side=OrderSide.SELL,
        price=Decimal("51000"),
        quantity=Decimal("2"),
    )
    order2.open()
    order2.fill(Decimal("1"))  # Partially filled

    order3 = Order.place_limit_order(
        user_id="user789",
        symbol="ETH/USDT",
        side=OrderSide.BUY,
        price=Decimal("3000"),
        quantity=Decimal("1"),
    )
    order3.open()
    order3.fill(Decimal("1"))  # Fully filled

    order_repo.save(order1)
    order_repo.save(order2)
    order_repo.save(order3)
    db_session.commit()

    open_orders = order_repo.find_open_orders()

    assert len(open_orders) == 2
    order_ids = [o.order_id for o in open_orders]
    assert order1.order_id in order_ids
    assert order2.order_id in order_ids


def test_repository_find_open_orders_by_user(order_repo, db_session):
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )
    order1.open()

    order2 = Order.place_limit_order(
        user_id="user456",
        symbol="BTC/USDT",
        side=OrderSide.SELL,
        price=Decimal("51000"),
        quantity=Decimal("1"),
    )
    order2.open()

    order_repo.save(order1)
    order_repo.save(order2)
    db_session.commit()

    open_orders = order_repo.find_open_orders(user_id="user123")

    assert len(open_orders) == 1
    assert open_orders[0].order_id == order1.order_id


# ============= Find by Status Tests =============
def test_repository_find_by_status(order_repo, db_session):
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )
    order1.open()

    order2 = Order.place_limit_order(
        user_id="user123",
        symbol="ETH/USDT",
        side=OrderSide.SELL,
        price=Decimal("3000"),
        quantity=Decimal("1"),
    )
    order2.open()
    order2.cancel()

    order_repo.save(order1)
    order_repo.save(order2)
    db_session.commit()

    open_orders = order_repo.find_by_status(OrderStatus.OPEN)
    cancelled_orders = order_repo.find_by_status(OrderStatus.CANCELLED)

    assert len(open_orders) == 1
    assert open_orders[0].order_id == order1.order_id

    assert len(cancelled_orders) == 1
    assert cancelled_orders[0].order_id == order2.order_id


def test_repository_find_by_status_with_user_filter(order_repo, db_session):
    order1 = Order.place_limit_order(
        user_id="user123",
        symbol="BTC/USDT",
        side=OrderSide.BUY,
        price=Decimal("50000"),
        quantity=Decimal("1"),
    )
    order1.open()

    order2 = Order.place_limit_order(
        user_id="user456",
        symbol="BTC/USDT",
        side=OrderSide.SELL,
        price=Decimal("51000"),
        quantity=Decimal("1"),
    )
    order2.open()

    order_repo.save(order1)
    order_repo.save(order2)
    db_session.commit()

    orders = order_repo.find_by_status(OrderStatus.OPEN, user_id="user123")

    assert len(orders) == 1
    assert orders[0].order_id == order1.order_id


# ============= Delete Tests =============
def test_repository_delete(order_repo, db_session, sample_order):
    order_repo.save(sample_order)
    db_session.commit()

    # Verify it exists
    found = order_repo.find_by_id(sample_order.order_id)
    assert found is not None

    # Delete it
    order_repo.delete(sample_order.order_id)
    db_session.commit()

    # Verify it's gone
    with pytest.raises(OrderNotFoundException):
        order_repo.find_by_id(sample_order.order_id)


def test_repository_delete_nonexistent(order_repo, db_session):
    # Should not raise an error
    order_repo.delete("NONEXISTENT-ID")
    db_session.commit()


# ============= Domain to Model Conversion Tests =============
def test_repository_domain_to_model_conversion(order_repo, sample_order):
    model = order_repo._domain_to_model(sample_order)

    assert model.order_id == sample_order.order_id
    assert model.user_id == sample_order.user_id
    assert model.symbol == sample_order.trading_pair.symbol
    assert model.price == sample_order.price.amount
    assert model.quantity == sample_order.quantity


def test_repository_model_to_domain_conversion(order_repo, db_session, sample_order):
    order_repo.save(sample_order)
    db_session.commit()

    # Retrieve and convert
    domain_order = order_repo.find_by_id(sample_order.order_id)

    assert domain_order.order_id == sample_order.order_id
    assert domain_order.user_id == sample_order.user_id
    assert domain_order.trading_pair.symbol == sample_order.trading_pair.symbol
    assert domain_order.price.amount == sample_order.price.amount
    assert domain_order.quantity == sample_order.quantity
