from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.reserva    import Reserva
from app.models.habitacion import Habitacion
from app.models.servicio   import Servicio
from app.utils.auth_middleware import rol_requerido
from app.utils.helpers import calcular_total
from datetime import date

reservas_bp = Blueprint("reservas", __name__)


# ── GET /api/reservas ────────────────────────────────────────────────────────
@reservas_bp.route("/", methods=["GET"])
@jwt_required()
def listar_reservas():
    """
    - Huésped: solo ve sus propias reservas.
    - Admin/Recepcionista: ve todas (con filtro opcional ?estado=confirmada).
    """
    claims     = get_jwt()
    usuario_id = int(get_jwt_identity())
    rol        = claims.get("rol")

    query = Reserva.query

    if rol == "huesped":
        query = query.filter_by(usuario_id=usuario_id)

    estado = request.args.get("estado")
    if estado:
        query = query.filter_by(estado=estado)

    reservas = query.order_by(Reserva.creado_en.desc()).all()
    return jsonify({
        "total": len(reservas),
        "reservas": [r.to_dict() for r in reservas]
    }), 200


# ── GET /api/reservas/<id> ───────────────────────────────────────────────────
@reservas_bp.route("/<int:id>", methods=["GET"])
@jwt_required()
def obtener_reserva(id):
    claims     = get_jwt()
    usuario_id = int(get_jwt_identity())
    rol        = claims.get("rol")

    reserva = Reserva.query.get_or_404(id)

    # Huésped solo puede ver sus propias reservas
    if rol == "huesped" and reserva.usuario_id != usuario_id:
        return jsonify({"error": "Acceso denegado."}), 403

    return jsonify({"reserva": reserva.to_dict()}), 200


# ── POST /api/reservas ───────────────────────────────────────────────────────
@reservas_bp.route("/", methods=["POST"])
@jwt_required()
def crear_reserva():
    """
    Crea una nueva reserva.
    Body JSON: {
        habitacion_id, fecha_checkin, fecha_checkout,
        num_huespedes, servicios_ids: [1, 3]   ← opcional
    }
    """
    usuario_id = int(get_jwt_identity())
    data = request.get_json()

    # Validar campos obligatorios
    campos = ["habitacion_id", "fecha_checkin", "fecha_checkout"]
    faltantes = [c for c in campos if not data.get(c)]
    if faltantes:
        return jsonify({"error": f"Campos requeridos: {', '.join(faltantes)}"}), 400

    # Parsear fechas
    try:
        checkin  = date.fromisoformat(data["fecha_checkin"])
        checkout = date.fromisoformat(data["fecha_checkout"])
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}), 400

    if checkout <= checkin:
        return jsonify({"error": "El checkout debe ser posterior al checkin."}), 400

    if checkin < date.today():
        return jsonify({"error": "No puedes reservar en fechas pasadas."}), 400

    # Verificar que la habitación existe y está disponible
    habitacion = Habitacion.query.get_or_404(data["habitacion_id"])

    if habitacion.estado == "mantenimiento":
        return jsonify({"error": "La habitación está en mantenimiento."}), 409

    # Verificar que no haya cruce de fechas con otra reserva
    cruce = Reserva.query.filter(
        Reserva.habitacion_id == habitacion.id,
        Reserva.estado.in_(["pendiente", "confirmada"]),
        Reserva.fecha_checkin  < checkout,
        Reserva.fecha_checkout > checkin
    ).first()

    if cruce:
        return jsonify({
            "error": "La habitación no está disponible en las fechas seleccionadas."
        }), 409

    # Servicios adicionales (opcional)
    servicios = []
    for sid in data.get("servicios_ids", []):
        s = Servicio.query.get(sid)
        if s:
            servicios.append(s)

    # Calcular total con IVA
    total = calcular_total(
        float(habitacion.precio_noche), checkin, checkout, servicios
    )

    # Crear reserva
    reserva = Reserva(
        usuario_id    = usuario_id,
        habitacion_id = habitacion.id,
        fecha_checkin = checkin,
        fecha_checkout= checkout,
        num_huespedes = data.get("num_huespedes", 1),
        estado        = "pendiente"
    )
    reserva.servicios = servicios

    db.session.add(reserva)
    db.session.commit()

    return jsonify({
        "mensaje":   "Reserva creada exitosamente.",
        "reserva":   reserva.to_dict(),
        "total_estimado": total
    }), 201

