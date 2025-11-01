from fastapi import FastAPI

app = FastAPI(title="Crypto Tax API")

@app.get("/")
def root():
    return {"message": "Crypto Tax API läuft 🚀"}
