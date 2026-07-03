def test_register_success(client):
    response = client.post("/auth/register", json={
        "nome": "Novo Usuário",
        "email": "novo@teste.com",
        "senha": "123456",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "novo@teste.com"
    assert "senha_hash" not in data  # nunca deve vazar o hash


def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "nome": "A", "email": "dup@teste.com", "senha": "123456",
    })
    response = client.post("/auth/register", json={
        "nome": "B", "email": "dup@teste.com", "senha": "outrasenha",
    })
    assert response.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={
        "nome": "Login Teste", "email": "login@teste.com", "senha": "123456",
    })
    response = client.post("/auth/login", data={
        "username": "login@teste.com", "password": "123456",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "nome": "Login Teste", "email": "login2@teste.com", "senha": "123456",
    })
    response = client.post("/auth/login", data={
        "username": "login2@teste.com", "password": "senhaerrada",
    })
    assert response.status_code == 401