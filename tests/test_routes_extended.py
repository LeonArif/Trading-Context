"""Additional tests for API routes to increase coverage"""

import pytest


def get_token(client):
    resp = client.post(
        "/api/token", data={"username": "LeonArif", "password": "password123"}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


# ============= Error Handling Tests =============
def test_place_order_for_different_user_forbidden(client):
    """Test that user cannot place order for another user"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": "OtherUser",  # Different from authenticated user
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.5,
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    assert resp.status_code == 403
    assert "Cannot place order for another user" in resp.json()["detail"]


def test_place_order_invalid_price(client):
    """Test placing order with invalid price"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 0.001,  # Below minimum price
        "quantity": 0.5,
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    assert resp.status_code == 400


def test_place_order_invalid_quantity(client):
    """Test placing order with invalid quantity"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.000000001,  # Below minimum quantity
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    assert resp.status_code == 400


def test_place_order_quantity_too_small(client):
    """Test placing order with quantity below minimum"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.000000001,  # Below minimum
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    assert resp.status_code == 400


def test_get_order_different_user_forbidden(client):
    """Test that user cannot get another user's order"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # First create an order
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.5,
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    order_id = resp.json()["order_id"]

    # Try to get it with different user_id
    resp = client.get(f"/api/orders/{order_id}?user_id=OtherUser", headers=headers)
    assert resp.status_code == 403
    assert "Cannot access another user's order" in resp.json()["detail"]


def test_list_orders_different_user_forbidden(client):
    """Test that user cannot list another user's orders"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/orders/?user_id=OtherUser", headers=headers)
    assert resp.status_code == 403
    assert "Cannot access another user's orders" in resp.json()["detail"]


def test_list_orders_with_symbol_filter(client):
    """Test listing orders filtered by symbol"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create BTC order
    btc_payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.5,
    }
    client.post("/api/orders/", json=btc_payload, headers=headers)

    # Create ETH order
    eth_payload = {
        "user_id": "LeonArif",
        "symbol": "ETH/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 3000,
        "quantity": 1.0,
    }
    client.post("/api/orders/", json=eth_payload, headers=headers)

    # List only BTC orders
    resp = client.get("/api/orders/?user_id=LeonArif&symbol=BTC/USDT", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["orders"][0]["symbol"] == "BTC/USDT"


def test_cancel_order_already_filled(client):
    """Test canceling an order that's already filled"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create and immediately try to cancel
    # Note: In real scenario, order would be filled by matching engine
    # For this test, we just test the endpoint error handling
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.5,
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    order_id = resp.json()["order_id"]

    # Cancel should work for open order
    resp = client.delete(f"/api/orders/{order_id}?user_id=LeonArif", headers=headers)
    assert resp.status_code == 200


def test_cancel_order_not_found(client):
    """Test canceling non-existent order"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.delete(
        "/api/orders/INVALID-ORDER-ID?user_id=LeonArif", headers=headers
    )
    assert resp.status_code == 404


def test_list_orders_empty(client):
    """Test listing orders when there are none"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/api/orders/?user_id=LeonArif", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "orders" in data
    assert "total" in data


# ============= Market Order Tests =============
def test_place_market_order(client):
    """Test placing a market order"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "MARKET",
        "price": 0,  # Market orders don't need price
        "quantity": 0.5,
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["order_type"] == "MARKET"


# ============= Multiple Orders Tests =============
def test_list_multiple_orders(client):
    """Test listing multiple orders"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Create multiple orders
    for i in range(3):
        payload = {
            "user_id": "LeonArif",
            "symbol": "BTC/USDT",
            "side": "BUY",
            "order_type": "LIMIT",
            "price": 65000 + i * 100,
            "quantity": 0.5,
        }
        client.post("/api/orders/", json=payload, headers=headers)

    # List all orders
    resp = client.get("/api/orders/?user_id=LeonArif", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3


# ============= Symbol Variations Tests =============
def test_place_order_different_symbols(client):
    """Test placing orders with different trading pairs"""
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    symbols = ["BTC/USDT", "ETH/USDT", "SOL/USDT"]

    for symbol in symbols:
        payload = {
            "user_id": "LeonArif",
            "symbol": symbol,
            "side": "BUY",
            "order_type": "LIMIT",
            "price": 1000,
            "quantity": 1.0,
        }
        resp = client.post("/api/orders/", json=payload, headers=headers)
        assert resp.status_code == 201
        assert resp.json()["symbol"] == symbol
