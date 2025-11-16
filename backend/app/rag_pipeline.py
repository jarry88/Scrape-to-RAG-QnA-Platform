# backend/app/rag_pipeline.py

import traceback
import chromadb
from langchain_community.vectorstores import Chroma
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from settings import settings # Import our settings instance
import time

class RAGPipeline:
    """A class to hold all the components and logic of the RAG pipeline."""
    def __init__(self):
        self.vector_store = None
        self.retrieval_chain = None
        print("RAGPipeline object created. Components are not yet initialized.")

    def initialize(self):
        """
        Initializes all RAG components. 
        This includes connecting to ChromaDB, setting up the embedding model,
        the LLM, and constructing the final retrieval chain.
        Returns True on success, False on failure.
        """
        try:
            # 1. Initialize ChromaDB client and Embedding Function
            chroma_client = chromadb.HttpClient(host=settings.chroma_db_host, port=settings.chroma_db_port)
            chroma_client.heartbeat() # A lightweight check to see if the server is responsive
            embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
            
            # 2. Initialize Vector Store
            self.vector_store = Chroma(
                client=chroma_client,
                collection_name="rag_collection",
                embedding_function=embedding_function,
            )
            
            # 3. Initialize LLM
            llm = ChatOllama(base_url=settings.ollama_base_url, model="qwen:0.5b")

            # 4. Create the Retrieval Chain (this is a performance optimization)
            # This chain is pre-built at startup to be ready for requests.
            prompt = ChatPromptTemplate.from_template("""
            Answer the following question based only on the provided context:
            <context>{context}</context>
            Question: {input}
            """)
            retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
            document_chain = create_stuff_documents_chain(llm, prompt)
            self.retrieval_chain = create_retrieval_chain(retriever, document_chain)

            print("✅ On-demand initialization successful.")
            return True
        except Exception as e:
            print("--- DETAILED STARTUP ERROR (RAGPipeline) ---")
            print(f"🚨 On-demand initialization FAILED: {e}")
            traceback.print_exc()
            print("--- END DETAILED STARTUP ERROR ---")
            return False
    
    # =========================================================================
# THE SINGLETON PATTERN: Create and initialize a single, global instance
# =========================================================================
def get_rag_pipeline():
    """
    This function manages the single, global instance of the RAG pipeline.
    It runs the resilient initialization loop ONCE and then returns the instance.
    """
    global _rag_pipeline_instance
    # Check if the instance has already been created
    if _rag_pipeline_instance is None:
        print("--- Initializing Singleton RAG Pipeline ---")
        _rag_pipeline_instance = RAGPipeline()
        
        # Resilient Initialization Loop
        MAX_RETRIES = 10
        RETRY_DELAY = 5
        for i in range(MAX_RETRIES):
            if _rag_pipeline_instance.initialize():
                print("--- Singleton RAG Pipeline is READY ---")
                break # Success
            if i < MAX_RETRIES - 1:
                print(f"Retrying initialization in {RETRY_DELAY} seconds...")
                time.sleep(RETRY_DELAY)
        else: # This 'else' belongs to the 'for' loop, it runs if the loop finishes without a 'break'
            print("🚨 FATAL: Could not initialize RAG pipeline after all retries.")
            # We will leave the instance created but uninitialized
    
    return _rag_pipeline_instance

# Initialize the global variable to None when the module is first loaded
_rag_pipeline_instance = None