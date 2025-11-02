from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.models import Wallet, Transaction
from app.services.db import SessionLocal, init_db

app = FastAPI(title="Crypto Tax API")
init_db()  # Tabellen erstellen

# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Wallet Endpunkte ---
@app.post("/wallets")
def create_wallet(address: str, db: Session = Depends(get_db)):
    db_wallet = db.query(Wallet).filter(Wallet.address == address).first()
    if db_wallet:
        raise HTTPException(status_code=400, detail="Wallet existiert bereits")
    new_wallet = Wallet(address=address)
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet

@app.get("/wallets")
def get_wallets(db: Session = Depends(get_db)):
    return db.query(Wallet).all()

# --- Transaction Endpunkte ---
@app.post("/transactions")
def create_transaction(wallet_id: int, token: str, amount: float, type: str, price_usd: float, db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")
    if amount <= 0:
        raise HTTPException(status_code=422, detail="Amount must be positive")
    if type not in ["buy", "sell"]:
        raise HTTPException(status_code=422, detail="Invalid transaction type")
    
    transaction = Transaction(wallet_id=wallet_id, token=token, amount=amount, type=type, price_usd=price_usd)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.get("/transactions")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()
