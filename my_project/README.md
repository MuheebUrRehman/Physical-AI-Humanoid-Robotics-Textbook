# Physical AI & Humanoid Robotics Textbook

A comprehensive textbook on Physical AI and Humanoid Robotics with an integrated RAG (Retrieval-Augmented Generation) chatbot system for interactive learning.

## Project Structure

```
my_project/
├── backend/                # FastAPI backend with RAG functionality
│   ├── app.py              # Main API application
│   ├── agent.py            # AI agent implementation
│   ├── retrieval.py        # Vector retrieval and similarity search
│   ├── config.py           # Configuration settings
│   ├── models/             # Data models
│   ├── utils/              # Utility functions
│   └── tests/              # Test suite
├── frontend/               # Docusaurus frontend application
│   ├── src/                # Source code
│   ├── docs/               # Documentation pages
│   ├── code/               # Code examples
│   ├── package.json        # Node.js dependencies
│   └── docusaurus.config.ts # Docusaurus configuration
├── ingestion/              # Book content ingestion scripts
│   ├── ingest_book.py      # Script to process and index book content
│   ├── e2e_test.py         # End-to-end tests
│   └── requirements.txt    # Python dependencies
├── .env                    # Environment variables
└── .gitignore              # Git ignore rules
```

## Commands to Navigate and Run

### Prerequisites
- Python 3.13+
- Node.js v18+

### Backend Setup and Run
1. Navigate to the backend directory:
```bash
cd my_project/backend
```

2. Set up a virtual environment and install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables in `.env` file:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_API_KEY=your_qdrant_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
QDRANT_HOST=your_qdrant_host_here
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=book_vectors
TOP_K=5
QUERY_TIMEOUT=30
```

4. Start the backend server:
```bash
uvicorn app:app --reload --port 8000
```

### Frontend Setup and Run
1. Navigate to the frontend directory:
```bash
cd my_project/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run start
```

The frontend will be available at `http://localhost:3000` and the backend API at `http://localhost:8000`.

### Content Ingestion
1. Navigate to the ingestion directory:
```bash
cd my_project/ingestion
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the ingestion script to process book content:
```bash
python ingest_book.py
```

### Full Application Usage
1. Start the backend server first
2. In a separate terminal, start the frontend server
3. Visit `http://localhost:3000` in your browser
4. Use the chat interface to ask questions about the textbook content