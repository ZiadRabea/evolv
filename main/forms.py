from django import forms
from .models import *
 
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields= ["text", "poster", "audience"]
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields= ["text"]

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        exclude = ["is_primary", "is_public", "rating"]

    

