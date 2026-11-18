"""
Application configuration for ASHA Saathi.
Manages environment variables, Gnani API settings, and security policies.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./asha_saathi.db"

    # Gnani API Credentials
    GNANI_API_KEY: str = Field(default="", description="Gnani Prisma / Timbre API key")
    GNANI_TOKEN: str = Field(default="", description="Gnani Auth Token")
    GNANI_PRISMA_WS_URL: str = "wss://api.gnani.ai/v1/prisma/stream"
    GNANI_TIMBRE_TTS_URL: str = "https://api.gnani.ai/v1/timbre/synthesize"

    # Voice & Language
    DEFAULT_LANGUAGE: str = "hi-IN-codemix"
    SUPPORTED_LANGUAGES: List[str] = [
        "hi-IN-codemix",
        "en-IN",
        "ta-IN-codemix",
        "te-IN-codemix",
        "mr-IN-codemix"
    ]

    # Responsible AI & Compliance
    DISCLOSE_AI_IDENTITY: bool = True
    RETAIN_AUDIO: bool = False
    ENCRYPT_TRANSCRIPTS: bool = True
    SESSION_ENCRYPTION_KEY: str = "asha-saathi-synthetic-dev-key-32chars"

    # Official Healthcare Keyterms for Gnani STT keyterm prompting
    HEALTHCARE_KEYTERMS: List[str] = [
        "ANC", "PNC", "HBNC", "IFA goli", "TT injection", "Tetanus Toxoid",
        "Pentavalent", "BCG", "OPV", "Rotavirus", "MR vaccine", "PCV",
        "Vitamin A", "Albendazole", "Calcium tablet", "Hemoglobin",
        "BP", "Blood Pressure", "KMC", "Kangaroo Mother Care",
        "Wajan", "Weight", "Sachan wajan", "Garam bukhar", "High fever",
        "Khoon aana", "Bleeding", "Pasli chalna", "Chest indrawing",
        "Doodh peena", "Breastfeeding", "Jhatke aana", "Convulsions",
        "Sust", "Lethargic", "PHC", "CHC", "Sub-centre", "Anganwadi"
    ]

    @property
    def is_gnani_configured(self) -> bool:
        """Checks if real Gnani API credentials are provided."""
        return bool(self.GNANI_API_KEY and self.GNANI_API_KEY.strip())


settings = Settings()
