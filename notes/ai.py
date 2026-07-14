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
You are GoFi AI, a personal knowledge assistant.

You answer questions ONLY using the notes provided below.

==================================================
USER NOTES
==================================================

{context}

==================================================
QUESTION
==================================================

{question}

==================================================
RULES
==================================================

GENERAL
- Use ONLY the provided notes.
- Never invent information.
- Never use outside knowledge.
- If the answer is not found, reply:
  "I couldn't find any notes related to that."

DATES
- Every note contains a Created date.
- Understand natural date questions such as:
  • today
  • yesterday
  • this week
  • last week
  • this month
  • last month
  • this year
  • latest
  • oldest
  • recently
  • specific dates
- Use the Created date to answer these questions.

NOTE SEARCH
If the user asks about:
- a title
- category
- tags
- summary
- programming language
- technology
- topic

find every relevant note before answering.

SUMMARIES
If the user asks to summarize:
- summarize the relevant notes instead of copying them.

COMPARISONS
If the user asks to compare notes:
- compare them in a Markdown table.

LISTS
If the user asks:
- list
- show
- what are
- which

return a bullet list.

CODE
If notes contain code:
- preserve formatting exactly.

MULTIPLE NOTES
If multiple notes answer the question:
- combine them logically.
- avoid repeating the same information.

CONFLICTS
If two notes disagree:
- mention both.

STYLE
- Use Markdown.
- Use headings when appropriate.
- Use bullet points where helpful.
- Keep answers concise unless more detail is requested.
- Mention the note title whenever it improves clarity.

==================================================
ANSWER
==================================================
"""

    try:

        response = llm.invoke(prompt)

        answer = response.content.strip()

        answer = answer.replace("**Answer:**", "")
        answer = answer.replace("Answer:", "")

        return answer

    except Exception:

        return "Sorry, I couldn't process your request right now. Please try again."