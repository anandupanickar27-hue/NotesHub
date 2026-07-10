from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages

from notes.models import Note
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
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")
    return render(request, "notes/login.html")


@login_required
def home(request):
    notes = Note.objects.filter(user=request.user)

    return render(
        request,
        "notes/home.html",
        {"notes": notes}
    )


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def add_note(request):

    if request.method == "POST":
        form = NoteForm(request.POST)

        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()

            return redirect("home")

    else:
        form = NoteForm()

    return render(request, "notes/add_note.html", {"form": form})

@login_required
def edit_note(request, pk):

    note = Note.objects.get(pk=pk, user=request.user)

    if request.method == "POST":
        form = NoteForm(request.POST, instance=note)

        if form.is_valid():
            form.save()
            return redirect("home")

    else:
        form = NoteForm(instance=note)

    return render(request, "notes/edit_note.html", {"form": form})

@login_required
def delete_note(request, pk):

    note = Note.objects.get(pk=pk, user=request.user)

    if request.method == "POST":
        note.delete()
        messages.success(request, "Note deleted successfully.")

    return redirect("home")