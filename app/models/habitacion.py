from app import db

class Habitacion(db.Model):
    __tablename__ = "habitaciones"

    id           = db.Column(db.Integer, primary_key=True)
    numero       = db.Column(db.String(10), unique=True, nullable=False)  # ej: "101", "205"
    tipo         = db.Column(db.Enum("sencilla", "doble", "suite", "familiar"), nullable=False)
    precio_noche = db.Column(db.Numeric(10, 2), nullable=False)
    capacidad    = db.Column(db.Integer, nullable=False, default=2)
    descripcion  = db.Column(db.Text)
    estado       = db.Column(db.Enum("disponible", "ocupada", "mantenimiento"), default="disponible")

    # Relación: una habitación puede tener muchas reservas (historial)
    reservas = db.relationship("Reserva", backref="habitacion", lazy=True)

    def to_dict(self):
        return {
            "id":           self.id,
            "numero":       self.numero,
            "tipo":         self.tipo,
            "precio_noche": float(self.precio_noche),
            "capacidad":    self.capacidad,
            "descripcion":  self.descripcion,
            "estado":       self.estado,
        }
