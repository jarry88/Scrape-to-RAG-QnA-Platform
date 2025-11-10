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

            print("✅ RAG components initialized successfully inside the pipeline object.")
            return True
        except Exception:
            print("--- DETAILED STARTUP ERROR (RAGPipeline) ---")
            traceback.print_exc()
            print("--- END DETAILED STARTUP ERROR ---")
            return False