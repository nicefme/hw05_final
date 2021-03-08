from django.urls import path
from . import views


app_name = "posts"

urlpatterns = [
    path("", views.index, name="index"),
    path("group/<slug:slug>/", views.group_posts, name="group"),
    path("new_group/", views.new_group, name="new_group"),
    path("new/", views.new_post, name="new_post"),
    path("follow/", views.follow_index, name="follow_index"),
    path("<str:username>/", views.profile, name="profile"),
    path("<str:username>/<int:post_id>/", views.post_view, name="post"),
    path(
        "<str:username>/<int:post_id>/edit/",
        views.post_edit,
        name="post_edit"
    ),
    path(
        "<str:username>/<int:post_id>/comment/",
        views.add_comment,
        name="add_comment"
    ),
    path(
        "<str:username>/follow/",
        views.profile_follow,
        name="profile_follow"
    ),
    path(
        "<str:username>/unfollow/",
        views.profile_unfollow,
        name="profile_unfollow"
    ),
    path(
        "<str:username>/<int:post_id>/del/",
        views.post_del,
        name="post_del"
    ),
    path(
        "<str:username>/<int:post_id>/<int:rate>/rate",
        views.post_rate,
        name="post_rate"
    ),
]
