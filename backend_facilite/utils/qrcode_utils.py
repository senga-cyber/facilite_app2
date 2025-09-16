# utils/qrcode_utils.py
import os, json, qrcode
from datetime import datetime

QR_DIR = os.path.join("static", "qrcodes")
os.makedirs(QR_DIR, exist_ok=True)

def ensure_tx_code(prefix="TXN"):
    # ex: TXN-20250912-1694549012
    return f"{prefix}-{int(datetime.utcnow().timestamp())}"

def generate_qr_png(data: dict, filename: str) -> str:
    """Génère un QR PNG depuis un dict, retourne le chemin relatif."""
    payload = json.dumps(data, separators=(",", ":"))
    img = qrcode.make(payload)
    path = os.path.join(QR_DIR, filename)
    img.save(path)
    return path  # ex: static/qrcodes/xxx.png
