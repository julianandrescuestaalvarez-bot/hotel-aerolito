from app import db

# Tabla pivote: relaciona reservas con servicios adicionales
reserva_servicios = db.Table(
    "reserva_servicios",
    db.Column("id",          db.Integer, primary_key=True),
    db.Column("reserva_id",  db.Integer, db.ForeignKey("reservas.id"),  nullable=False),
    db.Column("servicio_id", db.Integer, db.ForeignKey("servicios.id"), nullable=False),
    db.Column("cantidad",    db.Integer, default=1),
)

class Servicio(db.Model):
    __tablename__ = "servicios"

    id          = db.Column(db.Integer, primary_key=True)
    nombre      = db.Column(db.String(100), nullable=False)   # ej: "Desayuno", "Spa", "Parqueadero"
    descripcion = db.Column(db.Text)
    precio      = db.Column(db.Numeric(10, 2), nullable=False)

    def to_dict(self):
        return {
            "id":          self.id,
            "nombre":      self.nombre,
            "descripcion": self.descripcion,
            "precio":      float(self.precio),
        }
