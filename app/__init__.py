from flask import Flask

from app.extensions import db, migrate
from app.routes.site import site
from app.routes.admin import admin

# Importa os modelos para o Flask-Migrate reconhecê-los
from app.models import Produto, Categoria


def create_app():

    app = Flask(__name__)

    app.config["SECRET_KEY"] = "sgae"

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///sgae.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["UPLOAD_FOLDER"] = "app/static/img/products"

    # =========================================================
    # DADOS DO ADMINISTRADOR
    # =========================================================

    app.config["ADMIN_USERNAME"] = "admin"
    app.config["ADMIN_PASSWORD"] = "sgae123"

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(site)
    app.register_blueprint(admin)

    return app