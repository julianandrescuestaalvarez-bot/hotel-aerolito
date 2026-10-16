"""
Script para crear las tablas y cargar datos de prueba.
Ejecutar UNA sola vez: python init_db.py
"""
from app import create_app, db
from app.models.usuario    import Usuario
from app.models.habitacion import Habitacion
from app.models.servicio   import Servicio

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tablas creadas.")

    # --- Usuarios de prueba ---
    if not Usuario.query.first():
        admin = Usuario(nombre="Administrador", email="admin@hotelaerolito.com", rol="admin")
        admin.set_contraseña("admin123")

        recep = Usuario(nombre="Recepcionista Demo", email="recep@hotelaerolito.com", rol="recepcionista")
        recep.set_contraseña("recep123")

        huesped = Usuario(nombre="Juan Pérez", email="juan@email.com", rol="huesped")
        huesped.set_contraseña("huesped123")

        db.session.add_all([admin, recep, huesped])
        print("✅ Usuarios de prueba creados.")

    # --- Habitaciones ---
    if not Habitacion.query.first():
        habitaciones = [
            Habitacion(numero="101", tipo="sencilla",  precio_noche=120000, capacidad=1, descripcion="Habitación sencilla con vista al jardín."),
            Habitacion(numero="102", tipo="sencilla",  precio_noche=120000, capacidad=1, descripcion="Habitación sencilla con baño privado."),
            Habitacion(numero="201", tipo="doble",     precio_noche=180000, capacidad=2, descripcion="Habitación doble con cama matrimonial."),
            Habitacion(numero="202", tipo="doble",     precio_noche=180000, capacidad=2, descripcion="Habitación doble con dos camas."),
            Habitacion(numero="301", tipo="suite",     precio_noche=350000, capacidad=2, descripcion="Suite ejecutiva con sala y jacuzzi."),
            Habitacion(numero="302", tipo="suite",     precio_noche=350000, capacidad=3, descripcion="Suite premium con vista panorámica."),
            Habitacion(numero="401", tipo="familiar",  precio_noche=280000, capacidad=4, descripcion="Habitación familiar con dos cuartos."),
            Habitacion(numero="402", tipo="familiar",  precio_noche=280000, capacidad=5, descripcion="Habitación familiar grande con zona de juegos."),
        ]
        db.session.add_all(habitaciones)
        print("✅ Habitaciones creadas.")

    # --- Servicios adicionales ---
    if not Servicio.query.first():
        servicios = [
            Servicio(nombre="Desayuno buffet",  descripcion="Desayuno completo incluido por persona.",  precio=25000),
            Servicio(nombre="Spa & Relajación", descripcion="Acceso por un día al spa del hotel.",      precio=80000),
            Servicio(nombre="Parqueadero",      descripcion="Parqueadero cubierto por noche.",           precio=15000),
            Servicio(nombre="Transfer aeropuerto", descripcion="Traslado desde/hacia el aeropuerto.",   precio=60000),
            Servicio(nombre="Room service",     descripcion="Servicio a la habitación 24/7.",            precio=20000),
        ]
        db.session.add_all(servicios)
        print("✅ Servicios creados.")

    db.session.commit()
    print("\n🎉 Base de datos lista. Puedes iniciar el servidor con: python run.py")
