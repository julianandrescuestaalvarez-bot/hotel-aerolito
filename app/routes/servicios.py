from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.servicio import Servicio
from app.utils.auth_middleware import rol_requerido

servicios_bp = Blueprint("servicios", __name__)


# ── GET /api/servicios ───────────────────────────────────────────────────────
@servicios_bp.route("/", methods=["GET"])
def listar_servicios():
    """Público: cualquiera puede ver los servicios disponibles."""
    servicios = Servicio.query.all()
    return jsonify({
        "total": len(servicios),
        "servicios": [s.to_dict() for s in servicios]
    }), 200


# ── GET /api/servicios/<id> ──────────────────────────────────────────────────
@servicios_bp.route("/<int:id>", methods=["GET"])
def obtener_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    return jsonify({"servicio": servicio.to_dict()}), 200


# ── POST /api/servicios ──────────────────────────────────────────────────────
@servicios_bp.route("/", methods=["POST"])
@jwt_required()
@rol_requerido("admin")
def crear_servicio():
    data = request.get_json()

    if not data.get("nombre") or not data.get("precio"):
        return jsonify({"error": "Nombre y precio son requeridos."}), 400

    servicio = Servicio(
        nombre      = data["nombre"].strip(),
        descripcion = data.get("descripcion", ""),
        precio      = data["precio"]
    )
    db.session.add(servicio)
    db.session.commit()
    return jsonify({"mensaje": "Servicio creado.", "servicio": servicio.to_dict()}), 201


# ── PUT /api/servicios/<id> ──────────────────────────────────────────────────
@servicios_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@rol_requerido("admin")
def actualizar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    data = request.get_json()

    for campo in ["nombre", "descripcion", "precio"]:
        if campo in data:
            setattr(servicio, campo, data[campo])

    db.session.commit()
    return jsonify({"mensaje": "Servicio actualizado.", "servicio": servicio.to_dict()}), 200


# ── DELETE /api/servicios/<id> ───────────────────────────────────────────────
@servicios_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@rol_requerido("admin")
def eliminar_servicio(id):
    servicio = Servicio.query.get_or_404(id)
    db.session.delete(servicio)
    db.session.commit()
    return jsonify({"mensaje": f"Servicio '{servicio.nombre}' eliminado."}), 200
