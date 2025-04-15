# atualizar_senha.py

from getpass import getpass
from app import app, db
from app import Usuario

def atualizar_senha():
    username = input("Digite o nome de usuário (login): ").strip()
    
    with app.app_context():
        usuario = Usuario.query.filter_by(username=username).first()

        if not usuario:
            print("Usuário não encontrado.")
            return

        nova_senha = getpass("Nova senha: ")
        confirmar = getpass("Confirme a nova senha: ")

        if nova_senha != confirmar:
            print("As senhas não coincidem.")
            return

        usuario.set_senha(nova_senha)
        db.session.commit()
        print(f"Senha de '{usuario.nome}' (login: {usuario.username}) atualizada com sucesso.")

if __name__ == '__main__':
    atualizar_senha()
