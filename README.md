# Scrape-to-RAG-QnA-Platform

## 💡 Project Summary

This project implements a complete **Scrape-to-RAG** workflow, transforming unstructured multi-source data (web pages, emails) into an intelligent, queryable knowledge base.

It serves as a full-stack platform, utilizing a local **Ollama** Large Language Model (LLM) for high-quality, context-aware Q&A generation, orchestrated by **n8n** for robust data collection and process automation.

## 🚀 Key Technological Focus

| Layer | Technology | Role in Project |
| :--- | :--- | :--- |
| **Data Flow & Scheduling** | **n8n** | Handles multi-source data collection scheduling, incremental updates, and error alerting. |
| **API & RAG Core** | **Python / FastAPI** | High-performance API layer for the RAG engine, document chunking, vector management, and semantic retrieval. |
| **Local LLM** | **Ollama** | Provides the Generative Model for grounded, citation-backed answers. |
| **Data Storage** | **ChromaDB** | Local Vector Database for the knowledge base. |
| **Containerization** | **Docker Compose** | Manages the entire stack (FastAPI, Ollama, n8n) for easy setup and consistency. |

## 🛠️ Getting Started (Local Setup)

This project is designed to run locally using Docker Compose.

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/ja/Scrape-to-RAG-QnA-Platform.git](https://github.com/jarry88/Scrape-to-RAG-QnA-Platform.git)
    cd Scrape-to-RAG-QnA-Platform
    ```s
2.  **Configure Environment:**
    * Copy the `.env.example` to `.env` and fill in necessary configurations.
    * Create the persistent data directories: `mkdir -p data/chromadb data/n8n`
3.  **Build and Run Services:**
    ```bash
    docker-compose up --build -d
    ```
    * *(Note: This command will build the FastAPI backend, pull the n8n and Ollama images, and start all services.)*
4.  **Access:**
    * **FastAPI Backend:** Check the port defined in `docker-compose.yml`.
    * **n8n Workflow UI:** Access via the configured port (e.g., `http://localhost:5678`).

---

**Next Step:** 
填充 `docker-compose.yml` 文件，這是整個項目集成的核心。