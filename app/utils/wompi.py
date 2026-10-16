import os
import hashlib
import requests

WOMPI_PUBLIC_KEY       = os.getenv("WOMPI_PUBLIC_KEY")
WOMPI_INTEGRITY_SECRET = os.getenv("WOMPI_INTEGRITY_SECRET")
WOMPI_API_BASE         = "https://sandbox.wompi.co/v1"  # cuando pases a producción: https://production.wompi.co/v1


def generar_firma_integridad(referencia, monto_en_centavos, moneda="COP"):
    """
    Wompi exige un hash SHA256 de: referencia + monto_en_centavos + moneda + secreto_de_integridad
    Esto evita que alguien manipule el monto desde el navegador antes de abrir el widget.
    """
    cadena = f"{referencia}{monto_en_centavos}{moneda}{WOMPI_INTEGRITY_SECRET}"
    return hashlib.sha256(cadena.encode("utf-8")).hexdigest()


def consultar_transaccion(transaccion_id):
    """
    Consulta el estado REAL de una transacción directamente en la API de Wompi.
    Nunca confiamos en el estado que reporta el frontend: el frontend puede ser manipulado,
    esta consulta al servidor de Wompi es la única fuente de verdad.
    """
    resp = requests.get(f"{WOMPI_API_BASE}/transactions/{transaccion_id}")
    resp.raise_for_status()
    return resp.json()["data"]