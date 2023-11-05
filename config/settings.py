from pydantic_settings import BaseSettings, SettingsConfigDict


class SiteSettings(BaseSettings):
    HOST: str = "127.0.0.1"
    PORT: int = 5000
    LOOP: str = "asyncio"
    LOG_LEVEL: str = "info"
    RELOAD_DELAY: float = 0.25
    ACCESS_LOG: bool = False

    model_config = SettingsConfigDict(env_prefix="SITE_", env_file=".env")


class AppSettings(BaseSettings):
    TITLE: str = "Unauthorized trade detection"
    DEBUG: bool = True
    SUMMARY: str = "Система видеодетекции объектов нестационарной незаконной торговли"
    VERSION: str = "0.1.0"

    model_config = SettingsConfigDict(env_prefix="APP_", env_file=".env")


class DataBaseSettings(BaseSettings):
    # postgres
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    PORT: int = 5432
    NAME: str = "db_app"
    HOST: str = "localhost"

    DB_URL: str = "psycopg://postgres:postgres@localhost.host:5432/db_app"

    model_config = SettingsConfigDict(env_prefix="DATABASE_", env_file=".env")


class MinioSettings(BaseSettings):
    USER: str
    PASSWORD: str
    HOST: str
    PORT: int = 9000

    model_config = SettingsConfigDict(env_prefix="MINIO_", env_file=".env")


class Settings(BaseSettings):
    APP: AppSettings
    DATABASE: DataBaseSettings
    SITE: SiteSettings
    S3: MinioSettings


settings = Settings(
    APP=AppSettings(),
    DATABASE=DataBaseSettings(),
    SITE=SiteSettings(),
    S3=MinioSettings(),
)
