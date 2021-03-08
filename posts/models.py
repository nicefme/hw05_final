from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name="Название группы")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Описание группы", blank=True, null=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name="Текст поста",
                            help_text="* Обязательно поле")
    pub_date = models.DateTimeField("date published", auto_now_add=True)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="posts")
    group = models.ForeignKey(Group,
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              verbose_name="Группа",
                              related_name="posts",
                              help_text="Укажите наименование группы")
    image = models.ImageField(upload_to="posts/",
                              blank=True,
                              null=True,
                              verbose_name="Изображение")
    post_rate_avg = models.FloatField(blank=True,
                                        null=True)

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ["-pub_date"]


class Comment(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(verbose_name="Комментарий",
                            help_text="Напишите ваш комментарий к посту")
    created = models.DateTimeField("date published", auto_now_add=True)

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="follower")
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name="following")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"],
                name="unique_subscriber"
            )
        ]


class PostRate(models.Model):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name="rates")
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name="rates")
    rate = models.IntegerField(blank=True,
                               null=True)