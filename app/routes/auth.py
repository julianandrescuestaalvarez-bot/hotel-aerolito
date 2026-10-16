from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, get_jwt
)
from app import db
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__)


# ── POST /api/auth/registro ──────────────────────────────────────────────────
@auth_bp.route("/registro", methods=["POST"])
def registro():
    """
    Registra un nuevo huésped.
    Body JSON: { nombre, email, contraseña }
    """
    data = request.get_json()

    # Validar campos requeridos
    campos = ["nombre", "email", "contraseña"]
    faltantes = [c for c in campos if not data.get(c)]
    if faltantes:
        return jsonify({"error": f"Campos requeridos: {', '.join(faltantes)}"}), 400

    # Verificar que el email no esté registrado
    if Usuario.query.filter_by(email=data["email"].lower()).first():
        return jsonify({"error": "El correo ya está registrado."}), 409

    # Crear usuario (rol huésped por defecto)
    nuevo = Usuario(
        nombre=data["nombre"].strip(),
        email=data["email"].lower().strip(),
        rol="huesped"
    )
    nuevo.set_contraseña(data["contraseña"])

    db.session.add(nuevo)
    db.session.commit()

    # Generar token inmediatamente para que quede logueado
    token = create_access_token(
        identity=str(nuevo.id),
        additional_claims={"rol": nuevo.rol, "nombre": nuevo.nombre}
    )

    return jsonify({
        "mensaje": "Registro exitoso.",
        "token": token,
        "usuario": nuevo.to_dict()
    }), 201


# ── POST /api/auth/login ─────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Inicia sesión y devuelve un JWT.
    Body JSON: { email, contraseña }
    """
    data = request.get_json()

    if not data.get("email") or not data.get("contraseña"):
        return jsonify({"error": "Email y contraseña son requeridos."}), 400

    usuario = Usuario.query.filter_by(email=data["email"].lower().strip()).first()

    # Mismo mensaje para email inexistente o contraseña incorrecta (seguridad)
    if not usuario or not usuario.verificar_contraseña(data["contraseña"]):
        return jsonify({"error": "Credenciales incorrectas."}), 401

    token = create_access_token(
        identity=str(usuario.id),
        additional_claims={"rol": usuario.rol, "nombre": usuario.nombre}
    )

    return jsonify({
        "mensaje": f"Bienvenido, {usuario.nombre}.",
        "token": token,
        "usuario": usuario.to_dict()
    }), 200


# ── GET /api/auth/perfil ─────────────────────────────────────────────────────
@auth_bp.route("/perfil", methods=["GET"])
@jwt_required()
def perfil():
    """
    Devuelve los datos del usuario autenticado.
    Header: Authorization: Bearer <token>
    """
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    return jsonify({"usuario": usuario.to_dict()}), 200


# ── PUT /api/auth/perfil ─────────────────────────────────────────────────────
@auth_bp.route("/perfil", methods=["PUT"])
@jwt_required()
def actualizar_perfil():
    """
    Actualiza nombre o contraseña del usuario autenticado.
    Body JSON: { nombre?, contraseña_actual?, contraseña_nueva? }
    """
    usuario_id = int(get_jwt_identity())
    usuario = Usuario.query.get_or_404(usuario_id)
    data = request.get_json()

    if "nombre" in data and data["nombre"].strip():
        usuario.nombre = data["nombre"].strip()

    # Cambio de contraseña: requiere la actual
    if "contraseña_nueva" in data:
        if not data.get("contraseña_actual"):
            return jsonify({"error": "Debes enviar tu contraseña actual para cambiarla."}), 400
        if not usuario.verificar_contraseña(data["contraseña_actual"]):
            return jsonify({"error": "La contraseña actual es incorrecta."}), 401
        usuario.set_contraseña(data["contraseña_nueva"])

    db.session.commit()
    return jsonify({"mensaje": "Perfil actualizado.", "usuario": usuario.to_dict()}), 200


# ── POST /api/auth/logout ────────────────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout informativo. El cliente debe eliminar el token localmente.
    (Para revocación real de tokens se necesitaría una blocklist en Redis.)
    """
    claims = get_jwt()
    return jsonify({
        "mensaje": f"Sesión cerrada. Hasta pronto, {claims.get('nombre', '')}."
    }), 200
