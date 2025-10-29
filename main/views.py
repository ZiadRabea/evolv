from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from.models import *
from.forms import *
from Accounts.models import Message
# Create your views here.
def home(request):
    posts = Post.objects.all()
    
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            myform = form.save(commit=False)
            myform.owner = request.user.profile
            myform.save()
            return redirect("/")
    else:
        form = PostForm()

    context = {
        "posts":posts,
        "form": form
    }

    return render(request, "home.html", context)

def post(request, id):
    post = Post.objects.get(id=id)
    
    if request.method == "POST":
        form = CommentForm(request.POST)

        if form.is_valid():
            myform = form.save(commit=False)
            myform.owner = request.user.profile
            myform.post = post
            myform.save()
            Notification.objects.create(sender=request.user.profile, recipient=post.owner, content=f"{myform.text[:30]}", type="Comment")
            return redirect(f"/post/{id}")
    else:
        form = CommentForm()

    context = {
        "post":post,
        "form": form
    }

    return render(request, "post.html", context)

@login_required
def like_unlike(request, id):
    profile=request.user.profile
    post = Post.objects.get(id=id)

    if profile in post.likes.all():
        post.likes.remove(profile)
    else:
        post.likes.add(profile)
        Notification.objects.create(sender=request.user.profile, recipient=post.owner, content=f"{post.text[:30]}", type="Like")

    return redirect(f"/post/{post.id}")

def planner(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            myform = form.save(commit=False)
            myform.owner = request.user.profile
            myform.save()
            return redirect("/")
    else:
        form = PostForm()

    context = {
        "form": form
    }
    return render(request, "planner.html", context)

@login_required
def delete_comment(request, id, cid):
    user = request.user.profile
    post = Post.objects.get(id=id)
    comment = Comment.objects.get(id=cid)

    if comment.owner == user and comment.post == post:
        comment.delete()
        return redirect(f"/post/{id}")
    
    return redirect("/error")    

@login_required
def delete_post(request, id):
    user = request.user.profile
    post = Post.objects.get(id=id)

    if post.owner == user:
        post.delete()
        return redirect("/")
    
    return redirect("/error")

@login_required
def unread_counts(request):
    """Return unread notifications and messages counts as JSON."""
    user_profile = request.user.profile

    # Adjust these according to your actual models/fields
    unread_notifications = Notification.objects.filter(recipient=user_profile, is_read=False).count()
    unread_messages = Message.objects.filter(recipient=user_profile, is_read=False).count()
    data = {
        "notifications": unread_notifications,
        "messages": unread_messages
    }
    return JsonResponse(data)

@login_required
def notifications(request):
    user_profile = request.user.profile
    notifications = Notification.objects.filter(recipient=user_profile)
    notifications.update(is_read=True)

    context = {
        "notifications": notifications
    }

    return render(request, "notifications.html", context)


