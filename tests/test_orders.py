def get_token(client):
    resp = client.post("/api/token", data={"username": "LeonArif", "password": "password123"})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_token_field_required(client):
    resp = client.post("/api/token", json={"username": "LeonArif"})
    assert resp.status_code == 422

def test_token_success(client):
    resp = client.post("/api/token", data={"username": "LeonArif", "password": "password123"})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

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
        "quantity":  0.5
    }
    resp = client.post("/api/orders/", json=payload, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    assert body["user_id"] == "LeonArif"
    assert body["symbol"] == "BTC/USDT"
    assert body["status"] == "OPEN"  # ✅ Fixed

def test_cancel_order(client):
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
    order_id = resp.json()["order_id"]
    
    resp = client.delete(f"/api/orders/{order_id}?user_id=LeonArif", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["status"] == "CANCELLED"

def test_list_orders(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/orders/?user_id=LeonArif", headers=headers)
    assert resp.status_code == 200
    assert "orders" in resp.json()
    assert "total" in resp.json()

def test_get_order(client):
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
    order_id = resp.json()["order_id"]
    
    resp = client.get(f"/api/orders/{order_id}?user_id=LeonArif", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["order_id"] == order_id

def test_get_order_not_found(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/api/orders/INVALID-ID?user_id=LeonArif", headers=headers)  # ✅ Fixed
    assert resp.status_code == 404

def test_cancel_order_wrong_user(client):
    token = get_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "user_id": "LeonArif",
        "symbol":  "BTC/USDT",
        "side": "BUY",
        "order_type": "LIMIT",
        "price": 65000,
        "quantity": 0.5
    }
    resp = client. post("/api/orders/", json=payload, headers=headers)
    order_id = resp.json()["order_id"]
    
    resp = client.delete(f"/api/orders/{order_id}?user_id=OtherUser", headers=headers)
    assert resp.status_code == 403