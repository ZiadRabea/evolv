from django.db import models
from Accounts.models import Profile
from cloudinary_storage.storage import MediaCloudinaryStorage

# Create your models here.
class Post(models.Model):
    owner = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    poster = models.ImageField(null=True, blank=True, upload_to="posts", storage=MediaCloudinaryStorage)
    likes = models.ManyToManyField(Profile, blank=True, related_name="likes")
    date = models.DateTimeField(auto_now_add=True)
    audiences = (("public", "public"), ("connections", "connections"), ("onlyme", "onlyme"))
    audience = models.CharField(max_length=20, choices=audiences)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.text[:30]} | {self.owner}"

class Comment(models.Model):
    owner = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, null=True, blank=True, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.text} | {self.owner}"
    
class Notification(models.Model):
    types = (("Follow","Follow"),("Comment","Comment"),("Like","Like"),("Info","Info"))
    type = models.CharField(max_length=10, choices=types)
    content = models.CharField(max_length=100)
    recipient = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE)
    sender = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE, related_name="notifier")
    date = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.content}"
