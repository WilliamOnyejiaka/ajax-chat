import bcrypt

def hash_password(password: str) -> bytes:
    # Encode the password to bytes and generate a salted hash
    salt = bcrypt.gensalt()  # Default rounds=12
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password)
