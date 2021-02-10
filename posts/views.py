from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist

from .models import Post, Group, User, Follow
from .forms import PostForm, CommentForm, FollowForm


@cache_page(20)
def index(request):
    # одна строка вместо тысячи слов на SQL
    latest = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(latest, 10)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    # собираем тексты постов в один, разделяя новой строкой

    return render(request, "posts/index.html", {"page": page,
                                                "paginator": paginator,
                                                "latest": latest})


def group_posts(request, slug):
    # функция get_object_or_404 получает по заданным критериям объект из базы
    # данных или возвращает сообщение об ошибке, если объект не найден
    group = get_object_or_404(Group, slug=slug)

    posts = group.posts.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(posts, 10)
    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get("page")
    # Получаем набор записей для страницы с запрошенным номером
    page = paginator.get_page(page_number)
    # собираем тексты постов в один, разделяя новой строкой

    return render(
        request,
        "posts/group.html",
        {"group": group, "page": page, "paginator": paginator, "posts": posts}
    )


@login_required
def profile_follow(request, username):

    author = get_object_or_404(User.objects.select_related(),
                               username=username)
    user = request.user
    try:
        follow_user = Follow.objects.get(user=user, author=author)
        name = follow_user.author
    except ObjectDoesNotExist:
        follow_user = ""
        name = follow_user

    if request.user.username == username or name == author:
        return redirect(reverse_lazy("posts:profile", kwargs={
           "username": author
        }))

    form = FollowForm(request.POST or None)
    follow = form.save(commit=False)

    follow.author = author
    follow.user = user

    follow.save()
    return redirect(reverse_lazy("posts:profile", kwargs={
           "username": author
        }))


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User.objects.select_related(),
                               username=username)
    user = request.user

    unfollow = Follow.objects.get(user=user, author=author)

    unfollow.delete()
    return redirect(reverse_lazy("posts:profile", kwargs={
           "username": author
        }))


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if request.method != "POST" or not form.is_valid():
        form = PostForm()
        return render(request, "posts/new_post.html", {"form": form})

    # Мы используем ModelForm, а его метод save() возвращает инстанс
    # модели, связанный с формой. Аргумент commit=False говорит о том,
    # что записывать модель в базу рановато.
    post = form.save(commit=False)

    # Теперь, когда у нас есть несохранённая модель, можно добавить записи,
    # Т.к. форма уже знает как сохранять модель, то кроме автора ничего не надо
    post.author = request.user

    # А теперь можно сохранить в базу
    post.save()
    return redirect(reverse_lazy("posts:index"))


def profile(request, username):
    author = get_object_or_404(User.objects.select_related(),
                               username=username)
    user = request.user

    latest = author.posts.all()

    paginator = Paginator(latest, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    try:
        follow_user = Follow.objects.get(user=user, author=author)
        db_name = follow_user.author
    except TypeError:
        db_name = "0"
    except ObjectDoesNotExist:
        db_name = "0"

    return render(request, "posts/profile.html", {"author": author,
                                                  "user": user,
                                                  "page": page,
                                                  "paginator": paginator,
                                                  "db_name": db_name})


def post_edit(request, username, post_id):
    if request.user.username != username:
        return redirect(reverse_lazy("posts:post", kwargs={
            "username": username, "post_id": post_id
        }))

    username = request.user
    post = get_object_or_404(Post, author=username, id=post_id)
    date = post.pub_date

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if request.method != "POST" or not form.is_valid():
        return render(request, "posts/new_post.html", {"form": form,
                                                       "post_id": post_id,
                                                       "user": username,
                                                       "post": post})

    post = form.save(commit=False)

    article = Post.objects.get(author=username, pk=post_id, pub_date=date)
    post = PostForm(request.POST, request.FILES, instance=article)

    post.save()
    return redirect(reverse_lazy(
        "posts:post",
        kwargs={"username": username, "post_id": post_id}
    ))


def post_view(request, username, post_id):

    author = get_object_or_404(User.objects.select_related(),
                               username=username)
    user = request.user

    post = get_object_or_404(Post, id=post_id, author=author)
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

    author = get_object_or_404(User.objects.select_related(),
                               username=username)

    post = get_object_or_404(Post, id=post_id, author=author)
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
    # Переменная exception содержит отладочную информацию,
    # выводить её в шаблон пользователской страницы 404 мы не станем
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
