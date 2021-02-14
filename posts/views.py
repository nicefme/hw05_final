from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm


@cache_page(20)
def index(request):
    latest = Post.objects.all()
    paginator = Paginator(latest, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "posts/index.html", {"page": page,
                                                "paginator": paginator,
                                                "latest": latest})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "posts/group.html",
        {"group": group, "page": page, "paginator": paginator, "posts": posts}
    )


@login_required
def profile_follow(request, username):

    author = get_object_or_404(User, username=username)
    user = request.user

    if user.username == username:
        return redirect(reverse_lazy(
            "posts:profile",
            kwargs={"username": author}
        ))

    Follow.objects.get_or_create(user=user, author=author)

    return redirect(reverse_lazy(
        "posts:profile",
        kwargs={"username": author}
    ))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user

    Follow.objects.filter(user=user, author=author).delete()

    return redirect(reverse_lazy(
        "posts:profile",
        kwargs={"username": author}
    ))


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if request.method != "POST" or not form.is_valid():
        return render(request, "posts/new_post.html", {"form": form})

    post = form.save(commit=False)
    post.author = request.user

    post.save()
    return redirect(reverse_lazy("posts:index"))


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user

    latest = author.posts.all()

    paginator = Paginator(latest, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    # Функция для тестов на подписку/отписку
    following = Follow.objects.filter(author=author).count()
    if user.is_authenticated is True:
        count = Follow.objects.filter(user=user, author=author).count()
    else:
        count = 0

    if user == author or count == 0:
        db_name = None
    else:
        follow_user = Follow.objects.get(user=user, author=author)
        db_name = follow_user.author

    return render(request, "posts/profile.html", {"author": author,
                                                  "user": user,
                                                  "page": page,
                                                  "paginator": paginator,
                                                  "db_name": db_name,
                                                  "following": following})


@login_required
def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect(reverse_lazy("posts:post", kwargs={
            "username": username, "post_id": post_id
        }))

    username = request.user
    post = get_object_or_404(Post, id=post_id, author__username=username)

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if request.method != "POST" or not form.is_valid():
        return render(request, "posts/new_post.html", {"form": form,
                                                       "post_id": post_id,
                                                       "user": username,
                                                       "post": post})

    form.save()
    return redirect(reverse_lazy(
        "posts:post",
        kwargs={"username": username, "post_id": post_id}
    ))


def post_view(request, username, post_id):

    author = get_object_or_404(User, username=username)
    user = request.user

    post = get_object_or_404(Post, id=post_id, author__username=author)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)

    return render(request, "posts/post.html", {"form": form,
                                               "author": author,
                                               "user": user,
                                               "post": post,
                                               "comments": comments,
                                               "post_id": post_id})


@login_required
def add_comment(request, username, post_id):

    author = get_object_or_404(User, username=username)

    post = get_object_or_404(Post, id=post_id, author__username=author)
    form = CommentForm(request.POST or None)

    comment = form.save(commit=False)

    comment.post = post
    comment.author = request.user

    comment.save()
    return redirect(reverse_lazy(
        "posts:post",
        kwargs={"username": username, "post_id": post_id}
    ))


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def follow_index(request):

    authors = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(authors, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "posts/follow.html", {"page": page,
                                                 "paginator": paginator})
