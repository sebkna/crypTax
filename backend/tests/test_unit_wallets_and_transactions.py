# backend/tests/test_unit_wallets_and_transactions.py
import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------
# --- Wallet Tests ---
# ---------------------------------------------------

def test_create_wallet(client: TestClient):
    """Erstelle eine neue Wallet"""
    response = client.post("/wallets?address=0xTESTADDR")
    assert response.status_code in [200, 201], response.text
    data = response.json()
    assert data["address"] == "0xTESTADDR"
    assert "id" in data

def test_create_duplicate_wallet(client: TestClient):
    """Versuche eine Wallet doppelt zu erstellen"""
    client.post("/wallets?address=0xDUPLICATE")
    response = client.post("/wallets?address=0xDUPLICATE")
    assert response.status_code == 400

def test_create_wallet_missing_address(client: TestClient):
    """Fehlende Adresse -> Validation Error"""
    response = client.post("/wallets")
    assert response.status_code == 422

def test_get_wallets(client: TestClient):
    """Hole alle Wallets"""
    client.post("/wallets?address=0xGETTEST1")
    client.post("/wallets?address=0xGETTEST2")
    response = client.get("/wallets")
    assert response.status_code == 200
    data = response.json()
    assert any(w["address"] == "0xGETTEST1" for w in data)
    assert any(w["address"] == "0xGETTEST2" for w in data)

# ---------------------------------------------------
# --- Transaction Tests (angepasst auf Query-Parameter) ---
# ---------------------------------------------------

def test_create_transaction(client: TestClient):
    """Erstelle eine gültige Transaction via Query-Parameter"""
    response_wallet = client.post("/wallets?address=0xWALLET1")
    wallet_id = response_wallet.json()["id"]

    response_tx = client.post(
        f"/transactions?wallet_id={wallet_id}&token=BTC&amount=0.5&type=buy&price_usd=30000.0"
    )
    assert response_tx.status_code in [200, 201]
    data = response_tx.json()
    assert data["wallet_id"] == wallet_id
    assert data["token"] == "BTC"
    assert data["amount"] == 0.5


def test_create_transaction_invalid_wallet(client: TestClient):
    """Transaction mit ungültiger Wallet-ID via Query-Parameter"""
    response = client.post(
        "/transactions?wallet_id=9999&token=ETH&amount=1.0&type=buy&price_usd=1800.0"
    )
    # Wallet existiert nicht → Endpunkt gibt 404 zurück
    assert response.status_code == 404

def test_create_transaction_negative_amount(client: TestClient):
    """Transaction mit negativem Betrag -> 422"""
    response_wallet = client.post("/wallets?address=0xWALLET2")
    wallet_id = response_wallet.json()["id"]

    response = client.post(
        f"/transactions?wallet_id={wallet_id}&token=ETH&amount=-5.0&type=buy&price_usd=1800.0"
    )
    assert response.status_code == 422


def test_create_transaction_zero_amount(client: TestClient):
    """Transaction mit 0 Betrag -> 422"""
    response_wallet = client.post("/wallets?address=0xWALLET3")
    wallet_id = response_wallet.json()["id"]

    response = client.post(
        f"/transactions?wallet_id={wallet_id}&token=ETH&amount=0.0&type=buy&price_usd=1800.0"
    )
    assert response.status_code == 422


def test_transaction_invalid_type(client: TestClient):
    """Transaction mit falschem Typ -> 422"""
    response_wallet = client.post("/wallets?address=0xWALLET4")
    wallet_id = response_wallet.json()["id"]

    response = client.post(
        f"/transactions?wallet_id={wallet_id}&token=ETH&amount=1.0&type=invalid_type&price_usd=1800.0"
    )
    assert response.status_code == 422


def test_get_transactions(client: TestClient):
    """Hole alle Transactions"""
    response_wallet = client.post("/wallets?address=0xWALLET5")
    wallet_id = response_wallet.json()["id"]

    # Zwei Transactions erstellen
    client.post(
        f"/transactions?wallet_id={wallet_id}&token=ETH&amount=2.0&type=buy&price_usd=1800.0"
    )
    client.post(
        f"/transactions?wallet_id={wallet_id}&token=BTC&amount=0.1&type=sell&price_usd=35000.0"
    )

    # GET Transactions prüfen
    response = client.get("/transactions")
    assert response.status_code == 200
    data = response.json()
    assert any(tx["wallet_id"] == wallet_id and tx["token"] == "ETH" for tx in data)
    assert any(tx["wallet_id"] == wallet_id and tx["token"] == "BTC" for tx in data)


def test_transaction_missing_fields(client: TestClient):
    """Transaction ohne Pflichtfelder -> 422"""
    response = client.post("/transactions")
    assert response.status_code == 422
