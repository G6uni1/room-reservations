from datetime import datetime, timedelta
from app.tests.helpers import register_and_login, make_admin


def _create_resource(client, admin_headers):
    response = client.post("/resources/", json={
        "nome": "Sala A", "capacidade": 4, "descricao": "Sala de estudo",
    }, headers=admin_headers)
    return response.json()["id"]


def test_create_reservation_success(client, db_session):
    admin_headers = register_and_login(client, email="admin@teste.com")
    make_admin(db_session, "admin@teste.com")
    resource_id = _create_resource(client, admin_headers)

    user_headers = register_and_login(client, email="cliente@teste.com")
    inicio = datetime(2026, 7, 10, 14, 0)
    fim = datetime(2026, 7, 10, 16, 0)

    response = client.post("/reservations/", json={
        "resource_id": resource_id,
        "data_inicio": inicio.isoformat(),
        "data_fim": fim.isoformat(),
    }, headers=user_headers)

    assert response.status_code == 201
    assert response.json()["status"] == "confirmada"


def test_create_reservation_conflict_returns_409(client, db_session):
    admin_headers = register_and_login(client, email="admin2@teste.com")
    make_admin(db_session, "admin2@teste.com")
    resource_id = _create_resource(client, admin_headers)

    user_headers = register_and_login(client, email="cliente2@teste.com")
    payload = {
        "resource_id": resource_id,
        "data_inicio": "2026-07-10T14:00:00",
        "data_fim": "2026-07-10T16:00:00",
    }

    first = client.post("/reservations/", json=payload, headers=user_headers)
    assert first.status_code == 201

    # mesmo horário, deve conflitar
    second = client.post("/reservations/", json=payload, headers=user_headers)
    assert second.status_code == 409


def test_create_reservation_partial_overlap_returns_409(client, db_session):
    admin_headers = register_and_login(client, email="admin3@teste.com")
    make_admin(db_session, "admin3@teste.com")
    resource_id = _create_resource(client, admin_headers)

    user_headers = register_and_login(client, email="cliente3@teste.com")
    client.post("/reservations/", json={
        "resource_id": resource_id,
        "data_inicio": "2026-07-10T14:00:00",
        "data_fim": "2026-07-10T16:00:00",
    }, headers=user_headers)

    # começa dentro do intervalo já reservado
    response = client.post("/reservations/", json={
        "resource_id": resource_id,
        "data_inicio": "2026-07-10T15:00:00",
        "data_fim": "2026-07-10T17:00:00",
    }, headers=user_headers)
    assert response.status_code == 409


def test_adjacent_reservation_does_not_conflict(client, db_session):
    admin_headers = register_and_login(client, email="admin4@teste.com")
    make_admin(db_session, "admin4@teste.com")
    resource_id = _create_resource(client, admin_headers)

    user_headers = register_and_login(client, email="cliente4@teste.com")
    client.post("/reservations/", json={
        "resource_id": resource_id,
        "data_inicio": "2026-07-10T14:00:00",
        "data_fim": "2026-07-10T16:00:00",
    }, headers=user_headers)

    # começa exatamente onde a anterior termina — não deve conflitar
    response = client.post("/reservations/", json={
        "resource_id": resource_id,
        "data_inicio": "2026-07-10T16:00:00",
        "data_fim": "2026-07-10T18:00:00",
    }, headers=user_headers)
    assert response.status_code == 201


def test_cancel_reservation_success(client, db_session):
    admin_headers = register_and_login(client, email="admin5@teste.com")
    make_admin(db_session, "admin5@teste.com")
    resource_id = _create_resource(client, admin_headers)

    user_headers = register_and_login(client, email="cliente5@teste.com")
    created = client.post("/reservations/", json={
        "resource_id": resource_id,
        "data_inicio": "2026-07-10T14:00:00",
        "data_fim": "2026-07-10T16:00:00",
    }, headers=user_headers)
    reservation_id = created.json()["id"]

    response = client.patch(f"/reservations/{reservation_id}/cancel", headers=user_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelada"


def test_cancel_other_user_reservation_forbidden(client, db_session):
    admin_headers = register_and_login(client, email="admin6@teste.com")
    make_admin(db_session, "admin6@teste.com")
    resource_id = _create_resource(client, admin_headers)

    owner_headers = register_and_login(client, email="dono@teste.com")
    created = client.post("/reservations/", json={
        "resource_id": resource_id,
        "data_inicio": "2026-07-10T14:00:00",
        "data_fim": "2026-07-10T16:00:00",
    }, headers=owner_headers)
    reservation_id = created.json()["id"]

    other_headers = register_and_login(client, email="outro@teste.com")
    response = client.patch(f"/reservations/{reservation_id}/cancel", headers=other_headers)
    assert response.status_code == 403