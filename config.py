from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_prefix='SMTP_')

    account_email: str
    account_password: SecretStr

    target_email: str

    provider_domain: str
    provider_port: int

settings = Settings()