from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env')

    account_email: str
    account_password: str

    target_email: str

    provider_domain: str
    provider_port: int

settings = Settings()