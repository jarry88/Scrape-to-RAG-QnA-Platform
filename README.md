# Scrape-to-RAG QnA Platform

This project is a complete, end-to-end Question and Answer platform that uses a Retrieval-Augmented Generation (RAG) architecture. It can automatically scrape web content, ingest it into a vector knowledge base, and answer user questions based on the ingested data.

## Features

- **Automated Data Collection:** Uses a Python script with Playwright to scrape web pages.
- **Asynchronous Job Processing:** Leverages Celery and Redis to handle long-running scraping tasks in the background without blocking the API.
- **Workflow Orchestration:** n8n automates the entire pipeline from scheduling the scrape to ingesting the final data.
- **RAG Core:** A FastAPI backend provides API endpoints for ingesting documents (`.pdf`, `.txt`) and querying the knowledge base.
- **Vector Knowledge Base:** Uses ChromaDB for efficient semantic search and retrieval of document chunks.
- **Local LLM Integration:** Powered by Ollama to generate answers based on the retrieved context.
- **Web Interface:** A simple React frontend provides a user-friendly interface for asking questions.

## Architecture Diagram

(We can create a simple text-based diagram here)
`User -> React Frontend -> FastAPI Backend -> RAG Pipeline -> Ollama`
`n8n -> FastAPI Backend -> Celery Worker -> Scraper -> FastAPI Backend`

## Tech Stack

- **Backend:** Python, FastAPI, LangChain
- **Frontend:** JavaScript, React
- **AI:** Ollama, ChromaDB, Sentence-Transformers
- **Automation & Job Queue:** n8n, Celery, Redis
- **Web Scraping:** Playwright
- **Containerization:** Docker, Docker Compose

## Getting Started

### Prerequisites

- Docker and Docker Compose
- An `.env` file in the project root (see `.env.example`)

### Setup

1.  **Create the Environment File:**
    Copy the `.env.example` file to `.env` and fill in the necessary values (e.g., for the scraper).

    ```bash
    cp .env.example .env
    ```

2.  **Build and Start Services:**
    Run the following command to build all the images and start the containerized services.

    ```bash
    docker-compose up -d --build
    ```

3.  **Download an LLM Model:**
    After the services are running, you need to pull a model for Ollama to use.

    ```bash
    docker-compose exec ollama ollama run qwen:0.5b
    ```

### Usage

- **Web Interface:** Open `http://localhost:3000`
- **API Documentation:** Open `http://localhost:8000/docs`
- **Automation Workflows:** Open `http://localhost:5678`

## How to Use the Pipeline

1.  **Ingest Data Manually:** Use the `/docs` page to call the `/ingest` endpoint and upload a PDF or TXT file.
2.  **Ingest Data Automatically:**
    - Go to the n8n interface at `http://localhost:5678`.
    - Configure and activate the "Scrape and Ingest" workflow.
    - The workflow will automatically call the `/scrape` API, which runs the scraper, and then calls `/ingest` with the result.
3.  **Ask a Question:** Use the React UI at `http://localhost:3000` to ask a question related to the content you have ingested.

---