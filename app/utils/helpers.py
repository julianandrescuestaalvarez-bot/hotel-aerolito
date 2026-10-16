from datetime import date

def calcular_total(precio_noche: float, fecha_checkin: date, fecha_checkout: date, servicios: list) -> float:
    """Calcula el total de una reserva incluyendo servicios."""
    noches = (fecha_checkout - fecha_checkin).days
    if noches <= 0:
        raise ValueError("La fecha de checkout debe ser posterior al checkin.")
    
    total_habitacion = precio_noche * noches
    total_servicios  = sum(float(s.precio) for s in servicios)
    iva              = (total_habitacion + total_servicios) * 0.19
    
    return round(total_habitacion + total_servicios + iva, 2)
