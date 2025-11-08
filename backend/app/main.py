# backend/app/main.py

# =================================================================================
# 1. IMPORTS
# =================================================================================
import os
import time
import traceback
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from pydantic_settings import BaseSettings

import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# =================================================================================
# 2. CONFIGURATION & APP INITIALIZATION
# =================================================================================
class Settings(BaseSettings):
    chroma_db_host: str
    chroma_db_port: int
    ollama_base_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
app = FastAPI(title="Scrape-to-RAG QnA Platform API")

# =================================================================================
# 3. STARTUP EVENT
# =================================================================================
@app.on_event("startup")
def startup_event():
    print("--- Application Startup Event ---")
    
    # Initialize state variables directly on app.state
    app.state.vector_store = None
    app.state.retrieval_chain = None
    
    # Resilient Initialization Loop
    MAX_RETRIES = 10
    RETRY_DELAY = 5
    for i in range(MAX_RETRIES):
        try:
            print(f"Attempting to initialize RAG components (Attempt {i+1}/{MAX_RETRIES})...")
            
            chroma_client = chromadb.HttpClient(host=settings.chroma_db_host, port=settings.chroma_db_port)
            chroma_client.heartbeat()
            embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            
            # ATTACH DIRECTLY TO app.state
            app.state.vector_store = Chroma(
                client=chroma_client,
                collection_name="rag_collection",
                embedding_function=embedding_function,
            )
            
            llm = ChatOllama(base_url=settings.ollama_base_url, model="qwen:0.5b")

            prompt = ChatPromptTemplate.from_template("""
            Answer the following question based only on the provided context:
            <context>{context}</context>
            Question: {input}
            """)
            retriever = app.state.vector_store.as_retriever(search_kwargs={"k": 3})
            document_chain = create_stuff_documents_chain(llm, prompt)
            
            # ATTACH DIRECTLY TO app.state
            app.state.retrieval_chain = create_retrieval_chain(retriever, document_chain)
            
            print("✅ RAG components initialized and attached directly to app.state.")
            return # Exit loop on success

        except Exception:
            print("--- DETAILED STARTUP ERROR ---")
            traceback.print_exc()
            print("--- END DETAILED STARTUP ERROR ---")
            if i < MAX_RETRIES - 1:
                print(f"Retrying in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
    
    print("🚨 Could not initialize RAG pipeline after all retries.")

# =================================================================================
# 4. API ENDPOINTS
# =================================================================================
class IngestResponse(BaseModel):
    message: str
    filename: str
    chunks_added: int

@app.post("/ingest", response_model=IngestResponse, tags=["RAG"])
async def ingest_document(request: Request, file: UploadFile = File(...)):
    # Access vector_store directly from the request state
    if not hasattr(request.app.state, 'vector_store') or request.app.state.vector_store is None:
        raise HTTPException(status_code=503, detail="Vector store is not initialized. Please check server logs.")

    vector_store = request.app.state.vector_store
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

        vector_store.add_documents(chunks)
        
        return IngestResponse(
            message="Document ingested successfully.",
            filename=file.filename,
            chunks_added=len(chunks)
        )
    finally:
        if os.path.exists(tmp_file_path):
            os.remove(tmp_file_path)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str

@app.post("/query", response_model=QueryResponse, tags=["RAG"])
async def query_knowledge_base(request: Request, query_req: QueryRequest):
    # Access retrieval_chain directly from the request state
    if not hasattr(request.app.state, 'retrieval_chain') or request.app.state.retrieval_chain is None:
        raise HTTPException(status_code=503, detail="Retrieval chain is not initialized. Please check server logs.")

    response = request.app.state.retrieval_chain.invoke({"input": query_req.query})
    
    return QueryResponse(answer=response["answer"])

@app.get("/", tags=["General"])
def read_root():
    return {"message": "Welcome to the RAG API!"}