import os
from fastapi import FastAPI
from pydantic import BaseModel
from .faiss_store import FaissStore

app = FastAPI(title="vectorstore_service")

DATA_DIR = os.getenv("VECTORSTORE_DATA_DIR", "/data")
MODEL = os.getenv("VECTORSTORE_MODEL", "all-MiniLM-L6-v2")
store = FaissStore(DATA_DIR, MODEL)


class UpsertReq(BaseModel):
    id: str
    text: str


class SearchReq(BaseModel):
    text: str
    k: int = 5
    include_text: bool = True


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/upsert")
def upsert(req: UpsertReq):
    store.upsert(req.id, req.text)
    return {"status": "ok"}


@app.post("/search")
def search(req: SearchReq):
    return {"results": store.search(req.text, req.k, include_text=req.include_text)}
