from fastapi.testclient import TestClient


def _setup_vehiculo_and_conductor(client: TestClient) -> int:
    c = client.post(
        "/api/v1/conductores",
        json={
            "nombre": "Carlos Arango",
            "licencia": "C-VIAJE-SETUP",
            "telefono": "3001122334",
        },
    )
    id_cond = c.json()["id_conductor"]

    v = client.post(
        "/api/v1/vehiculos",
        json={
            "placa": "MED001",
            "modelo": "Renault Duster",
            "id_conductor": id_cond,
        },
    )
    return v.json()["id_vehiculo"]


def test_create_viaje_success(client: TestClient) -> None:
    id_veh = _setup_vehiculo_and_conductor(client)
    payload = {
        "destino": "Aeropuerto José María Córdova",
        "fecha": "2026-10-20",
        "id_vehiculo": id_veh,
    }
    response = client.post("/api/v1/viajes", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id_viaje"] is not None
    assert data["destino"] == payload["destino"]
    assert data["fecha"] == "2026-10-20"


def test_create_viaje_non_existent_vehiculo_returns_404(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/viajes",
        json={
            "destino": "Estadio Atanasio Girardot",
            "fecha": "2026-10-20",
            "id_vehiculo": 99999,
        },
    )
    assert response.status_code == 404
    assert "no fue encontrado" in response.json()["detail"]


def test_list_viajes_with_filters(client: TestClient) -> None:
    id_veh = _setup_vehiculo_and_conductor(client)

    client.post(
        "/api/v1/viajes",
        json={
            "destino": "Parque Arví",
            "fecha": "2026-10-10",
            "id_vehiculo": id_veh,
        },
    )
    client.post(
        "/api/v1/viajes",
        json={
            "destino": "El Tesoro",
            "fecha": "2026-10-15",
            "id_vehiculo": id_veh,
        },
    )
    client.post(
        "/api/v1/viajes",
        json={
            "destino": "Plaza Mayor",
            "fecha": "2026-10-25",
            "id_vehiculo": id_veh,
        },
    )

    # Filtro por destino parcial
    res_dest = client.get("/api/v1/viajes?destino=Parque")
    assert res_dest.status_code == 200
    assert len(res_dest.json()) == 1
    assert "Parque" in res_dest.json()[0]["destino"]

    # Filtro por rango de fechas
    res_fechas = client.get(
        "/api/v1/viajes?fecha_desde=2026-10-12&fecha_hasta=2026-10-20"
    )
    assert res_fechas.status_code == 200
    assert len(res_fechas.json()) == 1
    assert res_fechas.json()[0]["destino"] == "El Tesoro"


def test_get_viajes_detalle_joinedload(client: TestClient) -> None:
    c = client.post(
        "/api/v1/conductores",
        json={
            "nombre": "Ana Restrepo",
            "licencia": "C-DETALLE",
            "telefono": "3119998877",
        },
    )
    id_cond = c.json()["id_conductor"]

    v = client.post(
        "/api/v1/vehiculos",
        json={
            "placa": "DET999",
            "modelo": "Toyota Corolla",
            "id_conductor": id_cond,
        },
    )
    id_veh = v.json()["id_vehiculo"]

    client.post(
        "/api/v1/viajes",
        json={
            "destino": "Universidad de Antioquia",
            "fecha": "2026-10-18",
            "id_vehiculo": id_veh,
        },
    )

    res = client.get("/api/v1/viajes/detalle")
    assert res.status_code == 200
    detalles = res.json()
    assert len(detalles) >= 1

    item = next(d for d in detalles if d["placa"] == "DET999")
    assert item["conductor"] == "Ana Restrepo"
    assert item["destino"] == "Universidad de Antioquia"
    assert item["modelo"] == "Toyota Corolla"
    assert item["fecha"] == "2026-10-18"


def test_update_viaje_and_reject_null(client: TestClient) -> None:
    id_veh = _setup_vehiculo_and_conductor(client)
    res_v = client.post(
        "/api/v1/viajes",
        json={
            "destino": "Terminal del Norte",
            "fecha": "2026-10-11",
            "id_vehiculo": id_veh,
        },
    )
    id_viaje = res_v.json()["id_viaje"]

    # PATCH
    patch_res = client.patch(
        f"/api/v1/viajes/{id_viaje}",
        json={"destino": "Terminal del Sur"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["destino"] == "Terminal del Sur"

    # Rechazo de null
    null_res = client.patch(
        f"/api/v1/viajes/{id_viaje}",
        json={"fecha": None},
    )
    assert null_res.status_code == 422


def test_delete_viaje_success_and_not_found(client: TestClient) -> None:
    id_veh = _setup_vehiculo_and_conductor(client)
    res_v = client.post(
        "/api/v1/viajes",
        json={
            "destino": "Para Borrar",
            "fecha": "2026-10-30",
            "id_vehiculo": id_veh,
        },
    )
    id_viaje = res_v.json()["id_viaje"]

    del_res = client.delete(f"/api/v1/viajes/{id_viaje}")
    assert del_res.status_code == 204

    # 404 al intentar obtenerlo
    get_res = client.get(f"/api/v1/viajes/{id_viaje}")
    assert get_res.status_code == 404


def test_update_viaje_put_and_edge_cases(client: TestClient) -> None:
    id_veh = _setup_vehiculo_and_conductor(client)
    res_v = client.post(
        "/api/v1/viajes",
        json={
            "destino": "Inicial",
            "fecha": "2026-10-01",
            "id_vehiculo": id_veh,
        },
    )
    id_viaje = res_v.json()["id_viaje"]

    # PUT completo
    put_res = client.put(
        f"/api/v1/viajes/{id_viaje}",
        json={
            "destino": "Modificado PUT",
            "fecha": "2026-10-02",
            "id_vehiculo": id_veh,
        },
    )
    assert put_res.status_code == 200
    assert put_res.json()["destino"] == "Modificado PUT"

    # PUT con vehículo inexistente -> 404
    bad_veh = client.put(
        f"/api/v1/viajes/{id_viaje}",
        json={
            "destino": "Dest",
            "fecha": "2026-10-02",
            "id_vehiculo": 99999,
        },
    )
    assert bad_veh.status_code == 404

    # 404 actualizando viaje inexistente
    bad_viaje = client.put(
        "/api/v1/viajes/99999",
        json={
            "destino": "Dest",
            "fecha": "2026-10-02",
            "id_vehiculo": id_veh,
        },
    )
    assert bad_viaje.status_code == 404


def test_list_viajes_filter_by_id_vehiculo(client: TestClient) -> None:
    id_veh = _setup_vehiculo_and_conductor(client)
    client.post(
        "/api/v1/viajes",
        json={
            "destino": "Destino Unico",
            "fecha": "2026-10-15",
            "id_vehiculo": id_veh,
        },
    )
    res = client.get(f"/api/v1/viajes?id_vehiculo={id_veh}")
    assert res.status_code == 200
    assert len(res.json()) >= 1
    assert res.json()[0]["id_vehiculo"] == id_veh
