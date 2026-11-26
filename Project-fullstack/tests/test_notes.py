from unittest.mock import patch


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


@patch("app.api.v1.notes.notifyNoteCreated.delay")
def test_create_note(mockDelay, client):
    token = getToken(client)
    resp = client.post(
        "/api/v1/notes",
        json={"title": "Купить молоко", "body": "Не забыть про хлеб"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Купить молоко"
    assert data["body"] == "Не забыть про хлеб"
    assert data["ownerId"] == 1
    mockDelay.assert_called_once()


def test_notes_requires_auth(client):
    resp = client.get("/api/v1/notes")
    assert resp.status_code == 401


@patch("app.api.v1.notes.notifyNoteCreated.delay")
def test_list_only_own_notes(mockDelay, client):
    token = getToken(client, "x@example.com")
    client.post(
        "/api/v1/notes",
        json={"title": "Заметка X", "body": ""},
        headers={"Authorization": f"Bearer {token}"},
    )

    token2 = getToken(client, "y@example.com")
    resp = client.get(
        "/api/v1/notes", headers={"Authorization": f"Bearer {token2}"}
    )
    assert resp.status_code == 200
    assert resp.json() == []