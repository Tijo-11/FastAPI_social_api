from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class GlobalConfig(BaseSettings):
    app_name: str = Field(default="Awesome API")
    admin_email: str
    items_per_user: int = Field(default=50)
    database_url: Optional[str] = None
    db_force_rollback: bool = Field(default=False)
    env_state: Optional[Literal["development", "testing", "production"]] = (
        None  # Removed env="ENV_STATE"
    )
    # Add secret settings
    SECRET_KEY: str
    ALGORITHM: str

    # Add maigun
    DEV_MAILGUN_API_KEY: Optional[str] = None
    DEV_MAILGUN_DOMAIN: Optional[str] = None

    ##file handling
    B2_KEY_ID: Optional[str] = None
    B2_APPLICATION_KEY: Optional[str] = None
    B2_BUCKET_NAME: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow",  # Allow extra fields
        env_prefix="",  # No prefix for global config
        # Map ENV_STATE environment variable to env_state field
        env_nested_delimiter="__",
        # Optionally, you can specify custom environment variable names
        # but here we rely on the field name matching ENV_STATE
    )


class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="DEV_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


class TestConfig(GlobalConfig):
    database_url: str = "sqlite:///test.db"
    db_force_rollback: bool = True

    model_config = SettingsConfigDict(
        env_prefix="TEST_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(
        env_prefix="PROD_",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
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
