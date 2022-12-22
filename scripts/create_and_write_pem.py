import sys, os

sys.path.append("./")

from src.utils.assymetric_encryption import *

private_key, public_key = create_rsa_key()

private_key_pem = get_private_key_bytes(private_key)

with open("./pem/private_key_player.pem", "wb") as f:
    f.write(private_key_pem)
