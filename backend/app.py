import os
from flask import Flask, render_template, redirect


from database import db


# Importa os models para o SQLAlchemy reconhecer as tabelas no db.create_all()
from models.chamado import Chamado
from models.usuario import Usuario
from models.categoria import Categoria
from models.material import Material
from models.comentario import Comentario
from models.evento import Evento

# Blueprints da API
from routes.chamados_routes import chamados_bp
from routes.auth_routes import auth_bp
from routes.usuarios_routes import usuarios_bp
from routes.categorias_routes import categorias_bp
from routes.materiais_routes import materiais_bp
from routes.comentarios_routes import comentarios_bp
from routes.eventos_routes import eventos_bp

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Configurações principais
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///chamados.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

db.init_app(app)

# Inclusão dos Blueprints:
app.register_blueprint(chamados_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(materiais_bp)
app.register_blueprint(comentarios_bp)
app.register_blueprint(eventos_bp)


# ===== Páginas (Jinja2 + Bootstrap) =====
@app.route('/')
def index():
    return redirect('/login')

@app.route('/login')
def page_login():
    return render_template('login.html')

@app.route('/dashboard')
def page_dashboard():
    return render_template('dashboard.html')

@app.route('/nova-solicitacao')
def page_nova_solicitacao():
    return render_template('nova_solicitacao.html')

@app.route('/detalhes/<int:chamado_id>')
def page_detalhes(chamado_id):
    return render_template('detalhes_solicitacao.html', chamado_id=chamado_id)

@app.route('/admin')
def page_admin():
    return render_template('admin.html')


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
