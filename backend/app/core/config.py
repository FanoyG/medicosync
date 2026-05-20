from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    # App Settings
    PROJECT_NAME: str = "MedicoSync"
    
    # Database
    DATABASE_URL: str = Field(alias="DATABASE_URL", description="Alembic Connection")  # e.g., Alembic 
    DB_CONNECTION: str = Field(alias="DB_CONNECTION", description="Fastapi Connection") # e.g., "postgresql://user:password@localhost/medicosync"
    
    # Security
    SECRET_KEY: str = Field(alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    MAX_VERIFY_ATTEMPTS: int = 3
    
    # AWS S3 (Using Minio for now)
    S3_BUCKET: str = Field(alias="AWS_BUCKET_NAME")
    AWS_ACCESS_KEY: str = Field(alias="AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY: str = Field(alias="AWS_SECRET_ACCESS_KEY")
    AWS_REGION: str = Field(alias="AWS_REGION")
    AWS_ENDPOINT_URL: str = Field(alias="AWS_ENDPOINT_URL")

    model_config = SettingsConfigDict(env_file=ENV_PATH, extra="ignore")

settings = Settings() #type: ignore
