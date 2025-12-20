# Physical AI & Humanoid Robotics Textbook

This project contains a comprehensive textbook on Physical AI and Humanoid Robotics, with an integrated RAG chatbot system.

## Project Structure

- `backend/` - RAG Chatbot backend with FastAPI, Cohere, Qdrant and Gemini integration
- `my-website/` - Docusaurus frontend with ChatKit integration
- `specs/` - Specification files for the RAG chatbot feature

## Running the Application

### Prerequisites

- Python 3.13+
- Node.js v18+
- Access to Cohere, Qdrant Cloud, and Google Gemini APIs

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env` file:
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

### Frontend Setup

1. Navigate to the website directory:
```bash
cd my-website
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

### Usage

1. Make sure both backend and frontend are running
2. Visit `http://localhost:3000` in your browser
3. Use the "Chat with AI Assistant" button or navigate to the Chat page
4. Ask questions about the technical book content
5. The system will retrieve relevant information and generate responses based on the book content

## Features

- **RAG Chatbot**: Retrieval-Augmented Generation chatbot that answers questions based on book content
- **Content Guardrails**: Rejects off-topic queries and focuses on book-related content
- **Docusaurus Integration**: Seamless integration with Docusaurus documentation site
- **Performance Monitoring**: Response time tracking and metrics
- **Security**: Input validation and sanitization