from flask import Flask
from database import db
from models.chamado import Chamado
from models.usuario import Usuario

# Inclusão das Rotas:
from routes.chamados_routes import chamados_bp
from routes.auth_routes import auth_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chamados.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Inclusão dos Blueprints:
app.register_blueprint(chamados_bp)
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)