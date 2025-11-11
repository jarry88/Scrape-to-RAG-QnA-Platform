# backend/app/main.py

# =================================================================================
# 1. IMPORTS
# =================================================================================
import os
import time
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import from our new, separated modules
from settings import settings
from schemas import IngestResponse, QueryRequest, QueryResponse
from rag_pipeline import RAGPipeline

from tasks import run_scraper_task # Import our new task
from pydantic import BaseModel
# =================================================================================
# 2. APP INITIALIZATION & STARTUP EVENT
# =================================================================================
app = FastAPI(
    title="Scrape-to-RAG QnA Platform API",
    description="An API for ingesting documents and answering questions using a RAG pipeline.",
    version="1.0.0"
)

class ScrapeRequest(BaseModel):
    target_url: str
    content_selector: str
    output_filename: str
    login: bool = False

@app.post("/scrape", status_code=202, tags=["Collection"])
async def start_scraping_job(request: ScrapeRequest):
    """
    Accepts a scraping request and starts it as a background job.
    """
    # .delay() sends the task to the Celery worker
    task = run_scraper_task.delay(
        request.target_url,
        request.content_selector,
        request.output_filename,
        request.login
    )
    return {"message": "Scraping job accepted", "task_id": task.id}
@app.on_event("startup")
def startup_event():
    print("--- Application Startup Event ---")
    app.state.rag_pipeline = RAGPipeline()
    
    # Resiliently initialize the pipeline
    MAX_RETRIES = 10
    RETRY_DELAY = 5
    for i in range(MAX_RETRIES):
        print(f"Attempting to initialize RAG pipeline (Attempt {i+1}/{MAX_RETRIES})...")
        if app.state.rag_pipeline.initialize():
            return # Success
        if i < MAX_RETRIES - 1:
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
    
    print("🚨 Could not initialize RAG pipeline after all retries. The application will not be functional.")

# =================================================================================
# 3. API ENDPOINTS
# =================================================================================
@app.post("/ingest", response_model=IngestResponse, tags=["RAG"], summary="Ingest a PDF document")
async def ingest_document(request: Request, file: UploadFile = File(..., description="The PDF file to be ingested.")):
    """
    Ingests a PDF document by splitting it into chunks, creating embeddings,
    and storing them in the vector database.
    """
    rag_pipeline = request.app.state.rag_pipeline
    
    if not rag_pipeline or not rag_pipeline.vector_store:
        raise HTTPException(status_code=503, detail="Vector store is not initialized. Check server logs.")

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    tmp_file_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        loader = PyPDFLoader(tmp_file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        if not chunks:
            raise HTTPException(status_code=400, detail="Could not extract any text chunks from the document.")

        rag_pipeline.vector_store.add_documents(chunks)
        
        return IngestResponse(
            message="Document ingested successfully.",
            filename=file.filename,
            chunks_added=len(chunks)
        )
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

@app.post("/query", response_model=QueryResponse, tags=["RAG"], summary="Query the knowledge base")
async def query_knowledge_base(request: Request, query_req: QueryRequest):
    """
    Receives a query, retrieves relevant context from the vector database,
    and generates an answer using the LLM.
    """

    rag_pipeline = request.app.state.rag_pipeline
    
    if not rag_pipeline or not rag_pipeline.retrieval_chain:
        raise HTTPException(status_code=503, detail="Retrieval chain is not initialized. Check server logs.")

    response = rag_pipeline.retrieval_chain.invoke({"input": query_req.query})
    
    return QueryResponse(answer=response["answer"])

@app.get("/", tags=["General"], summary="Root endpoint")
def read_root():
    """
    A simple root endpoint to confirm the API is running.
    """
    return {"message": "Welcome to the RAG API!"}