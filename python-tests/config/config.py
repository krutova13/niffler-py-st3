from pydantic import BaseModel


class Config(BaseModel):
    frontend_url: str
    gateway_url: str
    spend_db_url: str
