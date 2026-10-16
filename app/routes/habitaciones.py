from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.habitacion import Habitacion
from app.models.reserva import Reserva
from app.utils.auth_middleware import rol_requerido
from datetime import date

habitaciones_bp = Blueprint("habitaciones", __name__)


# ── GET /api/habitaciones ────────────────────────────────────────────────────
@habitaciones_bp.route("/", methods=["GET"])
def listar_habitaciones():
    """
    Lista habitaciones. Acepta filtros por query params:
      ?checkin=YYYY-MM-DD&checkout=YYYY-MM-DD  → solo disponibles en esas fechas
      ?tipo=suite
      ?capacidad=3
    """
    query = Habitacion.query

    # Filtro por tipo
    tipo = request.args.get("tipo")
    if tipo:
        query = query.filter_by(tipo=tipo)

    # Filtro por capacidad mínima
    capacidad = request.args.get("capacidad", type=int)
    if capacidad:
        query = query.filter(Habitacion.capacidad >= capacidad)

    # Filtro por disponibilidad en fechas (el más importante)
    checkin_str  = request.args.get("checkin")
    checkout_str = request.args.get("checkout")

    if checkin_str and checkout_str:
        try:
            checkin  = date.fromisoformat(checkin_str)
            checkout = date.fromisoformat(checkout_str)
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400

        if checkout <= checkin:
            return jsonify({"error": "El checkout debe ser posterior al checkin."}), 400

        # Excluir habitaciones con reservas que se crucen con el rango pedido
        habitaciones_ocupadas = db.session.query(Reserva.habitacion_id).filter(
            Reserva.estado.in_(["pendiente", "confirmada"]),
            Reserva.fecha_checkin  < checkout,
            Reserva.fecha_checkout > checkin
        ).subquery()

        query = query.filter(
            Habitacion.id.notin_(habitaciones_ocupadas),
            Habitacion.estado == "disponible"
        )

    habitaciones = query.all()
    return jsonify({
        "total": len(habitaciones),
        "habitaciones": [h.to_dict() for h in habitaciones]
    }), 200


# ── GET /api/habitaciones/<id> ───────────────────────────────────────────────
@habitaciones_bp.route("/<int:id>", methods=["GET"])
def obtener_habitacion(id):
    habitacion = Habitacion.query.get_or_404(id)
    return jsonify({"habitacion": habitacion.to_dict()}), 200


# ── POST /api/habitaciones ───────────────────────────────────────────────────
@habitaciones_bp.route("/", methods=["POST"])
@jwt_required()
@rol_requerido("admin")
def crear_habitacion():
    """Solo admin puede crear habitaciones."""
    data = request.get_json()

    campos = ["numero", "tipo", "precio_noche", "capacidad"]
    faltantes = [c for c in campos if not data.get(c)]
    if faltantes:
        return jsonify({"error": f"Campos requeridos: {', '.join(faltantes)}"}), 400

    if Habitacion.query.filter_by(numero=data["numero"]).first():
        return jsonify({"error": f"Ya existe la habitación número {data['numero']}."}), 409

    habitacion = Habitacion(
        numero       = data["numero"],
        tipo         = data["tipo"],
        precio_noche = data["precio_noche"],
        capacidad    = data["capacidad"],
        descripcion  = data.get("descripcion", ""),
        estado       = data.get("estado", "disponible")
    )
    db.session.add(habitacion)
    db.session.commit()

    return jsonify({"mensaje": "Habitación creada.", "habitacion": habitacion.to_dict()}), 201


# ── PUT /api/habitaciones/<id> ───────────────────────────────────────────────
@habitaciones_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
@rol_requerido("admin", "recepcionista")
def actualizar_habitacion(id):
    """Admin y recepcionista pueden editar (ej: cambiar estado a mantenimiento)."""
    habitacion = Habitacion.query.get_or_404(id)
    data = request.get_json()

    for campo in ["tipo", "precio_noche", "capacidad", "descripcion", "estado"]:
        if campo in data:
            setattr(habitacion, campo, data[campo])

    db.session.commit()
    return jsonify({"mensaje": "Habitación actualizada.", "habitacion": habitacion.to_dict()}), 200


# ── DELETE /api/habitaciones/<id> ────────────────────────────────────────────
@habitaciones_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
@rol_requerido("admin")
def eliminar_habitacion(id):
    habitacion = Habitacion.query.get_or_404(id)
    db.session.delete(habitacion)
    db.session.commit()
    return jsonify({"mensaje": f"Habitación {habitacion.numero} eliminada."}), 200
