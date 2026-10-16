from app import db
from datetime import datetime
from app.models.servicio import reserva_servicios

class Reserva(db.Model):
    __tablename__ = "reservas"

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    habitacion_id   = db.Column(db.Integer, db.ForeignKey("habitaciones.id"), nullable=False)
    fecha_checkin   = db.Column(db.Date, nullable=False)
    fecha_checkout  = db.Column(db.Date, nullable=False)
    num_huespedes   = db.Column(db.Integer, default=1)
    estado          = db.Column(
        db.Enum("pendiente", "confirmada", "cancelada", "completada"),
        default="pendiente"
    )
    creado_en       = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    servicios = db.relationship("Servicio", secondary=reserva_servicios, lazy="subquery")
    pago      = db.relationship("Pago", backref="reserva", uselist=False)  # 1-a-1

    @property
    def noches(self) -> int:
        """Calcula automáticamente el número de noches."""
        return (self.fecha_checkout - self.fecha_checkin).days

    def to_dict(self):
        return {
            "id":             self.id,
            "usuario_id":     self.usuario_id,
            "habitacion_id":  self.habitacion_id,
            "fecha_checkin":  self.fecha_checkin.isoformat(),
            "fecha_checkout": self.fecha_checkout.isoformat(),
            "noches":         self.noches,
            "num_huespedes":  self.num_huespedes,
            "estado":         self.estado,
            "servicios":      [s.to_dict() for s in self.servicios],
            "creado_en":      self.creado_en.isoformat(),
        }
