from sqlalchemy import Column, Integer, String, Float
from database import Base


class Ticker(Base):
    __tablename__ = 'tickers'
    id = Column(Integer, primary_key=True)
    name = Column(String(256))
    price = Column(Float)

