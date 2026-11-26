from app.models.user import User


def getToken(client, email="user@example.com", password="secret123"):
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password},
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return resp.json()["accessToken"]


def test_admin_endpoint_forbidden_for_regular_user(client):
    token = getToken(client, "plain@example.com")
    resp = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Недостаточно прав"


def test_admin_endpoint_allows_admin(client, updateDb):
    token = getToken(client, "admin@example.com")

    def promote(session):
        user = (
            session.query(User)
            .filter(User.email == "admin@example.com")
            .first()
        )
        user.role = "admin"

    updateDb(promote)

    resp = client.get(
        "/api/v1/users", headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 200
    emails = [u["email"] for u in resp.json()]
    assert "admin@example.com" in emails