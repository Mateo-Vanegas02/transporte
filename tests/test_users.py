from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Verifica que el endpoint de salud responda correctamente."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_create_user_success(client: TestClient) -> None:
    """Verifica la creación exitosa de un usuario (201 Created)."""
    payload = {"name": "Carlos Gomez", "email": "carlos@example.com"}
    response = client.post("/users", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]


def test_create_user_duplicate_email_returns_409(client: TestClient) -> None:
    """Verifica que registrar un usuario con un email existente retorne 409 Conflict."""
    payload = {"name": "Carlos Gomez", "email": "duplicado@example.com"}
    response_1 = client.post("/users", json=payload)
    assert response_1.status_code == 201

    # Intento de crear el mismo email
    response_2 = client.post(
        "/users",
        json={"name": "Otro Nombre", "email": "duplicado@example.com"},
    )
    assert response_2.status_code == 409
    assert "ya se encuentra registrado" in response_2.json()["detail"]


def test_get_user_by_id_success(client: TestClient) -> None:
    """Verifica la consulta de un usuario existente por ID (200 OK)."""
    create_res = client.post(
        "/users",
        json={"name": "Maria Lopez", "email": "maria@example.com"},
    )
    user_id = create_res.json()["id"]

    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == "Maria Lopez"
    assert data["email"] == "maria@example.com"


def test_get_user_by_id_not_found_returns_404(client: TestClient) -> None:
    """Verifica que solicitar un ID inexistente devuelva 404 Not Found."""
    response = client.get("/users/99999")
    assert response.status_code == 404
    assert "no fue encontrado" in response.json()["detail"]


def test_list_users(client: TestClient) -> None:
    """Verifica la lista de usuarios y soporte de parámetros skip y limit."""
    # Lista inicial vacía
    initial_res = client.get("/users")
    assert initial_res.status_code == 200
    assert initial_res.json() == []

    # Insertar 3 usuarios
    for i in range(1, 4):
        client.post(
            "/users",
            json={"name": f"User {i}", "email": f"user{i}@example.com"},
        )

    # Listar todos
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 3

    # Probar paginación
    paginated_res = client.get("/users?skip=1&limit=1")
    assert paginated_res.status_code == 200
    paginated_users = paginated_res.json()
    assert len(paginated_users) == 1
    assert paginated_users[0]["name"] == "User 2"


def test_update_user_success(client: TestClient) -> None:
    """Verifica la actualización de campos de un usuario (200 OK)."""
    create_res = client.post(
        "/users",
        json={"name": "Lucia Original", "email": "lucia@example.com"},
    )
    user_id = create_res.json()["id"]

    update_payload = {"name": "Lucia Modificada", "email": "lucia.nueva@example.com"}
    response = client.put(f"/users/{user_id}", json=update_payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == "Lucia Modificada"
    assert data["email"] == "lucia.nueva@example.com"


def test_update_user_not_found_returns_404(client: TestClient) -> None:
    """Verifica que actualizar un usuario inexistente retorne 404."""
    response = client.put(
        "/users/99999",
        json={"name": "Inexistente"},
    )
    assert response.status_code == 404
    assert "no fue encontrado" in response.json()["detail"]


def test_update_user_duplicate_email_returns_409(client: TestClient) -> None:
    """Verifica que actualizar al email de otro usuario existente devuelva 409."""
    user1_res = client.post(
        "/users",
        json={"name": "User Uno", "email": "uno@example.com"},
    )
    assert user1_res.status_code == 201
    user2_res = client.post(
        "/users",
        json={"name": "User Dos", "email": "dos@example.com"},
    )
    assert user2_res.status_code == 201
    user2_id = user2_res.json()["id"]

    # Intentar cambiar email de user2 al de user1
    response = client.put(
        f"/users/{user2_id}",
        json={"email": "uno@example.com"},
    )
    assert response.status_code == 409
    assert "ya se encuentra registrado" in response.json()["detail"]


def test_delete_user_success(client: TestClient) -> None:
    """Verifica la eliminación de un usuario (204 No Content)."""
    create_res = client.post(
        "/users",
        json={"name": "Para Borrar", "email": "borrar@example.com"},
    )
    user_id = create_res.json()["id"]

    # Eliminar
    delete_res = client.delete(f"/users/{user_id}")
    assert delete_res.status_code == 204

    # Verificar que ya no existe
    get_res = client.get(f"/users/{user_id}")
    assert get_res.status_code == 404


def test_delete_user_not_found_returns_404(client: TestClient) -> None:
    """Verifica que eliminar un usuario inexistente retorne 404."""
    response = client.delete("/users/99999")
    assert response.status_code == 404
    assert "no fue encontrado" in response.json()["detail"]


def test_create_user_invalid_email_format(client: TestClient) -> None:
    """Verifica que datos con formato de email inválido fallen con 422 de Pydantic."""
    response = client.post(
        "/users",
        json={"name": "Invalido", "email": "correo-no-valido"},
    )
    assert response.status_code == 422
