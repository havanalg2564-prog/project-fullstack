def test_register(client):
    resp = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "secret123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "user"
    assert "id" in data


def test_register_duplicate(client):
    payload = {"email": "bob@example.com", "password": "secret123"}
    client.post("/api/v1/auth/register", json=payload)
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
    assert resp.json()["detail"] == "Email уже зарегистрирован"


def test_login(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "carol@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "carol@example.com", "password": "secret123"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "accessToken" in body
    assert body["tokenType"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "dave@example.com", "password": "secret123"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": "dave@example.com", "password": "wrong"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Неверный email или пароль"


def test_protected_endpoint_requires_token(client):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Требуется авторизация"


def test_protected_endpoint_with_token(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "eve@example.com", "password": "secret123"},
    )
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "eve@example.com", "password": "secret123"},
    )
    token = login.json()["accessToken"]
    resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "eve@example.com"