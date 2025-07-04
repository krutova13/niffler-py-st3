from typing import Dict

from pydantic import BaseModel


class SpendRequest(BaseModel):
    amount: str
    currency: str
    spendDate: str
    category: Dict[str, str]
    description: str = ""
