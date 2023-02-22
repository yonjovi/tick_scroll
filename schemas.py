from typing import Optional
from pydantic import BaseModel


class TickerBase(BaseModel):
    name: str
    price: float


class TickerCreate(TickerBase):
    pass


class Ticker(TickerBase):
    id: int

    class Config:
        orm_mode = True


class TickerUpdate(BaseModel):
    id: int
    name: Optional[str]
    price: Optional[float]
