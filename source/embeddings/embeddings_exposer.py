from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
from elasticsearch import Elasticsearch
import openai
import os
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# ====================================================================
# CONFIG
# ====================================================================
load_dotenv(dotenv_path="../.env")

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

# Elasticsearch
ES_HOST = os.getenv("ES_HOST")
ES_PORT = os.getenv("ES_PORT")
ES_INDEX = os.getenv("ES_INDEX")

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_DATABASE_HC'),
}

SQL_QUERY = """
    SELECT id, title, content, post_type, langues, ecoles 
    FROM questions
    WHERE status = 'publish'
"""

# ====================================================================
# FASTAPI INIT
# ====================================================================

app = FastAPI(title="FAQ RAG API")


# ✅ Configuration CORS - À ajouter juste après la création de l'app
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",      # ✅ Votre frontend Vue.js
        "http://127.0.0.1:3000",      # ✅ Alternative localhost
        "http://localhost:5173",      # ✅ Si vous utilisez Vite
        "http://127.0.0.1:5173",      # ✅ Alternative Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],              # ✅ Autorise toutes les méthodes (GET, POST, etc.)
    allow_headers=["*"],              # ✅ Autorise tous les headers
)


# ====================================================================
# MODELS
# ====================================================================

class QuestionRequest(BaseModel):
    message: str
    top_k: int = 5


# ====================================================================
# HELPERS
# ====================================================================

def get_mysql_rows():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    cursor.execute(SQL_QUERY)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def generate_embedding(text: str):
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def index_document(es, row, embedding):
    es.index(index=ES_INDEX, id=row['id'], document={
        "id": row['id'],
        "question": row['title'],
        "answer": row['content'],
        "embedding": embedding,
        "category": row.get("post_type"),
        "language": row.get("langues"),
        "schools": row.get("ecoles")
    })


# ====================================================================
# ✅ API 1 : BUILD INDEX + EMBEDDINGS
# ====================================================================

@app.post("/build_index")
def build_index():
    es = Elasticsearch([f"http://{ES_HOST}:{ES_PORT}"])

    # Create index if not exists
    if not es.indices.exists(index=ES_INDEX):
        es.indices.create(
            index=ES_INDEX,
            mappings={
                "properties": {
                    "id": {"type": "keyword"},
                    "question": {"type": "text"},
                    "answer": {"type": "text"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": 1536,
                        "index": True,
                        "similarity": "cosine"
                    },
                    "category": {"type": "keyword"},
                    "language": {"type": "keyword"},
                    "schools": {"type": "keyword"}
                }
            }
        )

    rows = get_mysql_rows()
    count = 0

    for row in rows:
        text = f"{row['title']} {row['content']}"
        embedding = generate_embedding(text)
        index_document(es, row, embedding)
        count += 1

    es.indices.refresh(index=ES_INDEX)
    return {"status": "ok", "indexed": count}


# ====================================================================
# ✅ API 2 : SYNC + ANSWER
# ====================================================================

@app.get("/sync")
def sync_database():

    # === Fetch all MySQL IDs ===
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM questions WHERE status='publish'")
    mysql_ids = {row[0] for row in cursor.fetchall()}
    cursor.close()
    conn.close()

    # === Fetch all Elasticsearch IDs ===
    es = Elasticsearch([f"http://{ES_HOST}:{ES_PORT}"])
    resp = es.search(index=ES_INDEX, size=10000, _source=False, query={"match_all": {}})

    es_ids = {int(hit["_id"]) for hit in resp["hits"]["hits"]}

    # Compute differences
    to_delete = es_ids - mysql_ids
    to_add = mysql_ids - es_ids

    # Delete
    for doc_id in to_delete:
        es.delete(index=ES_INDEX, id=doc_id, ignore=[404])

    # Add missing rows
    if to_add:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor(dictionary=True)
        format_ids = ",".join(str(i) for i in to_add)

        cursor.execute(f"""
            SELECT id, title, content, post_type, langues, ecoles
            FROM questions
            WHERE id IN ({format_ids})
        """)
        
        rows = cursor.fetchall()
        for row in rows:
            text = f"{row['title']} {row['content']}"
            embedding = generate_embedding(text)
            index_document(es, row, embedding)

        cursor.close()
        conn.close()

    es.indices.refresh(index=ES_INDEX)

    return {
        "status": "ok",
        "deleted": len(to_delete),
        "added": len(to_add)
    }


# ====================================================================
# ✅ API 2 (suite) : SEARCH
# ====================================================================

@app.post("/ask")
def ask_question(payload: QuestionRequest):
    query = payload.message
    top_k = payload.top_k

    es = Elasticsearch([f"http://{ES_HOST}:{ES_PORT}"])

    query_embedding = generate_embedding(query)

    results = es.search(
        index=ES_INDEX,
        size=top_k,
        query={
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                    "params": {"query_vector": query_embedding}
                }
            }
        },
        _source=["id", "question", "answer", "category"]
    )

    return {
        "matches": [
            {
                "score": hit["_score"],
                "id": hit["_source"]["id"],
                "question": hit["_source"]["question"],
                "answer": hit["_source"]["answer"],
            }
            for hit in results['hits']['hits']
        ]
    }
