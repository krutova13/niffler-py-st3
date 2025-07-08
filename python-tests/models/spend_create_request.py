from pydantic import BaseModel


class SpendRequest(BaseModel):
    amount: str
    currency: str
    spendDate: str
    category: dict[str, str]
    description: str = ""
