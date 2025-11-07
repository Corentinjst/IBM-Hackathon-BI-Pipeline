# IBM Hackathon BI Pipeline

This project was developed for an IBM Hackathon focused on building a Business Intelligence pipeline with AI-powered question answering capabilities. The system combines a traditional help center database with semantic search using embeddings and OpenAI's GPT models to provide intelligent responses to user queries.

## Overview

The project consists of two main applications and a supporting AI infrastructure:

- **Admin Application**: For managing the help center content, viewing analytics, and monitoring system performance
- **User Application**: A public-facing interface where users can search the knowledge base and get AI-powered answers
- **RAG Pipeline**: A Retrieval-Augmented Generation system using Elasticsearch for vector search and OpenAI for answer synthesis

## Architecture

### Applications

**Admin App** (`source/app_admin/`)
- Frontend: Vue.js 3 with Vite, featuring Chart.js for analytics visualization
- Backend: Express.js REST API with MySQL2 for database access
- Purpose: Content management, analytics dashboard, feedback monitoring

**User App** (`source/app_user/`)
- Frontend: Vue.js 3 with similar architecture
- Backend: Express.js API serving user queries
- Purpose: Public help center interface

### Data Layer

**Database Scripts** (`source/db/`)
- MariaDB/MySQL database for storing help center questions and answers
- Feedback tracking system for monitoring answer quality
- Support ticket management
- Data import utilities from Excel files

**Embeddings API** (`source/embeddings/`)
- FastAPI service for semantic search
- Integration with OpenAI's text-embedding-3-small model
- Elasticsearch for vector storage and similarity search
- GPT-4o-mini for answer synthesis

## Tech Stack

### Frontend
- Vue.js 3
- Vite
- Chart.js for data visualization
- Axios for API communication

### Backend
- Express.js (Node.js)
- FastAPI (Python)
- CORS enabled for cross-origin requests

### Database & Search
- MariaDB/MySQL
- Elasticsearch (dense vector search)
- PyMySQL for Python database connections

### AI/ML
- OpenAI API (embeddings + chat completions)
- Cosine similarity for semantic search

## Project Structure

```
.
├── certification/              # IBM certification badges
├── source/
│   ├── app_admin/             # Admin dashboard
│   │   ├── backend/           # Express API
│   │   └── frontend/          # Vue.js app
│   ├── app_user/              # User-facing help center
│   │   ├── backend/           # Express API
│   │   └── frontend/          # Vue.js app
│   ├── data/                  # Data files (Excel imports)
│   ├── db/                    # Database scripts
│   │   ├── maria.py           # Main DB setup
│   │   ├── queries.py         # Query utilities
│   │   ├── feedback.py        # Feedback table schema
│   │   └── support_tickets.py # Support system
│   └── embeddings/            # RAG pipeline
│       └── embeddings_exposer.py  # FastAPI service
└── .env.example               # Environment template
```

## Setup

### Prerequisites

- Node.js (v20.19.0 or v22.12.0+)
- Python 3.8+
- MariaDB/MySQL
- Elasticsearch 8.x
- OpenAI API key

### Environment Variables

Create a `.env` file in the `source/` directory:

```env
# Database
DB_HOST=your_database_host
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_DATABASE_HC=help_center

# Elasticsearch
ES_HOST=localhost
ES_PORT=9200
ES_INDEX=faq_index

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Server Ports
ADMIN_PORT=4000
USER_PORT=3001
```

### Installation

**1. Database Setup**

```bash
cd source/db
python maria.py              # Create tables and import data
python feedback.py           # Set up feedback tracking
python support_tickets.py    # Set up support system
```

**2. Admin Application**

```bash
cd source/app_admin/backend
npm install
node server.js

cd ../frontend
npm install
npm run dev
```

**3. User Application**

```bash
cd source/app_user/backend
npm install
node server.js

cd ../frontend
npm install
npm run dev
```

**4. Embeddings Service**

```bash
cd source/embeddings
pip install -r requirements.txt  # if available
# Or manually install: fastapi uvicorn elasticsearch pymysql openai python-dotenv
uvicorn embeddings_exposer:app --reload --port 8000
```

### Building the Search Index

Once the embeddings service is running, build the initial index:

```bash
curl -X POST http://localhost:8000/build_index
```

This will fetch all published questions from the database, generate embeddings, and index them in Elasticsearch.

## Usage

### Admin Dashboard

Access at `http://localhost:5173` (or configured Vite port)

Features:
- View and manage help center questions
- Monitor feedback and answer quality
- Analytics dashboard with visualizations
- Support ticket management

### User Help Center

Access at `http://localhost:5173` (user frontend port)

Users can:
- Search the knowledge base
- Receive AI-generated answers based on relevant content
- Provide feedback on answer quality
- Submit support tickets

### API Endpoints

**Embeddings Service** (`http://localhost:8000`)

- `POST /build_index` - Build the complete search index
- `GET /sync` - Sync database changes with Elasticsearch
- `POST /ask` - Ask a question and get an AI-powered answer
  ```json
  {
    "message": "How do I reset my password?",
    "top_k": 5,
    "use_llm": true
  }
  ```

**Admin Backend** (`http://localhost:4000/api`)

- `/questions` - CRUD operations for help center content
- `/dashboard` - Analytics and metrics
- `/forms` - Form submissions and feedback

**User Backend** (`http://localhost:3001/api`)

- Similar endpoints for public-facing operations

## How It Works

1. **Content Ingestion**: Admin users manage help center content through the admin dashboard. Questions and answers are stored in MariaDB.

2. **Embedding Generation**: When content is indexed, the embeddings service uses OpenAI's API to generate vector embeddings for each question-answer pair.

3. **Vector Storage**: Embeddings are stored in Elasticsearch with cosine similarity indexing for efficient semantic search.

4. **Query Processing**: When a user asks a question:
   - The query is embedded using the same model
   - Elasticsearch performs a cosine similarity search
   - Top K most relevant documents are retrieved
   - GPT-4o-mini synthesizes a coherent answer from the retrieved context
   - Citations and source documents are included in the response

5. **Feedback Loop**: User feedback on answer quality is stored and can be used to improve the system over time.

## IBM Certifications

Team members completed various IBM certifications as part of the hackathon:

- IBM Watsonx Technical Essentials
- IBM Watsonx Data Technical Essentials
- Generative AI in Action
- Getting Started with Generative AI

Certificates are available in the `certification/` directory.

## Development Notes

- The system uses a standardized JSON schema for LLM responses to ensure consistent front-end integration
- Includes fallback mechanisms when the AI cannot confidently answer
- CORS is configured for local development across multiple ports
- Database sync functionality prevents index drift between MariaDB and Elasticsearch

## License

This project was created for the IBM Hackathon and is intended for educational purposes.
