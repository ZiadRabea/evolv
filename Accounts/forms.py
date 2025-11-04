from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
 
class SignUP(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'first_name', 'last_name']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        exclude= ["user", "slug", "youtube"]

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ["owner", "created_at"]

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name']