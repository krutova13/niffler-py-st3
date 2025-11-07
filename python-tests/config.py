from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    AUTH_URL: str = Field(default="http://auth.niffler.dc:9000")
    FRONTEND_URL: str = Field(default="http://frontend.niffler.dc")
    GATEWAY_URL: str = Field(default="http://gateway.niffler.dc:8090")
    API_BASE_URL: str = Field(default="http://gateway.niffler.dc:8090/swagger-ui")
    TEST_USERNAME: str = Field(default="test")
    TEST_PASSWORD: str = Field(default="123")
    SPEND_DB_URL: str = Field(default="postgresql+psycopg2://postgres:secret@localhost:5432/niffler-spend")
    AUTH_SECRET: str = Field(default="secret")
    USER_DB_URL: str = Field(default="postgresql+psycopg2://postgres:secret@localhost:5432/niffler-userdata")
    KAFKA_ADDRESS: str = Field(default="localhost:9093")
    GRPC_URL: str = Field(default="localhost:8092")

    class ConfigDict:
        env_file = ".env"
        env_file_encoding = "utf-8"
