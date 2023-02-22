import requests
from typing import List
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException, Depends
from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session
import models
import schemas

Base.metadata.create_all(engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class TickerData:
    def __init__(self):
        self.tickers = []

    def add_ticker(self, ticker_name, ticker_price):
        for ticker in self.tickers:
            if ticker['name'] == ticker_name:
                ticker['price'] = ticker_price
                return
        self.tickers.append({'name': ticker_name, 'price': ticker_price})

app = FastAPI(debug=True)
ticker_data = TickerData()



@app.get("/")
async def get_tickers(session: Session = Depends(get_session)):
    all_tickers = session.query(models.Ticker).all()
    return all_tickers


@app.get("/{id}")
async def get_ticker(id: int, session: Session = Depends(get_session)):
    ticker = session.query(models.Ticker).get(id)
    return ticker


@app.post("/")
async def add_ticker(ticker: schemas.TickerCreate, session: Session = Depends(get_session)):
    ticker_obj = session.query(models.Ticker).filter(models.Ticker.name == ticker.name).first()
    if ticker_obj:
        raise HTTPException(status_code=400, detail=f"Sorry, {ticker.name} already exists")
    new_ticker = models.Ticker(name=ticker.name, price=float(ticker.price))
    session.add(new_ticker)
    session.commit()
    session.refresh(new_ticker)
    return new_ticker


@app.get("/get_ticker_data/{ticker}")
async def get_ticker_data(ticker: str) -> str:
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'})
    response = session.get(f'https://finance.yahoo.com/quote/{ticker}')
    if response.status_code != 200:
        return ""
    soup = BeautifulSoup(response.text, "html.parser")
    try:
        price = soup.find("fin-streamer", {"class": "Fw(b) Fz(36px) Mb(-4px) D(ib)"}).text
        print(type(price))
        return price
    except KeyError:
        return ""
    # await get_ticker_data




@app.put("/")
async def update_ticker(ticker_update: schemas.TickerUpdate, session: Session = Depends(get_session)):
    ticker = session.query(models.Ticker).get(ticker_update.id)
    if ticker is None:
        raise HTTPException(status_code=404, detail=f"Ticker with ID {ticker_update.id} not found")
    if ticker_update.name is not None:
        ticker.name = ticker_update.name
    if ticker_update.price is not None:
        ticker.price = ticker_update.price
    session.commit()
    return f"{ticker.name}: ${ticker.price}"



@app.put("/update_tickers")
async def update_tickers(session: Session = Depends(get_session)):
    tickers = session.query(models.Ticker).all()
    for ticker in tickers:
        current_ticker = session.query(models.Ticker).get(ticker.id)
        if current_ticker is None:
            raise HTTPException(status_code=404, detail=f"Ticker with ID {id} not found")
        else:
            price = await get_ticker_data(ticker.name.upper())
            if price:
                current_ticker.price = float(price.replace(",", ""))
            session.commit()
    return "Tickers updated"


@app.delete("/{id}")
async def delete_ticker(id: int, session: Session = Depends(get_session)):
    ticker_obj = session.query(models.Ticker).get(id)
    session.delete(ticker_obj)
    session.commit()
    session.close()
    return f'Ticker {ticker_obj.name} was deleted!'
