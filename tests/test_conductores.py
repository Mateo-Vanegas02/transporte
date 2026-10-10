from fastapi.testclient import TestClient


def test_create_conductor_success(client: TestClient) -> None:
    payload = {
        "nombre": "Pedro Ramirez",
        "licencia": "C1-11223344",
        "telefono": "3109876543",
    }
    response = client.post("/api/v1/conductores", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id_conductor"] is not None
    assert data["nombre"] == payload["nombre"]
    assert data["licencia"] == payload["licencia"]


def test_create_conductor_duplicate_licencia_returns_409(
    client: TestClient,
) -> None:
    payload = {
        "nombre": "Pedro Ramirez",
        "licencia": "C1-DUPLICADA",
        "telefono": "3109876543",
    }
    res1 = client.post("/api/v1/conductores", json=payload)
    assert res1.status_code == 201

    res2 = client.post(
        "/api/v1/conductores",
        json={
            "nombre": "Otro Nombre",
            "licencia": "C1-DUPLICADA",
            "telefono": "3000000000",
        },
    )
    assert res2.status_code == 409
    assert "ya se encuentra registrada" in res2.json()["detail"]


def test_get_conductor_by_id_success(client: TestClient) -> None:
    res = client.post(
        "/api/v1/conductores",
        json={
            "nombre": "Laura Gomez",
            "licencia": "C2-99887766",
            "telefono": "3151234567",
        },
    )
    id_conductor = res.json()["id_conductor"]

    get_res = client.get(f"/api/v1/conductores/{id_conductor}")
    assert get_res.status_code == 200
    assert get_res.json()["nombre"] == "Laura Gomez"


def test_get_conductor_not_found_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/conductores/9999")
    assert response.status_code == 404
    assert "no fue encontrado" in response.json()["detail"]


def test_list_conductores_and_pagination(client: TestClient) -> None:
    for i in range(1, 4):
        client.post(
            "/api/v1/conductores",
            json={
                "nombre": f"Conductor {i}",
                "licencia": f"LIC-{i}",
                "telefono": f"300000000{i}",
            },
        )

    res = client.get("/api/v1/conductores?skip=1&limit=1")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Conductor 2"


def test_update_conductor_put_and_patch(client: TestClient) -> None:
    res = client.post(
        "/api/v1/conductores",
        json={
            "nombre": "Original",
            "licencia": "LIC-ORIGINAL",
            "telefono": "3111111111",
        },
    )
    id_cond = res.json()["id_conductor"]

    # PATCH parcial
    patch_res = client.patch(
        f"/api/v1/conductores/{id_cond}",
        json={"telefono": "3222222222"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["telefono"] == "3222222222"
    assert patch_res.json()["nombre"] == "Original"

    # PUT completo
    put_res = client.put(
        f"/api/v1/conductores/{id_cond}",
        json={
            "nombre": "Nombre Actualizado",
            "licencia": "LIC-NUEVA",
            "telefono": "3333333333",
        },
    )
    assert put_res.status_code == 200
    assert put_res.json()["nombre"] == "Nombre Actualizado"
    assert put_res.json()["licencia"] == "LIC-NUEVA"


def test_update_conductor_duplicate_licencia_returns_409(
    client: TestClient,
) -> None:
    client.post(
        "/api/v1/conductores",
        json={"nombre": "C1", "licencia": "L-1", "telefono": "111"},
    )
    c2 = client.post(
        "/api/v1/conductores",
        json={"nombre": "C2", "licencia": "L-2", "telefono": "222"},
    )
    id_c2 = c2.json()["id_conductor"]

    res = client.patch(
        f"/api/v1/conductores/{id_c2}",
        json={"licencia": "L-1"},
    )
    assert res.status_code == 409
    assert "ya se encuentra registrada" in res.json()["detail"]


def test_update_conductor_rejects_null_values(client: TestClient) -> None:
    c = client.post(
        "/api/v1/conductores",
        json={"nombre": "Valido", "licencia": "L-NULL", "telefono": "123"},
    )
    id_cond = c.json()["id_conductor"]

    # Enviar null explícito debe dar 422
    res = client.patch(
        f"/api/v1/conductores/{id_cond}",
        json={"nombre": None},
    )
    assert res.status_code == 422
    assert "no puede ser nulo" in str(res.json())


def test_delete_conductor_success_and_not_found(client: TestClient) -> None:
    c = client.post(
        "/api/v1/conductores",
        json={"nombre": "Borrar", "licencia": "L-BORRAR", "telefono": "999"},
    )
    id_cond = c.json()["id_conductor"]

    del_res = client.delete(f"/api/v1/conductores/{id_cond}")
    assert del_res.status_code == 204

    # 404 al intentar borrar de nuevo
    del_res_again = client.delete(f"/api/v1/conductores/{id_cond}")
    assert del_res_again.status_code == 404


def test_delete_conductor_with_vehiculos_returns_409(
    client: TestClient,
) -> None:
    c = client.post(
        "/api/v1/conductores",
        json={"nombre": "Con Auto", "licencia": "L-AUTO", "telefono": "888"},
    )
    id_cond = c.json()["id_conductor"]

    # Crear vehículo asociado
    client.post(
        "/api/v1/vehiculos",
        json={
            "placa": "AUT123",
            "modelo": "Chevrolet Tracker",
            "id_conductor": id_cond,
        },
    )

    # Intento de borrado bloqueado
    del_res = client.delete(f"/api/v1/conductores/{id_cond}")
    assert del_res.status_code == 409
    assert "tiene vehículos asociados" in del_res.json()["detail"]


def test_get_vehiculos_de_conductor(client: TestClient) -> None:
    c = client.post(
        "/api/v1/conductores",
        json={"nombre": "Flota", "licencia": "L-FLOTA", "telefono": "777"},
    )
    id_cond = c.json()["id_conductor"]

    client.post(
        "/api/v1/vehiculos",
        json={"placa": "FLT001", "modelo": "Van 1", "id_conductor": id_cond},
    )
    client.post(
        "/api/v1/vehiculos",
        json={"placa": "FLT002", "modelo": "Van 2", "id_conductor": id_cond},
    )

    res = client.get(f"/api/v1/conductores/{id_cond}/vehiculos")
    assert res.status_code == 200
    vehiculos = res.json()
    assert len(vehiculos) == 2
    assert vehiculos[0]["placa"] == "FLT001"
