from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count

from .models import Note, Category
from .ai import process_note, ask_notes
from .vector_store import (
    save_to_chroma,
    search_chroma,
    collection,
)
from .forms import ProfileForm
from .models import Profile


from notes.models import Category, Note
from .forms import NoteForm

def register(request):

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists")
            return redirect("register")       
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")
        User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
        messages.success(request, "Registration successful. Please login.")
        return redirect("login")

    return render(request, "notes/register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect("workspace")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "notes/login.html")

@login_required
def notes_list(request):

    search = request.GET.get("search", "")
    sort = request.GET.get("sort", "latest")
    category = request.GET.get("category", "")
    note_type = request.GET.get("type", "")
    pinned = request.GET.get("pinned", "")

    notes = Note.objects.filter(user=request.user)

    if search:

        notes = notes.filter(
            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(summary__icontains=search) |
            Q(tags__icontains=search)
        )

    if category:

        notes = notes.filter(
            category__name=category
        )

    if note_type == "ai":

        notes = notes.filter(
            ai_generated=True
        )

    elif note_type == "manual":

        notes = notes.filter(
            ai_generated=False
        )

    if pinned == "yes":

        notes = notes.filter(
            is_pinned=True
        )

    elif pinned == "no":

        notes = notes.filter(
            is_pinned=False
        )

    if sort == "latest":

        notes = notes.order_by("-created_at")

    elif sort == "oldest":

        notes = notes.order_by("created_at")

    elif sort == "az":

        notes = notes.order_by("title")

    elif sort == "za":

        notes = notes.order_by("-title")

    paginator = Paginator(notes, 5)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    user_notes = Note.objects.filter(
        user=request.user
    )

    total_notes = user_notes.count()

    pinned_notes = user_notes.filter(
        is_pinned=True
    ).count()

    total_categories = (
        Category.objects
        .filter(user=request.user)
        .annotate(note_count=Count("note"))
        .filter(note_count__gt=0)
        .count()
    )

    categories = (
        Category.objects
        .filter(user=request.user)
        .annotate(note_count=Count("note"))
        .filter(note_count__gt=0)
        .order_by("name")
    )

    return render(request, "notes/home.html", {

        "page_obj": page_obj,
        "total_notes": total_notes,
        "pinned_notes": pinned_notes,
        "total_categories": total_categories,
        "categories": categories,

    })


def logout_view(request):

    if request.session.get("is_demo"):

        demo_notes = Note.objects.filter(
            user=request.user,
            is_seed=False
        )

        for note in demo_notes:

            try:
                collection.delete(
                    ids=[str(note.id)]
                )

            except Exception:
                pass

        demo_notes.delete()

        request.session.pop("is_demo", None)

    request.session.pop("chat_history", None)

    logout(request)

    return redirect("login")




@login_required
def edit_note(request, pk):

    note = Note.objects.get(pk=pk, user=request.user)

    if request.method == "POST":

        form = NoteForm(request.POST, instance=note)

        if form.is_valid():

            note = form.save()

            collection.delete(
                ids=[str(note.id)]
            )

            save_to_chroma(note)

            messages.success(request, "Note updated successfully.")

            return redirect("library")

    else:

        form = NoteForm(instance=note)

    return render(request, "notes/edit_note.html", {
        "form": form
    })
@login_required
def delete_note(request, pk):

    note = Note.objects.get(pk=pk, user=request.user)

    if request.method == "POST":

        collection.delete(
            ids=[str(note.id)]
        )

        note.delete()

        remaining_notes = Note.objects.filter(
            user=request.user,
            category=note.category
        )

        if not remaining_notes.exists():

            note.category.delete()

        messages.success(request, "Note deleted successfully.")

        return redirect("library")

@login_required
def toggle_pin(request, pk):

    note = Note.objects.get(pk=pk, user=request.user)

    note.is_pinned = not note.is_pinned

    note.save()

    return redirect("library")


@login_required
def generate_title_ai(request):

    if request.method == "POST":

        content = request.POST.get("content")

        try:
            result = process_note(content)
            return JsonResponse(result)

        except Exception as e:
            return JsonResponse(
                {
                    "error": str(e)
                },
                status=400
            )

    return JsonResponse(
        {
            "error": "Invalid request."
        },
        status=405
    )


@login_required
def ai_workspace(request):
    categories = Category.objects.filter(
        user=request.user
    ).order_by("name")
    return render(

    request,

    "notes/ai_workspace.html",

    {

        "categories": categories

    }

)

def save_note(request):

    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")
        category_name = request.POST.get("category")
        summary = request.POST.get("summary")
        tags = request.POST.get("tags")
        ai_generated = request.POST.get("ai_generated") == "true"
        if ai_generated:

            category, _ = Category.objects.get_or_create(
                user=request.user,
                name=category_name
            )

        else:

            category, _ = Category.objects.get_or_create(

                user=request.user,
                name=category_name

            )

        note = Note.objects.create(
            user=request.user,
            title=title,
            content=content,
            category=category,
            summary=summary,
            tags=tags,
            ai_generated=ai_generated,
            embedding_status=False
        )

        save_to_chroma(note)

        note.embedding_status = True
        note.save()

        return JsonResponse({
            "message": "Note saved successfully!"
        })


def about(request):

    return render(request, "notes/about.html")  

@login_required
def ask_question(request):

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request"}, status=400)

    question = request.POST.get("question", "").strip()

    if not question:
        return JsonResponse({
            "answer": "Please enter a question."
        })


    results = search_chroma(
        question,
        request.user.id
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    if not documents:
        return JsonResponse({
            "answer": "I couldn't find any notes related to that."
        })

    seen = set()
    context = ""

    for doc, meta in zip(documents, metadatas):

        key = (
            meta.get("title"),
            meta.get("created_at")
        )

        if key in seen:
            continue

        seen.add(key)

        context += f"""
Title: {meta.get("title")}

Category: {meta.get("category")}

Created: {meta.get("created_at")}

AI Generated: {meta.get("ai_generated")}

Pinned: {meta.get("is_pinned")}

{doc}

------------------------------------------

"""


    answer = ask_notes(
        question=question,
        context=context,
        username=request.user.first_name or request.user.username,
        is_demo=request.user.username == "demo"
    )

    return JsonResponse({
        "answer": answer
    })

def demo_login(request):

    user = User.objects.get(username="demo")

    login(request, user)

    request.session["is_demo"] = True

    return redirect("workspace")

@login_required
def profile(request):

    profile, _ = Profile.objects.get_or_create(
    user=request.user
    )

    notes = Note.objects.filter(user=request.user)

    context = {

        "profile": profile,

        "total_notes": notes.count(),

        "ai_notes": notes.filter(ai_generated=True).count(),

        "manual_notes": notes.filter(ai_generated=False).count(),

        "pinned_notes": notes.filter(is_pinned=True).count(),

        "categories": (
            Category.objects
            .filter(user=request.user)
            .annotate(note_count=Count("note"))
            .filter(note_count__gt=0)
            .count()
        )

    }

    return render(
        request,
        "notes/profile.html",
        context
    )


@login_required
def edit_profile(request):

    profile, _ = Profile.objects.get_or_create(
    user=request.user
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully."
            )

            return redirect("profile")

    else:

        form = ProfileForm(
            instance=profile
        )

    return render(
        request,
        "notes/edit_profile.html",
        {
            "form": form
        }
    )