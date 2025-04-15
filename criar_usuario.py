# criar_usuario.py

from app import app, db
from app import Usuario
from getpass import getpass
from werkzeug.security import generate_password_hash

def criar_usuario():
    print("== Criar novo usuário ==")
    nome = input("Nome completo: ")
    username = input("Nome de usuário (login): ")
    email = input("Email: ")
    senha = getpass("Senha: ")

    with app.app_context():
        if Usuario.query.filter_by(username=username).first():
            print("Já existe um usuário com esse nome de usuário.")
            return

        novo = Usuario(
            nome=nome,
            username=username,
            email=email,
            senha_hash=generate_password_hash(senha),
            ativo=True
        )

        db.session.add(novo)
        db.session.commit()
        print(f"Usuário '{nome}' (login: {username}) criado com sucesso.")

if __name__ == '__main__':
    criar_usuario()
