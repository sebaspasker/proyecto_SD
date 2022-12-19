from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding


def create_rsa_key():
    """
    Create RSA key.
    Returns private_key, public_key
    """

    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )

    public_key = private_key.public_key()

    return private_key, public_key


def get_private_key_bytes(private_key):
    """
    Get RSA private key in bytes.
    """
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def get_public_key_bytes(public_key):
    """
    Get RSA public key in bytes.
    """
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def read_private_key_bytes(private_key):
    return serialization.load_pem_private_key(
        private_key, password=None, backend=default_backend()
    )


def read_public_key_bytes(public_key):
    return serialization.load_pem_public_key(public_key, backend=default_backend())


def encrypt(public_key, message):
    return public_key.encrypt(
        message.encode("UTF-8"),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def decrypt(private_key, message):
    return private_key.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
