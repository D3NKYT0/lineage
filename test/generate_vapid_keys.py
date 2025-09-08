from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
import base64

# Gera a chave privada EC (prime256v1)
private_key = ec.generate_private_key(ec.SECP256R1())

# Serializa a chave privada para bytes
private_bytes = private_key.private_numbers().private_value.to_bytes(32, 'big')
private_key_b64 = base64.urlsafe_b64encode(private_bytes).rstrip(b'=').decode('utf-8')

# Gera a chave pública correspondente
public_key = private_key.public_key()
public_numbers = public_key.public_numbers()
x = public_numbers.x.to_bytes(32, 'big')
y = public_numbers.y.to_bytes(32, 'big')
public_bytes = b'\x04' + x + y  # Uncompressed point
public_key_b64 = base64.urlsafe_b64encode(public_bytes).rstrip(b'=').decode('utf-8')

print("VAPID Public Key:", public_key_b64)
print("VAPID Private Key:", private_key_b64)