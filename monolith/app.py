"""Monolito: lógica de negocio de la lista de llegadas, persistida en MongoDB."""

import os
from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel
from pymongo import DESCENDING, MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/arrivals")

# MongoClient conecta de forma perezosa, así que la app arranca aunque Mongo aún no esté listo.
# tz_aware=True: Mongo guarda UTC; sin esto las fechas leídas salen sin zona y el navegador las desfasa.
client = MongoClient(MONGO_URI, tz_aware=True)
arrivals = client.get_default_database()["arrivals"]

app = FastAPI(title="Arrivals Monolith")


class ArrivalIn(BaseModel):
    name: str


class Arrival(BaseModel):
    id: str
    name: str
    timestamp: datetime


def to_arrival(doc: dict) -> Arrival:
    return Arrival(id=str(doc["_id"]), name=doc["name"], timestamp=doc["timestamp"])


@app.post("/arrivals", response_model=Arrival, status_code=201)
def create_arrival(data: ArrivalIn):
    # La hora de llegada la fija el servidor, no el cliente.
    doc = {"name": data.name, "timestamp": datetime.now(timezone.utc)}
    result = arrivals.insert_one(doc)
    doc["_id"] = result.inserted_id
    return to_arrival(doc)


@app.get("/arrivals", response_model=list[Arrival])
def list_arrivals():
    return [to_arrival(doc) for doc in arrivals.find().sort("timestamp", DESCENDING)]
