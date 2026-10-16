from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app import db
from app.models.pago    import Pago
from app.models.reserva import Reserva
from app.utils.auth_middleware import rol_requerido
from app.utils.helpers import calcular_total
from app.utils.wompi import generar_firma_integridad, consultar_transaccion, WOMPI_PUBLIC_KEY
import uuid

pagos_bp = Blueprint("pagos", __name__)


# ── POST /api/pagos/iniciar ───────────────────────────────────────────────
@pagos_bp.route("/iniciar", methods=["POST"])
@jwt_required()
def iniciar_pago():
    """
    Genera los datos que el frontend necesita para abrir el widget de Wompi.
    Body JSON: { reserva_id }
    """
    usuario_id = int(get_jwt_identity())
    claims     = get_jwt()
    rol        = claims.get("rol")
    data       = request.get_json()

    if not data.get("reserva_id"):
        return jsonify({"error": "reserva_id es requerido."}), 400

    reserva = Reserva.query.get_or_404(data["reserva_id"])

    if rol == "huesped" and reserva.usuario_id != usuario_id:
        return jsonify({"error": "No puedes pagar una reserva que no es tuya."}), 403

    if reserva.pago and reserva.pago.estado == "aprobado":
        return jsonify({"error": "Esta reserva ya tiene un pago aprobado."}), 409

    monto = calcular_total(
        float(reserva.habitacion.precio_noche),
        reserva.fecha_checkin,
        reserva.fecha_checkout,
        reserva.servicios
    )
    monto_en_centavos = int(round(monto * 100))
    referencia        = f"AEROLITO-{reserva.id}-{uuid.uuid4().hex[:8].upper()}"
    firma             = generar_firma_integridad(referencia, monto_en_centavos, "COP")

    return jsonify({
        "llave_publica":     WOMPI_PUBLIC_KEY,
        "referencia":        referencia,
        "monto_en_centavos": monto_en_centavos,
        "moneda":            "COP",
        "firma_integridad":  firma
    }), 200


# ── POST /api/pagos/confirmar ─────────────────────────────────────────────
@pagos_bp.route("/confirmar", methods=["POST"])
@jwt_required()
def confirmar_pago():
    """
    El frontend llama esto justo después de que el widget de Wompi cierra
    con un id de transacción. Verificamos ese id contra la API de Wompi
    (no confiamos en el estado que reporta el navegador) y guardamos el pago.
    Body JSON: { reserva_id, transaccion_id, metodo }
    """
    usuario_id = int(get_jwt_identity())
    claims     = get_jwt()
    rol        = claims.get("rol")
    data       = request.get_json()

    reserva = Reserva.query.get_or_404(data["reserva_id"])

    if rol == "huesped" and reserva.usuario_id != usuario_id:
        return jsonify({"error": "No puedes pagar una reserva que no es tuya."}), 403

    try:
        transaccion = consultar_transaccion(data["transaccion_id"])
    except Exception:
        return jsonify({"error": "No se pudo verificar la transacción con Wompi."}), 502

    mapa_estados = {
        "APPROVED": "aprobado",
        "DECLINED": "rechazado",
        "ERROR":    "rechazado",
        "VOIDED":   "rechazado",
        "PENDING":  "pendiente"
    }
    estado_local = mapa_estados.get(transaccion["status"], "pendiente")

    pago = reserva.pago
    if not pago:
        pago = Pago(reserva_id=reserva.id, metodo=data.get("metodo", "tarjeta"))
        db.session.add(pago)

    pago.monto_total          = transaccion["amount_in_cents"] / 100
    pago.estado               = estado_local
    pago.referencia           = transaccion["reference"]
    pago.transaccion_wompi_id = transaccion["id"]
    pago.codigo_transaccion   = transaccion["id"]

    if estado_local == "aprobado":
        reserva.estado            = "confirmada"
        reserva.habitacion.estado = "ocupada"

    db.session.commit()

    return jsonify({
        "mensaje": "¡Pago aprobado! Tu reserva está confirmada." if estado_local == "aprobado" else f"El pago quedó en estado: {estado_local}.",
        "pago":    pago.to_dict(),
        "reserva": reserva.to_dict()
    }), 200


# ── GET /api/pagos/<reserva_id> ───────────────────────────────────────────
@pagos_bp.route("/<int:reserva_id>", methods=["GET"])
@jwt_required()
def obtener_pago(reserva_id):
    usuario_id = int(get_jwt_identity())
    claims     = get_jwt()
    rol        = claims.get("rol")

    reserva = Reserva.query.get_or_404(reserva_id)

    if rol == "huesped" and reserva.usuario_id != usuario_id:
        return jsonify({"error": "Acceso denegado."}), 403

    if not reserva.pago:
        return jsonify({"error": "Esta reserva aún no tiene un pago registrado."}), 404

    return jsonify({"pago": reserva.pago.to_dict(), "reserva": reserva.to_dict()}), 200


# ── GET /api/pagos ────────────────────────────────────────────────────────
@pagos_bp.route("/", methods=["GET"])
@jwt_required()
@rol_requerido("admin", "recepcionista")
def listar_pagos():
    estado = request.args.get("estado")
    query  = Pago.query
    if estado:
        query = query.filter_by(estado=estado)
    pagos = query.order_by(Pago.fecha.desc()).all()
    return jsonify({"total": len(pagos), "pagos": [p.to_dict() for p in pagos]}), 200