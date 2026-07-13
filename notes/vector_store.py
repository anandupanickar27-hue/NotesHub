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

    collection.add(

        ids=[str(note.id)],

        documents=[note.content],

       metadatas=[{
            "title": note.title,
            "category": note.category.name,
            "user_id": note.user.id
        }],

        embeddings=[
            embeddings.embed_query(note.content)
        ]

    )

def search_chroma(query, user_id):

    query_embedding = embeddings.embed_query(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=5,
        where={
            "user_id": user_id
        }
    )

    return results