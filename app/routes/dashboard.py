from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app import db
from app.models.reserva    import Reserva
from app.models.habitacion import Habitacion
from app.models.pago       import Pago
from app.models.usuario    import Usuario
from app.utils.auth_middleware import rol_requerido
from datetime import date
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


# ── GET /api/dashboard/resumen ───────────────────────────────────────────────
@dashboard_bp.route("/resumen", methods=["GET"])
@jwt_required()
@rol_requerido("admin", "recepcionista")
def resumen():
    """
    Métricas generales para el dashboard:
    - Check-ins de hoy
    - Habitaciones libres vs total
    - Porcentaje de ocupación
    - Ingresos del día
    """
    hoy = date.today()

    # Check-ins de hoy
    checkins_hoy = Reserva.query.filter(
        Reserva.fecha_checkin == hoy,
        Reserva.estado == "confirmada"
    ).count()

    # Totales de habitaciones
    total_habitaciones = Habitacion.query.count()
    habitaciones_libres = Habitacion.query.filter_by(estado="disponible").count()
    ocupacion_pct = round(
        ((total_habitaciones - habitaciones_libres) / total_habitaciones * 100)
        if total_habitaciones else 0, 1
    )

    # Ingresos del día (pagos aprobados hoy)
    ingresos_hoy = db.session.query(func.sum(Pago.monto_total)).filter(
        func.date(Pago.fecha) == hoy,
        Pago.estado == "aprobado"
    ).scalar() or 0

    return jsonify({
        "fecha":              hoy.isoformat(),
        "checkins_hoy":       checkins_hoy,
        "habitaciones_libres": habitaciones_libres,
        "total_habitaciones": total_habitaciones,
        "ocupacion_pct":      ocupacion_pct,
        "ingresos_hoy":       float(ingresos_hoy)
    }), 200


# ── GET /api/dashboard/reservas-recientes ────────────────────────────────────
@dashboard_bp.route("/reservas-recientes", methods=["GET"])
@jwt_required()
@rol_requerido("admin", "recepcionista")
def reservas_recientes():
    """Últimas 10 reservas con datos del huésped y la habitación."""
    reservas = Reserva.query.order_by(Reserva.creado_en.desc()).limit(10).all()

    resultado = []
    for r in reservas:
        resultado.append({
            **r.to_dict(),
            "huesped_nombre":    r.huesped.nombre,
            "huesped_email":     r.huesped.email,
            "habitacion_numero": r.habitacion.numero,
            "habitacion_tipo":   r.habitacion.tipo,
        })

    return jsonify({"reservas": resultado}), 200


# ── GET /api/dashboard/usuarios ──────────────────────────────────────────────
@dashboard_bp.route("/usuarios", methods=["GET"])
@jwt_required()
@rol_requerido("admin")
def listar_usuarios():
    """Solo admin puede ver la lista de todos los usuarios."""
    usuarios = Usuario.query.order_by(Usuario.creado_en.desc()).all()
    return jsonify({
        "total":    len(usuarios),
        "usuarios": [u.to_dict() for u in usuarios]
    }), 200
