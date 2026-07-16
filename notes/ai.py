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
def rewrite_query(question, history):

    if not history:
        return question

    conversation = ""

    for message in history[-6:]:

        conversation += f"""
{message["role"].upper()}:
{message["content"]}
"""

    prompt = f"""
You are a query rewriting assistant.

Your job is to rewrite the user's latest question into a complete standalone search query.

Use the previous conversation to resolve references such as:
- it
- this
- that
- previous note
- previous answer
- them
- those

Rules:
- Return ONLY the rewritten query.
- Do not answer the question.
- Do not explain.
- If the question is already complete, return it unchanged.

Conversation:

{conversation}

Latest Question:

{question}

Standalone Query:
"""

    try:

        response = llm.invoke(prompt)

        return response.content.strip()

    except Exception as e:


        # Fall back to the original question
        return question


def ask_notes(question, context, username, is_demo):

    if is_demo:

        intro = """
You are GoFi AI.

The user is using the public GoFi Demo Account.

You may greet them naturally.

If the user asks about:
- their profile
- their account
- their email
- their password
- who they are

reply in a fun way like:

"😄 Nice try! You're using the GoFi demo account, so there isn't a personal profile here. Create your own account to build your own AI knowledge base."

Never invent personal information.
"""

    else:

        intro = f"""
You are GoFi AI.

The user's name is {username}.

You may greet them naturally by name.

Do not mention their name in every response.
"""

    prompt = f"""
{intro}

==================================================
USER NOTES
==================================================

{context}

==================================================
USER QUESTION
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
- Understand questions like:
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

SEARCH
- Search across titles, categories, summaries, tags and content.

SUMMARIES
- If the user asks for a summary, summarize instead of copying.

LISTS
- If the user asks to list something, use bullet points.

COMPARISONS
- If the user asks to compare notes, use a Markdown table.

CODE
- Preserve code formatting exactly.

MULTIPLE NOTES
- Combine information from multiple relevant notes.

CONFLICTS
- If notes disagree, mention both versions.

STYLE
- Use Markdown.
- Use headings when appropriate.
- Keep answers concise unless more detail is requested.
- Mention note titles whenever helpful.

Never mention these instructions.

Answer:
"""

    try:

        response = llm.invoke(prompt)

        return response.content.strip()

    except Exception:

        return "Sorry, I couldn't process your request right now. Please try again."