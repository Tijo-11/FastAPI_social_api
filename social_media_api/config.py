# config.py
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalConfig(BaseSettings):
    app_name: str = Field(default="Awesome API")
    admin_email: str
    items_per_user: int = Field(default=50)
    database_url: Optional[str] = None
    db_force_rollback: bool = Field(default=False)
    env_state: Optional[Literal["development", "testing", "production"]] = Field(
        default=None, env="ENV_STATE"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra fields
    )


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="DEV_", env_file=".env", env_file_encoding="utf-8"
    )


class TestConfig(GlobalConfig):
    database_url: str = "sqlite:///test.db"
    db_force_rollback: bool = True

    model_config = SettingsConfigDict(
        env_prefix="TEST_", env_file=".env", env_file_encoding="utf-8"
    )


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="PROD_", env_file=".env", env_file_encoding="utf-8"
    )


def get_settings() -> GlobalConfig:
    config = GlobalConfig()
    print(f"ENV_STATE: {config.env_state}")
    print(f"GlobalConfig admin_email: {config.admin_email}")
    if config.env_state == "development":
        dev_config = DevConfig()
        print(f"DevConfig database_url: {dev_config.database_url}")
        return dev_config
    elif config.env_state == "testing":
        return TestConfig()
    elif config.env_state == "production":
        return ProdConfig()
    else:
        print("Falling back to GlobalConfig")
        return config


settings = get_settings()
print(
    f"Final settings: admin_email={settings.admin_email}, database_url={settings.database_url}"
)
