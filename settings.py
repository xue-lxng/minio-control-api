from dataclasses import dataclass


@dataclass
class Settings:
    endpoint_url: str
    access_key: str
    secret_key: str
    redis_url: str

    region: str = "us-east-1"
    secure: bool = True
