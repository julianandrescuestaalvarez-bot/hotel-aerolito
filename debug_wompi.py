import os
from dotenv import load_dotenv
load_dotenv()

from app.utils.wompi import generar_firma_integridad, WOMPI_PUBLIC_KEY
import requests

referencia = "TEST-DEBUG-001"
monto      = 100000
moneda     = "COP"
firma      = generar_firma_integridad(referencia, monto, moneda)

print("Llave publica:", WOMPI_PUBLIC_KEY)
print("Firma generada:", firma)

url = "https://checkout.wompi.co/p/"
params = {
    "public-key": WOMPI_PUBLIC_KEY,
    "currency": moneda,
    "amount-in-cents": monto,
    "reference": referencia,
    "signature:integrity": firma,
    "redirect-url": "http://127.0.0.1:5500/frontend/confirmacionReserva.html",
}

resp = requests.get(url, params=params)
print("STATUS:", resp.status_code)
print("BODY:")
print(resp.text[:3000])