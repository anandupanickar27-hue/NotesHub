import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "noteshub.settings")
django.setup()

from django.contrib.auth.models import User
from notes.models import Category, Note
from notes.vector_store import save_to_chroma, collection
from datetime import datetime, timedelta
from django.utils import timezone

user = User.objects.get(username="demo")

demo_notes = Note.objects.filter(user=user)

for note in demo_notes:

    try:
        collection.delete(ids=[str(note.id)])

    except Exception:
        pass

demo_notes.delete()

Category.objects.filter(user=user).delete()

notes = [

("Python Basics","Python","Python is a high-level, interpreted programming language known for its readability and versatility. It supports object-oriented, procedural, and functional programming paradigms."),

("Object-Oriented Programming","Python","Object-Oriented Programming (OOP) organizes code using classes and objects. The four pillars are encapsulation, inheritance, polymorphism, and abstraction."),

("Django Models","Django","Django models represent database tables. Every model corresponds to a table, and each field represents a column."),

("Django Views","Django","Views process incoming HTTP requests and return HTTP responses. Django supports both function-based and class-based views."),

("REST APIs","Web Development","REST APIs allow applications to communicate over HTTP using methods like GET, POST, PUT, PATCH, and DELETE."),

("SQL Joins","SQL","SQL joins combine data from multiple tables. Common joins include INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN."),

("Machine Learning Basics","Artificial Intelligence","Machine learning enables computers to learn patterns from data without explicit programming."),

("Deep Learning","Artificial Intelligence","Deep learning uses multi-layer neural networks to solve tasks such as image recognition and natural language processing."),

("Prompt Engineering","Artificial Intelligence","Prompt engineering is the practice of writing effective prompts to obtain better responses from large language models."),

("Retrieval-Augmented Generation","Artificial Intelligence","Retrieval-Augmented Generation (RAG) combines semantic search with large language models to answer questions using external knowledge."),

("ChromaDB","Artificial Intelligence","ChromaDB stores vector embeddings and enables semantic search based on meaning instead of keywords."),

("Git Basics","Git","Git is a distributed version control system used to track changes and collaborate on software projects."),

("Docker Overview","DevOps","Docker packages applications and their dependencies into lightweight containers for consistent deployment."),

("Agile Development","Software Engineering","Agile development focuses on iterative delivery, collaboration, customer feedback, and continuous improvement."),

("Time Management","Productivity","Effective time management includes prioritization, time blocking, and minimizing distractions."),

("Meeting Notes","Productivity","Project meeting discussed implementing profile management, semantic search improvements, deployment planning, and UI enhancements."),

("Workout Routine","Fitness","Weekly routine: Monday - Chest & Triceps, Tuesday - Back & Biceps, Wednesday - Legs, Thursday - Shoulders, Friday - Full Body."),

("Healthy Diet","Fitness","A balanced diet includes lean proteins, vegetables, fruits, whole grains, healthy fats, and sufficient water intake."),

("Sleep Tips","Health","Adults should aim for seven to nine hours of quality sleep every night for better health and recovery."),

("Monthly Budget","Finance","A good monthly budget allocates money for needs, savings, investments, and discretionary spending."),

("Investing Basics","Finance","Long-term investing emphasizes diversification, compound growth, and consistent investing over time."),

("Japan Travel Plan","Travel","Travel itinerary includes Tokyo, Kyoto, Osaka, Mount Fuji, and using the JR Pass for transportation."),

("Kerala Trip","Travel","Visit Munnar, Alleppey, Fort Kochi, Wayanad, and Athirappilly during a one-week Kerala trip."),

("High Protein Breakfast","Cooking","A nutritious breakfast can include eggs, oats, Greek yogurt, fruits, and nuts for sustained energy.")

]

base_date = timezone.make_aware(
    datetime(2026, 7, 1, 9, 0)
)

for i, (title, category_name, content) in enumerate(notes):

    category, _ = Category.objects.get_or_create(
        user=user,
        name=category_name
    )

    note = Note.objects.create(
        user=user,
        title=title,
        category=category,
        content=content,
        summary="",
        tags="",
        ai_generated=False
    )

    note.created_at = base_date + timedelta(days=i)
    note.save(update_fields=["created_at"])

    save_to_chroma(note)

print(f"{len(notes)} demo notes created successfully.")