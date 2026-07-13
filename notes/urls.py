from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("", views.ai_workspace, name="workspace"),
    path("library/", views.notes_list, name="library"),
    path("logout/", views.logout_view, name="logout"),
    path("edit-note/<int:pk>/", views.edit_note, name="edit_note"),
    path("delete-note/<int:pk>/", views.delete_note, name="delete_note"),
    path("toggle-pin/<int:pk>/", views.toggle_pin, name="toggle_pin"),
    path("generate-title/", views.generate_title_ai, name="generate_title_ai"),
    path("ai/", views.ai_workspace, name="ai_workspace"),
    path("save-note/", views.save_note, name="save_note"),
    path("ask/", views.ask_question, name="ask_question"),
]   