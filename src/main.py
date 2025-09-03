from fastapi import FastAPI
from typing import Dict
from client_albert import ClientAlbert

app: FastAPI = FastAPI()


@app.get("/health")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}
