from urllib.parse import quote_plus
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configuración central de la aplicación cargada desde
    variables de entorno (.env).
    """

    PROJECT_NAME: str = "API Gestión de Transporte"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Parámetros de base de datos MySQL
    DB_USER: str = "root"
    DB_PASSWORD: str = Field(
        ...,
        description="Contraseña obligatoria para la conexión a la base de datos",
    )
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "transporte_db"

    # Flag para controlar si lifespan inicializa tablas (desactivado por Alembic)
    INIT_DB_ON_STARTUP: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    @property
    def database_url(self) -> str:
        """Genera la URL de conexión para SQLAlchemy con el driver PyMySQL."""
        escaped_password = quote_plus(self.DB_PASSWORD)
        return (
            f"mysql+pymysql://{self.DB_USER}:{escaped_password}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
