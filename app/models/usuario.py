from app import db
import bcrypt
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = "usuarios"

    id             = db.Column(db.Integer, primary_key=True)
    nombre         = db.Column(db.String(120), nullable=False)
    email          = db.Column(db.String(120), unique=True, nullable=False)
    contraseña_hash = db.Column(db.String(255), nullable=False)
    rol            = db.Column(db.Enum("huesped", "recepcionista", "admin"), default="huesped", nullable=False)
    creado_en      = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación: un usuario puede tener muchas reservas
    reservas = db.relationship("Reserva", backref="huesped", lazy=True)

    def set_contraseña(self, contraseña_plana: str):
        """Hashea y guarda la contraseña."""
        self.contraseña_hash = bcrypt.hashpw(
            contraseña_plana.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    def verificar_contraseña(self, contraseña_plana: str) -> bool:
        """Devuelve True si la contraseña coincide con el hash."""
        return bcrypt.checkpw(
            contraseña_plana.encode("utf-8"),
            self.contraseña_hash.encode("utf-8")
        )

    def to_dict(self):
        return {
            "id":        self.id,
            "nombre":    self.nombre,
            "email":     self.email,
            "rol":       self.rol,
            "creado_en": self.creado_en.isoformat(),
        }
