from fastapi import FastAPI, Depends
from typing import Dict, Any

app: FastAPI = FastAPI()


@app.get("/health")
def route_sante() -> Dict[str, str]:
    return {"status": "ok"}
