def get_token(client):
    resp = client.post("/api/token", data={"username": "LeonArif", "password": "password123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_place_order_unauthenticated(client):
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.5
    }
    resp = client.post("/api/orders/", json=payload)
    assert resp.status_code == 401

def test_place_order_authenticated(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": "LeonArif",
        "symbol": "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.5
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["user_id"] == "LeonArif"
    assert body["symbol"] == "BTC/USDT"
    assert body["status"] == "OPEN"

def test_cancel_order(client):
    # Create order first
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {... }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    order_id = resp.json()["order_id"]
    
    # Cancel order
    resp = client.delete(f"/api/orders/{order_id}? user_id=LeonArif", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"

def test_list_orders(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/orders/? user_id=LeonArif", headers=headers)
    assert resp.status_code == 200
    assert "orders" in resp.json()