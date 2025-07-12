# G6PD Deficiency Health Assistant

An AI-powered assistant specialized in answering questions about G6PD deficiency, built with LangChain and FAISS vector database for efficient knowledge retrieval.

## Overview

This project creates a specialized Q&A system that can provide accurate information about G6PD deficiency based on medical documents. It uses:

- LangChain for creating a question-answering chain
- FAISS vector database for efficient document retrieval
- Embedding models to convert text into vector representations
- LLM integration for generating helpful responses

## Project Structure

```
health-assistant/
├── assistant/
│   ├── create_vector_db.py     # Script to create vector database from documents
│   ├── rag.py                 # Main application entry point
│   ├── simple_chain.py         # Simple implementation of LangChain
│   └── utils/
│       ├── pdf_loader.py       # Utility to load and process PDF documents
│       └── llm/
│           ├── embedding.py    # Text embedding initialization
│           └── llm.py          # LLM initialization
├── documents/                  # Source documents about G6PD deficiency
│   └── pdf/                    # PDF documents used for knowledge base
├── vector_db/                  # Vector database storage
│   └── faiss_index/            # FAISS index files
└── requirements.txt            # Project dependencies
```

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/leducanh95/health-assistant.git
   cd health-assistant
   ```
2. Create a Conda environment with Python 3.11 and install dependencies:
    ```
    conda create -n health-assistant python=3.11
    conda activate health-assistant
    pip install -r requirements.txt
    ```

3. Create a `.env` file with the following variables:
   ```
   VECTOR_DB_PATH=./vector_db/faiss_index
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Usage

### Creating the Vector Database

Before using the assistant, you need to create the vector database from your documents:

```
python assistant/create_vector_db.py
```

### Running the Assistant

To run the assistant with a default question:

```
python assistant/rag.py
```

## About G6PD Deficiency

G6PD (Glucose-6-phosphate dehydrogenase) deficiency is a genetic disorder that affects red blood cells. The assistant is designed to provide information on:

- Causes and symptoms of G6PD deficiency
- Diagnosis and treatment options
- Foods and medications to avoid
- Management strategies for people with the condition

## License


## Contributing

Contributions to improve the assistant are welcome. Please feel free to submit a Pull Request.

