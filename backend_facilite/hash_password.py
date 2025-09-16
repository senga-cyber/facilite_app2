# hash_password.py
from passlib.context import CryptContext
import sys
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(plain: str) -> str:
    return pwd_ctx.hash(plain)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hash_password.py <mot_de_passe_clair>")
        sys.exit(1)
    plain = sys.argv[1]
    print(hash_password(plain))
# generate_hash.py
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

password = "charsie2"
hashed = pwd_context.hash(password)
print(hashed)
