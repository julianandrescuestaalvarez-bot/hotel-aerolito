from app import db
from datetime import datetime

class Pago(db.Model):
    __tablename__ = "pagos"

    id                  = db.Column(db.Integer, primary_key=True)
    reserva_id          = db.Column(db.Integer, db.ForeignKey("reservas.id"), unique=True, nullable=False)
    metodo              = db.Column(db.Enum("tarjeta", "pse"), nullable=False)
    monto_total         = db.Column(db.Numeric(12, 2), nullable=False)
    estado              = db.Column(db.Enum("pendiente", "aprobado", "rechazado"), default="pendiente")
    codigo_transaccion  = db.Column(db.String(50), unique=True)
    codigo_autorizacion = db.Column(db.String(50))
    referencia           = db.Column(db.String(100), unique=True)   # 👈 nuevo: referencia interna que le pasamos a Wompi
    transaccion_wompi_id = db.Column(db.String(50), unique=True)    # 👈 nuevo: ID de transacción que Wompi nos devuelve
    fecha               = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id":                    self.id,
            "reserva_id":            self.reserva_id,
            "metodo":                self.metodo,
            "monto_total":           float(self.monto_total),
            "estado":                self.estado,
            "codigo_transaccion":    self.codigo_transaccion,
            "codigo_autorizacion":   self.codigo_autorizacion,
            "referencia":            self.referencia,
            "transaccion_wompi_id":  self.transaccion_wompi_id,
            "fecha":                 self.fecha.isoformat(),
        }