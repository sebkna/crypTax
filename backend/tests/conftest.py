# backend/tests/conftest.py
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.models.models import Base
from app.config import DATABASE_URL


# --- Engine & Session (gemeinsam für alle Tests) ---
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- Setup & Teardown ---
@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Erstelle einmalig Tabellen für Tests und entferne sie am Ende"""
    print(f"\n🧩 Using test database: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    print("🧹 Test database cleaned up.")


# --- Dependency Override ---
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override die App-Dependency
app.dependency_overrides[get_db] = override_get_db


# --- Client Fixture ---
@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
