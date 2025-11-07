from fastapi import FastAPI
from pydantic import BaseModel
import mysql.connector
from elasticsearch import Elasticsearch
import openai
import os
import json
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
    use_llm: bool = True  # Enable LLM post-processing by default


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


def llm_process_results(user_query: str, matches: list):
    """
    Use LLM to synthesize an answer from the top Elasticsearch matches,
    following a standardized JSON output schema for front-end consumption.
    """
    print("[LLM] Starting llm_process_results")
    print(f"[LLM] User query: {user_query}")
    print(f"[LLM] Number of matches: {len(matches)}")

    # ✅ Handle no matches
    if not matches:
        print("[LLM] No matches found, returning fallback response")

        return {
            "language": "fr",
            "answered": False,
            "answer_html": "<p>Je n’ai pas trouvé d’information fiable dans la base de connaissances.</p>"
                           "<p>Pour obtenir une réponse, utilise ce canal : "
                           "<a href='https://example.com/contact'>Formulaire de contact</a>.</p>",
            "reason_if_unanswered": "Aucun extrait pertinent n'a été trouvé.",
            "used_source_ids": [],
            "citations": [],
            "meta": {"query_echo": user_query, "notes": "No matches found"},
            "redirect": {
                "needed": True,
                "label": "Formulaire de contact",
                "url": "https://example.com/contact"
            }
        }

    # ✅ Build structured context for LLM
    print("[LLM] Building excerpts from matches...")
    excerpts = [
        {
            "id": match["id"],
            "title": match["question"],
            "url": None,
            "content": match["answer"],
            "language": "fr"  # Adapt if your data includes 'langues'
        }
        for match in matches
    ]
    print(f"[LLM] Built {len(excerpts)} excerpts")

    fallback = {"label": "Formulaire de contact", "url": "https://example.com/contact"}

    # ✅ System Prompt
    system_prompt = (
        "Rôle : Tu es l’assistant officiel du Help Center PLV. "
        "Objectif : Produire la meilleure réponse possible STRICTEMENT à partir des extraits fournis.\n\n"
        "Entrées : \n"
        "- user_question : la question utilisateur.\n"
        "- excerpts : liste d’extraits autorisés, chacun sous la forme :\n"
        "  { 'id': 'string', 'title': 'string', 'url': 'string|null', 'content': 'string', 'language': 'string' }\n"
        "- fallback : { 'label': 'string', 'url': 'string' }\n\n"
        "Règles :\n"
        "- Réponds uniquement à partir des excerpts. N’invente rien.\n"
        "- Si l’information n’est pas présente ou insuffisante, dis-le et propose la redirection (fallback).\n"
        "- Cite toutes les affirmations factuelles par [⟨titre/section⟩].\n"
        "- Le contenu doit être du HTML propre (<p>, <ul>, <ol>, <strong>, <a>, etc.).\n"
        "- Langue = celle de la question (FR par défaut). Ton : clair, concis, bienveillant.\n"
        "- S’il existe plusieurs procédures, commence par un résumé puis des étapes numérotées.\n"
        "- Sortie unique : retourne EXACTEMENT un objet JSON (aucun texte avant ou après, aucun Markdown).\n\n"
        "Format JSON attendu :\n"
        "{\n"
        '  "language": "fr",\n'
        '  "answered": true,\n'
        '  "answer_html": "<p><strong>Réponse courte :</strong> …</p><ol>…</ol>",\n'
        '  "reason_if_unanswered": null,\n'
        '  "used_source_ids": ["doc_017", "doc_042"],\n'
        '  "citations": [{"id": "doc_017", "title": "Procédure", "url": "https://..." }],\n'
        '  "meta": {"query_echo": "question utilisateur normalisée", "notes": "…"},\n'
        '  "redirect": {"needed": false, "label": null, "url": null}\n'
        "}"
    )

    # ✅ User Prompt (as JSON string for better parsing)
    user_prompt = {
        "user_question": user_query,
        "excerpts": excerpts,
        "fallback": fallback
    }

    # ✅ LLM call with response_format for JSON
    print("[LLM] Calling OpenAI API...")
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_prompt, ensure_ascii=False)}
            ],
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"}  # Force JSON output
        )

        print("[LLM] Received response from OpenAI")
        content = response.choices[0].message.content.strip()

        print("[LLM] Raw Response:", content[:200] + "..." if len(content) > 200 else content)

        # ✅ Parse JSON safely
        print("[LLM] Parsing JSON response...")
        try:
            result_json = json.loads(content)
            print("[LLM] JSON parsed successfully")
        except json.JSONDecodeError:
            print("[LLM] JSON parsing failed, using fallback")
            # fallback if not strictly JSON
            # Wrap answers in <p> tags if not already HTML
            citations_with_wrapped_answers = []
            for m in matches:
                answer = m['answer']
                if answer and not answer.strip().startswith('<'):
                    answer = f"<p>{answer}</p>"
                citations_with_wrapped_answers.append({
                    "id": m['id'],
                    "title": m['question'],
                    "url": None,
                    "answer": answer
                })

            result_json = {
                "language": "fr",
                "answered": True,
                "answer_html": f"<p>{content}</p>",
                "reason_if_unanswered": None,
                "used_source_ids": [m['id'] for m in matches],
                "citations": citations_with_wrapped_answers,
                "meta": {"query_echo": user_query, "notes": "Non-JSON fallback"},
                "redirect": {"needed": False, "label": None, "url": None}
            }

        # ✅ Enrich citations with full answer content from matches
        print("[LLM] Enriching citations with answer content...")
        if "citations" in result_json and result_json["citations"]:
            # Create a map of id -> match for quick lookup
            # Support both string and int IDs for flexible matching
            match_map = {}
            for m in matches:
                match_map[m['id']] = m
                match_map[str(m['id'])] = m  # Also add string version of ID

            print(f"DEBUG: Match map keys: {list(match_map.keys())}")
            print(f"DEBUG: Citation IDs before enrichment: {[c.get('id') for c in result_json['citations']]}")

            # Add answer content to each citation
            for citation in result_json["citations"]:
                citation_id = citation.get("id")

                # Try to find match with both original ID and string version
                matched_item = match_map.get(citation_id) or match_map.get(str(citation_id))

                # Always ensure the citation has an "answer" field
                if matched_item:
                    answer_content = matched_item["answer"]
                    print(f"DEBUG: Found match for citation ID {citation_id}, answer length: {len(answer_content) if answer_content else 0}")
                else:
                    # If ID not found in matches, check if citation already has an answer
                    answer_content = citation.get("answer")
                    if not answer_content:
                        print(f"WARNING: No match found for citation ID {citation_id} and no existing answer")
                        answer_content = "Contenu non disponible"
                    else:
                        print(f"DEBUG: No match for citation ID {citation_id}, using existing answer from citation")

                # If answer doesn't already start with HTML tags, wrap it in <p>
                if answer_content and not answer_content.strip().startswith('<'):
                    answer_content = f"<p>{answer_content}</p>"

                citation["answer"] = answer_content

                # Add score if available from match
                if matched_item:
                    citation["score"] = matched_item.get("score")

        # Debug: Print citations to verify answer field is present
        print("[LLM] Enriched citations:", json.dumps(result_json.get("citations", []), ensure_ascii=False, indent=2)[:500] + "...")

        print("[LLM] Returning result_json")
        return result_json

    except Exception as e:
        print(f"[LLM] ERROR: {str(e)}")

        # Fallback to the best match if API fails
        fallback_answer = matches[0]["answer"]
        # Wrap in <p> if not already HTML
        if fallback_answer and not fallback_answer.strip().startswith('<'):
            fallback_answer = f"<p>{fallback_answer}</p>"

        return {
            "language": "fr",
            "answered": True,
            "answer_html": fallback_answer,
            "reason_if_unanswered": None,
            "used_source_ids": [matches[0]["id"]],
            "citations": [{"id": matches[0]["id"], "title": matches[0]["question"], "url": None, "answer": fallback_answer, "score": matches[0].get("score")}],
            "meta": {"query_echo": user_query, "notes": "LLM error fallback"},
            "redirect": {"needed": False, "label": None, "url": None},
            "error": str(e)
        }


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
    print("\n" + "="*60)
    print("[START] ask_question called")
    print("="*60)

    query = payload.message
    top_k = payload.top_k
    use_llm = payload.use_llm

    print(f"[DEBUG] Query: {query}")
    print(f"[DEBUG] Top K: {top_k}")
    print(f"[DEBUG] Use LLM: {use_llm}")

    print("\n[STEP 1] Connecting to Elasticsearch...")
    es = Elasticsearch([f"http://{ES_HOST}:{ES_PORT}"])
    print(f"[DEBUG] Connected to Elasticsearch at {ES_HOST}:{ES_PORT}")

    print("\n[STEP 2] Generating query embedding...")
    query_embedding = generate_embedding(query)
    print(f"[DEBUG] Embedding generated (length: {len(query_embedding)})")

    print("\n[STEP 3] Searching Elasticsearch...")
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
    print(f"[DEBUG] Search complete. Found {len(results['hits']['hits'])} results")

    print("\n[STEP 4] Processing matches...")
    matches = [
        {
            "score": hit["_score"],
            "id": hit["_source"]["id"],
            "question": hit["_source"]["question"],
            "answer": hit["_source"]["answer"],
        }
        for hit in results['hits']['hits']
    ]
    print(f"[DEBUG] Processed {len(matches)} matches")

    # If LLM processing is enabled, use it to synthesize the best answer
    if use_llm and matches:
        print("\n[STEP 5] Calling LLM to process results...")
        result = llm_process_results(query, matches)
        print("[DEBUG] LLM processing complete")
        print("="*60)
        print("[END] Returning LLM-processed response")
        print("="*60 + "\n")
        return result

    # Otherwise, return raw matches (original behavior)
    print("\n[STEP 5] Returning raw matches (no LLM)")
    print("="*60)
    print("[END] Returning raw response")
    print("="*60 + "\n")
    return {
        "matches": matches,
        "llm_processed": False
    }
