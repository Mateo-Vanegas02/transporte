from fastapi.testclient import TestClient


def _create_conductor(client: TestClient, licencia: str = "C-TEST") -> int:
    res = client.post(
        "/api/v1/conductores",
        json={"nombre": "Conductor Base", "licencia": licencia, "telefono": "123"},
    )
    assert res.status_code == 201
    return res.json()["id_conductor"]


def test_create_vehiculo_success(client: TestClient) -> None:
    id_cond = _create_conductor(client, "C-VEH-1")
    payload = {
        "placa": "AAA111",
        "modelo": "Toyota Hilux",
        "id_conductor": id_cond,
    }
    response = client.post("/api/v1/vehiculos", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id_vehiculo"] is not None
    assert data["placa"] == "AAA111"
    assert data["id_conductor"] == id_cond


def test_create_vehiculo_non_existent_conductor_returns_404(
    client: TestClient,
) -> None:
    payload = {
        "placa": "NOEXIST",
        "modelo": "Moto",
        "id_conductor": 99999,
    }
    response = client.post("/api/v1/vehiculos", json=payload)
    assert response.status_code == 404
    assert "no fue encontrado" in response.json()["detail"]


def test_create_vehiculo_duplicate_placa_returns_409(
    client: TestClient,
) -> None:
    id_cond = _create_conductor(client, "C-PLACA-DUP")
    client.post(
        "/api/v1/vehiculos",
        json={
            "placa": "DUP999",
            "modelo": "Mazda 3",
            "id_conductor": id_cond,
        },
    )

    res2 = client.post(
        "/api/v1/vehiculos",
        json={
            "placa": "DUP999",
            "modelo": "Kia Picanto",
            "id_conductor": id_cond,
        },
    )
    assert res2.status_code == 409
    assert "ya se encuentra registrada" in res2.json()["detail"]


def test_get_vehiculo_by_id_and_not_found(client: TestClient) -> None:
    id_cond = _create_conductor(client, "C-GET-VEH")
    v_res = client.post(
        "/api/v1/vehiculos",
        json={"placa": "GET123", "modelo": "Nissan", "id_conductor": id_cond},
    )
    id_veh = v_res.json()["id_vehiculo"]

    res = client.get(f"/api/v1/vehiculos/{id_veh}")
    assert res.status_code == 200
    assert res.json()["placa"] == "GET123"

    res_404 = client.get("/api/v1/vehiculos/99999")
    assert res_404.status_code == 404


def test_update_vehiculo_put_patch_and_rejections(client: TestClient) -> None:
    id_cond = _create_conductor(client, "C-UPD-VEH")
    v_res = client.post(
        "/api/v1/vehiculos",
        json={"placa": "UPD001", "modelo": "Viejo", "id_conductor": id_cond},
    )
    id_veh = v_res.json()["id_vehiculo"]

    # PATCH modelo
    patch_res = client.patch(
        f"/api/v1/vehiculos/{id_veh}",
        json={"modelo": "Nuevo Modelo"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["modelo"] == "Nuevo Modelo"

    # Rechazo de null
    null_res = client.patch(
        f"/api/v1/vehiculos/{id_veh}",
        json={"placa": None},
    )
    assert null_res.status_code == 422

    # PUT con conductor inexistente -> 404
    bad_cond_res = client.put(
        f"/api/v1/vehiculos/{id_veh}",
        json={
            "placa": "UPD001",
            "modelo": "Nuevo Modelo",
            "id_conductor": 99999,
        },
    )
    assert bad_cond_res.status_code == 404


def test_delete_vehiculo_success_and_blocked_by_viajes(
    client: TestClient,
) -> None:
    id_cond = _create_conductor(client, "C-DEL-VEH")
    v_res = client.post(
        "/api/v1/vehiculos",
        json={"placa": "DEL001", "modelo": "Sedan", "id_conductor": id_cond},
    )
    id_veh = v_res.json()["id_vehiculo"]

    # Registrar un viaje para el vehículo
    client.post(
        "/api/v1/viajes",
        json={
            "destino": "Aeropuerto",
            "fecha": "2026-10-15",
            "id_vehiculo": id_veh,
        },
    )

    # Intento de borrado bloqueado -> 409
    del_res = client.delete(f"/api/v1/vehiculos/{id_veh}")
    assert del_res.status_code == 409
    assert "tiene viajes asociados" in del_res.json()["detail"]


def test_get_viajes_de_vehiculo(client: TestClient) -> None:
    id_cond = _create_conductor(client, "C-VIAJES-VEH")
    v_res = client.post(
        "/api/v1/vehiculos",
        json={"placa": "VIA001", "modelo": "Van", "id_conductor": id_cond},
    )
    id_veh = v_res.json()["id_vehiculo"]

    client.post(
        "/api/v1/viajes",
        json={
            "destino": "Terminal Norte",
            "fecha": "2026-10-11",
            "id_vehiculo": id_veh,
        },
    )
    client.post(
        "/api/v1/viajes",
        json={
            "destino": "Terminal Sur",
            "fecha": "2026-10-12",
            "id_vehiculo": id_veh,
        },
    )

    res = client.get(f"/api/v1/vehiculos/{id_veh}/viajes")
    assert res.status_code == 200
    viajes = res.json()
    assert len(viajes) == 2
