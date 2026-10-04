"""API Gateway (fachada): sirve el front-end, valida las peticiones y las reenvía al monolito."""

import os
from pathlib import Path
from typing import Annotated

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, StringConstraints

MONOLITH_URL = os.getenv("MONOLITH_URL", "http://localhost:8081")
INDEX_HTML = Path(__file__).parent / "static" / "index.html"

app = FastAPI(title="Arrivals API Gateway")


class ArrivalIn(BaseModel):
    # Validación del gateway: nombre obligatorio, sin espacios sobrantes, máx. 100 caracteres.
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=100)]


async def forward(method: str, path: str, json: dict | None = None):
    try:
        async with httpx.AsyncClient(base_url=MONOLITH_URL, timeout=5) as client:
            response = await client.request(method, path, json=json)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=502, detail=f"Monolith unreachable: {exc}") from exc
    if response.is_error:
        raise HTTPException(status_code=502, detail=f"Monolith error {response.status_code}")
    return response.json()


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(INDEX_HTML)


@app.post("/api/arrivals", status_code=201)
async def create_arrival(data: ArrivalIn):
    return await forward("POST", "/arrivals", json=data.model_dump())


@app.get("/api/arrivals")
async def list_arrivals():
    return await forward("GET", "/arrivals")
