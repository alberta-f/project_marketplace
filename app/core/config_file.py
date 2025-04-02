from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class DatabaseConfig(BaseConfig):
    db: str = Field(..., alias="POSTGRES_DB")
    user: str = Field(..., alias="POSTGRES_USER")
    password: SecretStr = Field(..., alias="POSTGRES_PASSWORD")
    host: str = Field(..., alias="POSTGRES_HOST")
    port: int = Field(..., alias="POSTGRES_PORT")

    @property
    def url(self) -> str:
        return f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}@{self.host}:{self.port}/{self.db}"


class MinioConfig(BaseConfig):
    access_key: str = Field(..., alias="MINIO_ROOT_USER")
    secret_key: SecretStr = Field(..., alias="MINIO_ROOT_PASSWORD")
    endpoint: str = Field(..., alias="MINIO_ENDPOINT")
    bucket: str = Field("marketplace", alias="S3_BUCKET")


class SessionConfig(BaseConfig):
    cookie_name: str = Field("session", alias="SESSION_COOKIE_NAME")


class JWTConfig(BaseConfig):
    secret_key: str = Field(..., alias='JWT_SECRET_KEY')
    algorithm: str = Field(..., alias='JWT_ALGORITHM')
    single_use_expire_mins: int = Field(...,
                                    alias='JWT_SINGLE_USE_TOKEN_EXPIRE_MINS')


class RedisConfig(BaseConfig):
    host: str = Field(..., alias='REDIS_HOST')
    port: int = Field(..., alias='REDIS_PORT')
    db: int = Field(..., alias='REDIS_DB')

    @property
    def url(self):
        return f"redis://{self.host}:{self.port}/{self.db}"


class AppConfig(BaseConfig):
    url: str = Field(..., alias='APP_URL')


class RabbitMQSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str

    class Config:
        env_prefix = "RABBITMQ_"


class SMTPSettings(BaseSettings):
    host: str
    port: int
    user: str
    password: str
    from_email: str = "no-reply@example.com"

    class Config:
        env_prefix = 'SMTP_'


class Config(BaseModel):
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    minio: MinioConfig = Field(default_factory=MinioConfig)
    session: SessionConfig = Field(default_factory=SessionConfig)
    jwt: JWTConfig = Field(default_factory=JWTConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    app: AppConfig = Field(default_factory=AppConfig)
    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    smtp: SMTPSettings = Field(default_factory=SMTPSettings)

config = Config()
