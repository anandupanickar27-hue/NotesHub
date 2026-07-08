from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages


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
    return render(request, "notes/home.html")


def logout_view(request):
    logout(request)
    return redirect("login")