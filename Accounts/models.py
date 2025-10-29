from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField
from cloudinary_storage.storage import MediaCloudinaryStorage
# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    profile_pic = models.ImageField(null=True, blank=True, upload_to="profile_pics", storage=MediaCloudinaryStorage)
    bio = models.TextField(null=True, blank=True, default="Add your bio")
    slug = models.SlugField(null=True, blank=True)
    job_title = models.CharField(null=True, blank=True, max_length=100, default="No job title")
    skills = ArrayField(models.CharField(max_length=100), null=True, blank=True, default=list)
    linkedin = models.URLField(null=True, blank=True)
    followers = models.ManyToManyField("Profile", blank=True, related_name="follower")
    following = models.ManyToManyField("Profile", blank=True, related_name="follow")
    chats = models.ManyToManyField("Profile", blank=True, related_name="chatters")
    github = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    youtube = models.URLField(null=True, blank=True)


    def __str__(self):
        return str(self.user)

class Project(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000)
    image = models.ImageField(upload_to="projects", storage=MediaCloudinaryStorage)
    created_at = models.DateTimeField(auto_now_add=True)
    tech = ArrayField(models.CharField(max_length=100), null=True, blank=True, default=list)
    
    def __str__(self):
        return f"{self.title} | {self.owner}"

    class Meta:
        ordering = ["-created_at"]

class Message(models.Model):
    sender = models.ForeignKey(Profile, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(Profile, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender.user.username} → {self.recipient.user.username}: {self.content[:30]}"
    
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance, slug=f"{instance.username}")