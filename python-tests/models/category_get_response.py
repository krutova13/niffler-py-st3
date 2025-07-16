from pydantic import BaseModel


class CategoryGetResponse(BaseModel):
    id: str
    name: str
    username: str
    archived: bool