# ── PUT /api/reservas/<id> ───────────────────────────────────────────────────
@reservas_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()
def modificar_reserva(id):
    """
    Modifica una reserva mientras esté en estado 'pendiente'.
    - Huésped: solo puede modificar su propia reserva.
    - Admin/Recepcionista: pueden modificar cualquiera.
    Body JSON (todos los campos son opcionales): {
        fecha_checkin, fecha_checkout, num_huespedes, servicios_ids: [1, 3]
    }
    """
    claims     = get_jwt()
    usuario_id = int(get_jwt_identity())
    rol        = claims.get("rol")

    reserva = Reserva.query.get_or_404(id)

    if rol == "huesped" and reserva.usuario_id != usuario_id:
        return jsonify({"error": "No puedes modificar una reserva que no es tuya."}), 403

    if reserva.estado != "pendiente":
        return jsonify({"error": "Solo se pueden modificar reservas en estado 'pendiente'."}), 409

    data = request.get_json() or {}

    checkin  = reserva.fecha_checkin
    checkout = reserva.fecha_checkout

    if "fecha_checkin" in data:
        try:
            checkin = date.fromisoformat(data["fecha_checkin"])
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido en fecha_checkin. Usa YYYY-MM-DD."}), 400

    if "fecha_checkout" in data:
        try:
            checkout = date.fromisoformat(data["fecha_checkout"])
        except ValueError:
            return jsonify({"error": "Formato de fecha inválido en fecha_checkout. Usa YYYY-MM-DD."}), 400

    if checkout <= checkin:
        return jsonify({"error": "El checkout debe ser posterior al checkin."}), 400

    if checkin < date.today():
        return jsonify({"error": "No puedes reservar en fechas pasadas."}), 400

    # Verificar cruce con otras reservas de la misma habitación (excluyendo esta misma)
    cruce = Reserva.query.filter(
        Reserva.habitacion_id == reserva.habitacion_id,
        Reserva.id != reserva.id,
        Reserva.estado.in_(["pendiente", "confirmada"]),
        Reserva.fecha_checkin  < checkout,
        Reserva.fecha_checkout > checkin
    ).first()

    if cruce:
        return jsonify({
            "error": "La habitación no está disponible en las nuevas fechas seleccionadas."
        }), 409

    reserva.fecha_checkin  = checkin
    reserva.fecha_checkout = checkout

    if "num_huespedes" in data:
        reserva.num_huespedes = data["num_huespedes"]

    if "servicios_ids" in data:
        servicios = []
        for sid in data["servicios_ids"]:
            s = Servicio.query.get(sid)
            if s:
                servicios.append(s)
        reserva.servicios = servicios

    db.session.commit()

    total = calcular_total(
        float(reserva.habitacion.precio_noche), checkin, checkout, reserva.servicios
    )

    return jsonify({
        "mensaje":        "Reserva actualizada correctamente.",
        "reserva":        reserva.to_dict(),
        "total_estimado": total
    }), 200


# ── PUT /api/reservas/<id>/estado ────────────────────────────────────────────
@reservas_bp.route("/<int:id>/estado", methods=["PUT"])
@jwt_required()
@rol_requerido("admin", "recepcionista")
def cambiar_estado(id):
    """
    Admin/Recepcionista pueden confirmar, cancelar o completar reservas.
    Body JSON: { estado: "confirmada" | "cancelada" | "completada" }
    """
    reserva = Reserva.query.get_or_404(id)
    data    = request.get_json()
    estados_validos = ["pendiente", "confirmada", "cancelada", "completada"]

    nuevo_estado = data.get("estado")
    if nuevo_estado not in estados_validos:
        return jsonify({"error": f"Estado inválido. Opciones: {estados_validos}"}), 400

    reserva.estado = nuevo_estado

    # Si se confirma, marcar la habitación como ocupada
    if nuevo_estado == "confirmada":
        reserva.habitacion.estado = "ocupada"

    # Si se cancela o completa, liberar la habitación
    if nuevo_estado in ["cancelada", "completada"]:
        reserva.habitacion.estado = "disponible"

    db.session.commit()
    return jsonify({"mensaje": f"Reserva marcada como '{nuevo_estado}'.", "reserva": reserva.to_dict()}), 200


# ── DELETE /api/reservas/<id> ────────────────────────────────────────────────
@reservas_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def cancelar_reserva(id):
    """
    El huésped puede cancelar su propia reserva (si aún está pendiente).
    Admin puede cancelar cualquiera.
    """
    claims     = get_jwt()
    usuario_id = int(get_jwt_identity())
    rol        = claims.get("rol")

    reserva = Reserva.query.get_or_404(id)

    if rol == "huesped":
        if reserva.usuario_id != usuario_id:
            return jsonify({"error": "No puedes cancelar una reserva que no es tuya."}), 403
        if reserva.estado == "confirmada":
            return jsonify({"error": "No puedes cancelar una reserva ya confirmada. Contacta recepción."}), 409

    reserva.estado = "cancelada"
    reserva.habitacion.estado = "disponible"
    db.session.commit()

    return jsonify({"mensaje": "Reserva cancelada.", "reserva": reserva.to_dict()}), 200
