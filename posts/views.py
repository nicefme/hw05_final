from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .models import Post, Group, User
from .forms import PostForm, CommentForm

#@cache_page(20)
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
    login_user = request.user

    latest = author.posts.all()
    count = latest.count()

    paginator = Paginator(latest, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(request, "posts/profile.html", {"name": author,
                                                  "login_user": login_user,
                                                  "page": page,
                                                  "count": count,
                                                  "paginator": paginator})


def post_edit(request, username, post_id):
   # user_page = username

    if request.user.username != username:
        return redirect(reverse_lazy("posts:post", kwargs={
            "username": username, "post_id": post_id
        }))

    username = request.user
   # post_id = post_id
    post = get_object_or_404(Post, author=username, id=post_id)
    date = post.pub_date

    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)

    if request.method != "POST" or not form.is_valid():
        return render(request, "posts/new_post.html", {"form": form,
                                                       "post_id": post_id,
                                                       "user": username,
                                                      # "username": username,
                                                       "post": post, })

    post = form.save(commit=False)

    article = Post.objects.get(author=username, pk=post_id, pub_date=date)
    post = PostForm(request.POST, request.FILES, instance=article)

    # А теперь можно сохранить в базу
    post.save()
    return redirect(reverse_lazy(
        "posts:post",
        kwargs={"username": username, "post_id": post_id}
    ))

def post_view(request, username, post_id):
    
    author = get_object_or_404(User.objects.select_related(),
                               username=username)
    user = request.user

    posts = author.posts.all()
    count = posts.count()
    
    post = get_object_or_404(Post, id=post_id, author=author)
    comments = post.comments.all()
    form = CommentForm(request.POST or None)
    
    if request.method != "POST" or not form.is_valid():
        return render(request, "posts/post.html", {"form": form,
                                                   "name": author,
                                                   "user": user,
                                                   "post": post,
                                                   "count": count, 
                                                   "comments": comments,
                                                   })

    comment = form.save(commit=False)

    comment.post = post
    comment.author = request.user

   # article = Comment.objects.get(post=post, author=request.user)
   # comment = CommentForm(request.POST, instance=article)
    comment.save()

    return redirect(reverse_lazy(
        "posts:add_comment",
        kwargs={"username": username, "post_id": post_id}
    ))


def add_comment(request, username, post_id):

   # author = get_object_or_404(User.objects.select_related(),
   #                            username=username)
 #   post = get_object_or_404(Post, id=post_id, author__username=username)

  #  form = CommentForm(request.POST or None)
    #if form.is_valid():
 #   comment = form.save(commit=False)

 #   comment.post = post
 #   comment.author = request.user
 #   comment.save()
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
