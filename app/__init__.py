from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from app.config import config_map
import os

db      = SQLAlchemy()
migrate = Migrate()
jwt     = JWTManager()

def create_app():
    app = Flask(__name__)

    # Cargar configuración según entorno
    env = os.getenv("FLASK_ENV", "development")
    app.config.from_object(config_map[env])

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)

    # Registrar modelos (para que Flask-Migrate los detecte)
    with app.app_context():
        from app.models import usuario, habitacion, servicio, reserva, pago

    # Registrar blueprints (rutas)
    from app.routes.auth        import auth_bp
    from app.routes.habitaciones import habitaciones_bp
    from app.routes.reservas    import reservas_bp
    from app.routes.servicios   import servicios_bp
    from app.routes.pagos       import pagos_bp
    from app.routes.dashboard   import dashboard_bp

    app.register_blueprint(auth_bp,         url_prefix="/api/auth")
    app.register_blueprint(habitaciones_bp, url_prefix="/api/habitaciones")
    app.register_blueprint(reservas_bp,     url_prefix="/api/reservas")
    app.register_blueprint(servicios_bp,    url_prefix="/api/servicios")
    app.register_blueprint(pagos_bp,        url_prefix="/api/pagos")
    app.register_blueprint(dashboard_bp,    url_prefix="/api/dashboard")

    return app
