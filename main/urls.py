from django.urls import path
from.views import *
urlpatterns = [
    path('', home, name="home"),
    path('error', error, name="error"),
    path('planner', planner, name="planner"),
    path('notifications', notifications),
    path('post/<int:id>', post, name="post"),
    path('post/<int:id>/like', like_unlike, name="like_unlike"),
    path('post/<int:id>/delete', delete_post, name="delete_post"),
    path('post/<int:id>/comment/<int:cid>/delete', delete_comment, name="delete_post"),
    path('api/unread_counts/', unread_counts, name='unread_counts'),
    path('courses', courses, name="courses"),
    path('courses/add', add_course, name="add_course"),
]