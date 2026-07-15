import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noteshub.settings")
django.setup()

from django.contrib.auth.models import User
from notes.models import Category, Note
from notes.vector_store import save_to_chroma

demo = User.objects.get(username="demo")

Note.objects.filter(user=demo).delete()

notes = [
    {
        "title": "Python Basics",
        "category": "Programming",
        "content": "Python is an interpreted, high-level programming language. It supports OOP, functions, modules and packages."
    },
    {
        "title": "Django Models",
        "category": "Programming",
        "content": "Django models represent database tables. Each model maps to one database table."
    },
    {
        "title": "Docker Commands",
        "category": "Technology",
        "content": "docker build builds images. docker run starts containers. docker compose manages multi-container apps."
    },
    {
        "title": "Workout Routine",
        "category": "Health & Fitness",
        "content": "Monday: Chest and Triceps. Tuesday: Back and Biceps. Wednesday: Legs."
    },
    {
        "title": "Healthy Diet",
        "category": "Health & Fitness",
        "content": "Eat enough protein, vegetables, fruits and drink plenty of water."
    }
]

for item in notes:

    category, _ = Category.objects.get_or_create(
        user=demo,
        name=item["category"]
    )

    note = Note.objects.create(
        user=demo,
        title=item["title"],
        content=item["content"],
        category=category,
        summary="",
        tags="",
        ai_generated=False,
        embedding_status=True
    )

    save_to_chroma(note)

print("Demo data created.")