from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


class PatientSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text='Required. Please enter a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'patient'
        if commit:
            user.save()
        return user
