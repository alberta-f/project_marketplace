from passlib.context import CryptContext


class SecurityService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def hash_paasword(self, password: str) -> str:
        return self.pwd_context.hash(password)


    def verify_password(self, plain:str, hashed: str) -> bool:
        return self.pwd_context.verify(plain, hashed)
