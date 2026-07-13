from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from .ai import process_note
from django.db.models import Q
from .vector_store import save_to_chroma
from .vector_store import search_chroma
from .ai import ask_notes


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

    search = request.GET.get("search")

    notes = Note.objects.filter(user=request.user).order_by("-is_pinned", "-created_at")


    if search:

        notes = notes.filter(

            Q(title__icontains=search) |
            Q(content__icontains=search) |
            Q(summary__icontains=search) |
            Q(tags__icontains=search) |
            Q(category__name__icontains=search)

        )

    paginator = Paginator(notes, 5)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    total_notes = Note.objects.filter(user=request.user).count()

    pinned_notes = Note.objects.filter(
        user=request.user,
        is_pinned=True
    ).count()

    total_categories = Category.objects.filter(
        user=request.user
    ).count()

    return render(request, "notes/home.html", {
    "page_obj": page_obj,
    "total_notes": total_notes,
    "pinned_notes": pinned_notes,
    "total_categories": total_categories,
})


def logout_view(request):
    logout(request)
    return redirect("login")



@login_required
def edit_note(request, pk):

    note = Note.objects.get(pk=pk, user=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)

        if form.is_valid():
            form.save()
            return redirect("library")

    else:
        form = NoteForm(instance=note)

    return render(request, "notes/edit_note.html", {"form": form})

@login_required
def delete_note(request, pk):

    note = Note.objects.get(pk=pk, user=request.user)

    if request.method == "POST":

        category = note.category

        note.delete()

        if not Note.objects.filter(category=category).exists():
            category.delete()

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

        result = process_note(content)

        return JsonResponse(result)


@login_required
def ai_workspace(request):
    return render(request, "notes/ai_workspace.html")


def save_note(request):

    if request.method == "POST":

        title = request.POST.get("title")
        content = request.POST.get("content")
        category_name = request.POST.get("category")
        summary = request.POST.get("summary")
        tags = request.POST.get("tags")
        ai_generated = request.POST.get("ai_generated") == "true"

        category, created = Category.objects.get_or_create(
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
    

@login_required
def ask_question(request):

    if request.method == "POST":

        question = request.POST.get("question")

        results = search_chroma(
            question,
            request.user.id
        )

        documents = results["documents"][0]

        context = "\n\n".join(documents)

        answer = ask_notes(question, context)

        return JsonResponse({
            "answer": answer
        })

    return JsonResponse({"error": "Invalid request"}, status=400)

   
