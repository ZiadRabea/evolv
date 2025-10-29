"""
URL configuration for Evolv project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Accounts.views import view_profile, edit_profile, projects, chat_room, follow_unfollow, chat_list

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chats/', chat_list),
    path('', include("main.urls")),
    path('accounts/', include("Accounts.urls")),
    path('in/<str:username>', view_profile),
    path('in/<str:username>/projects', projects, name="projects"),
    path('in/<slug:username>/chat/', chat_room, name='chat-room'),
    path('in/<slug:username>/follow/', follow_unfollow, name='follow'),
    path("update_profile", edit_profile),
    path('accounts/', include('django.contrib.auth.urls')),
    
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)