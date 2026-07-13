from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


import json

def process_note(content):

    prompt = f"""
    You are an AI assistant.

    Analyze the following note and return ONLY valid JSON.

    {{
      "title": "...",
      "category": "...",
      "summary": "...",
      "tags": ["...", "...", "..."]
    }}

    Note:
    {content}

    Do not return markdown.
    Do not use ```json.
    Return only JSON.
    """

    response = llm.invoke(prompt)

    return json.loads(response.content)

def ask_notes(question, context):

    prompt = f"""
You are an AI assistant.

Answer ONLY using the context below.

If the answer is not present in the context, reply:

"I couldn't find that information in your notes."

Context:
{context}

Question:
{question}
"""

    response = llm.invoke(prompt)

    return response.content