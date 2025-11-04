from .models import *
from main.models import Notification
# Create your views here.
from django.db.models import OuterRef, Subquery, Q
from django.db.models.functions import Coalesce, Now
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .forms import SignUP, ProfileForm, ProjectForm, UserForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

def sign_up(request):
    if request.method == 'POST':
        Form = SignUP(request.POST)
        if Form.is_valid():
            Form.save()
            username = Form.cleaned_data['username']
            password = Form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect(f'/update_profile')
    else:
        Form = SignUP()
    return render(request, 'registration/sign_up.html', {'form': Form})


def view_profile(request, username):
    profile = Profile.objects.get(slug = username)

    if request.method == "POST":
        if request.user.profile == profile:
            form = ProjectForm(request.POST, request.FILES)

            if form.is_valid():
                myform = form.save(commit=False)
                myform.owner = profile
                myform.save()
        else:
            return redirect("/Error")
    else:
        form = ProjectForm()
    try:
        post = profile.post_set.latest("date") 
    except: 
        post = None 

    context = {
        "profile":profile,
        "form": form,
        "post": post
    }

    return render(request, "profile.html", context)

@login_required
def edit_profile(request):
    if request.method == "POST":
        userform = UserForm(request.POST, request.FILES, instance=request.user)
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        
        if form.is_valid() and userform.is_valid():
            userform.save()
            form.save()
            return redirect(f"/in/{request.user.profile.slug}")
    else:
        form = ProfileForm(instance=request.user.profile)
        userform = UserForm(instance=request.user)
    
    context = {
        "userform" : userform,
        "profileform": form
    }

    return render(request, "edit_profile.html", context)

def projects(request, username):
    profile = Profile.objects.get(slug=username)

    context = {
        "profile" : profile
    }

    return render(request, "projects.html", context)  

@login_required
def chat_room(request, username):
    other_profile = get_object_or_404(Profile, slug=username)
    user_profile = request.user.profile
    user_profile.chats.add(other_profile)
    other_profile.chats.add(user_profile)
    # Fetch all messages between these two
    messages = Message.objects.filter(
        sender__in=[user_profile, other_profile],
        recipient__in=[user_profile, other_profile]
    ).order_by('timestamp')
    messages.update(is_read=True)

    context = {
        'other_profile': other_profile,
        'messages': messages,
    }
    return render(request, 'Accounts/chat_room.html', context)


@login_required
def send_message(request, username):
    if request.method == "POST":
        other_profile = get_object_or_404(Profile, slug=username)
        sender = request.user.profile
        content = request.POST.get('message', '').strip()

        if content:
            msg = Message.objects.create(sender=sender, recipient=other_profile, content=content)
            return JsonResponse({
                'sender': sender.user.username,
                'content': msg.content,
                'timestamp': msg.timestamp.strftime("%H:%M"),
            })
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def follow_unfollow(request, username):
    user = request.user.profile
    profile = Profile.objects.get(slug=username)

    if user == profile:
        return redirect("/error")
    if user in profile.followers.all():
        profile.followers.remove(user)
        user.following.remove(profile)
    else:
        profile.followers.add(user)
        user.following.add(profile)
        Notification.objects.create(sender=user, recipient=profile, type="Follow", content="Started following you.")
    
    return redirect(f"/in/{profile.slug}")

@login_required
def chat_list(request):
    user = request.user.profile

    chats = user.chats.all()

    last_msg_subquery = Message.objects.filter(
        Q(sender=user, recipient=OuterRef('pk')) |
        Q(sender=OuterRef('pk'), recipient=user)
    ).order_by('-timestamp')

    chats = chats.annotate(
        last_message_content=Subquery(last_msg_subquery.values('content')[:1]),
        last_message_time=Subquery(last_msg_subquery.values('timestamp')[:1]),
        last_message_sender_id=Subquery(last_msg_subquery.values('sender_id')[:1]),
        last_message_is_read=Subquery(last_msg_subquery.values('is_read')[:1]),
    ).order_by(Coalesce('last_message_time', Now()).desc())

    return render(request, 'chats.html', {'chatlist': chats, 'user_profile': user})
