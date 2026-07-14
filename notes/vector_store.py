from dotenv import load_dotenv

import chromadb

from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001"
)

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="notes"
)


def save_to_chroma(note):

    if not note.content or not note.content.strip():
        return

    try:
        collection.delete(
            ids=[str(note.id)]
        )
    except:
        pass

    text = f"""
Title: {note.title}

Category: {note.category.name}

Summary: {note.summary or ""}

Tags: {note.tags or ""}

Created: {note.created_at.strftime("%Y-%m-%d %H:%M")}

Content:
{note.content}
"""

    collection.add(

        ids=[str(note.id)],

        documents=[text],

        metadatas=[{

            "title": note.title,
            "category": note.category.name,
            "created_at": note.created_at.strftime("%Y-%m-%d"),
            "user_id": note.user.id,
            "ai_generated": note.ai_generated,
            "is_pinned": note.is_pinned

        }],

        embeddings=[

            embeddings.embed_query(text)

        ]

    )

def search_chroma(query, user_id):

    query_embedding = embeddings.embed_query(query)

    results = collection.query(

        query_embeddings=[query_embedding],

        n_results=10,

        where={
            "user_id": user_id
        },

        include=[
            "documents",
            "metadatas",
            "distances"
        ]

    )

    return results