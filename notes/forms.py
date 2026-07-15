from django import forms
from django.contrib.auth.models import User

from .models import Note, Profile


class NoteForm(forms.ModelForm):

    class Meta:

        model = Note

        fields = [
            "title",
            "category",
            "content",
            "is_pinned"
        ]


class ProfileForm(forms.ModelForm):

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False)

    class Meta:

        model = Profile

        fields = [
            "bio"
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields["first_name"].initial = self.instance.user.first_name
        self.fields["last_name"].initial = self.instance.user.last_name
        self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):

        profile = super().save(commit=False)

        user = profile.user

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:

            user.save()
            profile.save()

        return profile