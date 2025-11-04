from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from.models import *
from.forms import *
from.filters import PostFilter
from Accounts.models import Message
from django.core.paginator import Paginator
from django.contrib import messages
# Create your views here.

def error(request):
    return render(request, "error.html")

def home(request):
    posts = Post.objects.all()
    filters = PostFilter(request.GET, queryset=posts)
    posts=filters.qs

    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
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
        "posts":page_obj,
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

def courses(request):
    premium = Course.objects.filter(is_primary=True, is_public=True).order_by('?')[:3]
    main = Course.objects.filter(is_public=True)

    context = {
        "premium_courses": premium,
        "courses": main
    }

    return render(request, "courses.html", context)


@login_required
def add_course(request):
    if request.method == "POST":
        form = CourseForm(request.POST, request.FILES)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            my_form = form.save(commit=False)
            my_form.is_public = False
            my_form.is_primary = False
            my_form.save()
            messages.success(request, 'Thank you for submitting, your course is under review and well contact you shortly')
            return redirect("/courses")
    else:
        form = CourseForm()

    context = {
        "form": form
    }
    return render(request, "add_course.html", context)


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


