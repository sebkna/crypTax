from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, unique=True, index=True)
    user_name = Column(String, nullable=True)
    transactions = relationship("Transaction", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id"))
    token = Column(String)
    amount = Column(Float)
    type = Column(String)  # buy / sell
    date = Column(DateTime, default=datetime.utcnow)
    price_usd = Column(Float)
    wallet = relationship("Wallet", back_populates="transactions")
