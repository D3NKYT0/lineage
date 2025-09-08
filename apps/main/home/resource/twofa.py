import pyotp
import qrcode
import base64
from io import BytesIO
from django.conf import settings
from utils.protocol import create_protocol


def gerar_qr_png(email, secret):
    protocol = create_protocol()
    issuer = f"PDL: {settings.PROJECT_TITLE} - {protocol}"
    
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)
    
    # Gerar o QR Code
    img = qrcode.make(uri)
    
    # Salvar como PNG em um arquivo binário
    stream = BytesIO()
    img.save(stream, format='PNG')
    
    # Converter para base64
    img_base64 = base64.b64encode(stream.getvalue()).decode('utf-8')
    
    return img_base64
