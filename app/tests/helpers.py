def register_and_login(client, email="user@teste.com", senha="123456", nome="User Teste"):
    client.post("/auth/register", json={"nome": nome, "email": email, "senha": senha})
    response = client.post("/auth/login", data={"username": email, "password": senha})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def make_admin(db_session, email):
    from app.models.user import User, RoleEnum
    user = db_session.query(User).filter(User.email == email).first()
    user.role = RoleEnum.admin
    db_session.commit()