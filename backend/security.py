import hashlib
import hmac
import secrets

# Matches the seed database's existing hash format exactly (verified against
# the seeded test@campuscustoms.yale.edu / "password" row): pbkdf2_hmac with
# sha256, 120_000 iterations, a per-user random salt, format
# "pbkdf2_sha256$<salt>$<hex digest>".
_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 120_000


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS).hex()
    return f"{_ALGORITHM}${salt}${digest}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, salt, digest = stored_hash.split("$")
    except ValueError:
        return False
    if algorithm != _ALGORITHM:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERATIONS).hex()
    return hmac.compare_digest(candidate, digest)
