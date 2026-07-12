from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("", views.home, name="home"),
    path("logout/", views.logout_view, name="logout"),
    path("add-note/", views.add_note, name="add_note"),
    path("edit-note/<int:pk>/", views.edit_note, name="edit_note"),
    path("delete-note/<int:pk>/", views.delete_note, name="delete_note"),
    path("toggle-pin/<int:pk>/", views.toggle_pin, name="toggle_pin"),
]