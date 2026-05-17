import os
import sys
import unittest


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

os.environ["AUTO_CREATE_DB"] = "false"
os.environ["DATABASE_URI"] = "sqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret"

from app import app
from database import db
from controllers.usuarios_controller import criar_usuario
from controllers.chamados_controller import criar_chamado


class ChamadosPermissoesTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()
            self.professor = criar_usuario(
                "Professor",
                "professor@example.com",
                "123456",
                "professor",
            )
            self.outro_professor = criar_usuario(
                "Outro Professor",
                "outro@example.com",
                "123456",
                "professor",
            )
            self.admin = criar_usuario(
                "Admin",
                "admin@example.com",
                "123456",
                "admin",
            )
            self.chamado_professor = criar_chamado(
                "Computador nao liga",
                "Sala 3",
                self.professor.id,
            )
            self.chamado_outro = criar_chamado(
                "Impressora sem tinta",
                "Secretaria",
                self.outro_professor.id,
            )

    def login(self, email, senha="123456"):
        return self.client.post(
            "/api/login",
            json={"email": email, "senha": senha},
        )

    def test_delete_chamado_exige_admin(self):
        resposta_sem_login = self.client.delete(
            f"/api/chamados/{self.chamado_professor.id}"
        )
        self.assertEqual(resposta_sem_login.status_code, 401)

        self.login("professor@example.com")
        resposta_professor = self.client.delete(
            f"/api/chamados/{self.chamado_professor.id}"
        )
        self.assertEqual(resposta_professor.status_code, 403)

        self.client.post("/api/logout")
        self.login("admin@example.com")
        resposta_admin = self.client.delete(
            f"/api/chamados/{self.chamado_professor.id}"
        )
        self.assertEqual(resposta_admin.status_code, 200)

    def test_professor_nao_lista_chamados_de_outro_usuario(self):
        self.login("professor@example.com")

        resposta = self.client.get(
            f"/api/chamados/usuario/{self.outro_professor.id}"
        )

        self.assertEqual(resposta.status_code, 403)

    def test_busca_filtra_chamados_para_professor(self):
        self.login("professor@example.com")

        resposta = self.client.get("/api/chamados/busca?q=a")
        dados = resposta.get_json()
        ids = {item["id"] for item in dados}

        self.assertEqual(resposta.status_code, 200)
        self.assertIn(self.chamado_professor.id, ids)
        self.assertNotIn(self.chamado_outro.id, ids)


if __name__ == "__main__":
    unittest.main()
