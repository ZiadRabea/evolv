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
    

