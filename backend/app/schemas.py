# backend/app/schemas.py
from pydantic import BaseModel

class IngestResponse(BaseModel):
    message: str
    filename: str
    chunks_added: int

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str