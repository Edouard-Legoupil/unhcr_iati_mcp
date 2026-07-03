from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    iati_api_key: str

    iati_base_url: str = (
        "https://api.iatistandard.org/datastore"
    )

    unhcr_publisher_ref: str = (
        "XM-DAC-41121"
    )

    timeout_seconds: int = 120

    page_size: int = 1000

    class Config:
        env_file = ".env"


settings = Settings()