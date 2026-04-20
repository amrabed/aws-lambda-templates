from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    service_name: str = Field(description="Powertools service name", default="${name}")
    metrics_namespace: str = Field(description="Powertools metrics namespace", default="${camel_name}")
