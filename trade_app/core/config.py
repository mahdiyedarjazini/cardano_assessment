from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "Cardano Data Enrichment Service"
    API_PREFIX: str = "/api"
    GLEIF_API_URL: str = "https://api.gleif.org/api/v1/lei-records"

    class Config:
        env_file = ".env"


settings = Settings()
