from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt

def rol_requerido(*roles):
    """
    Decorador que protege rutas por rol.
    Uso:
        @rol_requerido("admin")
        @rol_requerido("admin", "recepcionista")
    """
    def decorador(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims.get("rol") not in roles:
                return jsonify({"error": "Acceso denegado. No tienes permisos suficientes."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorador
