import shutil
import tempfile
import datetime as dt
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.db import IntegrityError

from posts.models import Post, Group, Comment, Follow


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # Создадим запись в БД
        cls.user_0 = get_user_model().objects.create(username="AndreyTurutov",
                                                     first_name="Andrey",
                                                     last_name="Turutov")

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name="small.gif",
            content=small_gif,
            content_type="image/gif"
        )

        posts_count = 20

        new_groups = [
            Group(title=f"Тестовое название группы {post}",
                  slug=f"slug{post}",
                  description="Тестовое описание группы")
            for post in range(posts_count)
        ]

        Group.objects.bulk_create(new_groups)

        new_posts = [
            Post(text="Тестовая запись",
                 author=cls.user_0,
                 group=Group.objects.get(id=(post + 1)),
                 image=cls.uploaded)

            for post in range(posts_count)
        ]

        Post.objects.bulk_create(new_posts)

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.user = get_user_model().objects.create(username="AndreyT")
        self.authorized_client.force_login(self.user)
        # Создадим текущую дату
        self.date_now = dt.datetime.utcnow().strftime("%m/%d/%y")
        # Чистим cache перед запуском каждого теста
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: name"

        templates_pages_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group.html": reverse("posts:group",
                                        kwargs={"slug": "slug1"}),
            "posts/new_post.html": reverse("posts:new_post"),
        }

        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_new_post_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:new_post"))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем, что словарь context главной страницы
    # содержит ожидаемые значения
    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:index"))
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_post = response.context.get("page")[0]
        show_context = {
            first_post.text: "Тестовая запись",
            first_post.author.first_name: "Andrey",
            first_post.author.last_name: "Turutov",
            first_post.pub_date.strftime("%m/%d/%y"): self.date_now,
            len(first_post.image): len(self.uploaded),
        }

        for value, expected in show_context.items():
            with self.subTest():
                self.assertEqual(value, expected)

    # Проверяем, что словарь context страницы group/slug1
    # содержит ожидаемые значения
    def test_group_detail_pages_show_correct_context(self):
        """Шаблон group сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse("posts:group",
                                              kwargs={"slug": "slug1"}))

        take_group = response.context.get("group")
        take_first_post = response.context.get("page")[0]
        show_context = {
            take_group.title: "Тестовое название группы 1",
            take_group.slug: "slug1",
            take_group.description: "Тестовое описание группы",
            len(take_first_post.image): len(self.uploaded),
        }

        for value, expected in show_context.items():
            with self.subTest():
                self.assertEqual(value, expected)

    def test_first_page_containse_ten_records(self):
        response = self.authorized_client.get(reverse("posts:index"))
        # Проверка: количество постов на первой странице равно 10.

        self.assertEqual(len(response.context.get("page").object_list), 10)

    def test_second_page_containse_three_records(self):
        # Проверка: на второй странице должно быть 10 постов.
        response = self.authorized_client.get(
            reverse("posts:index") + "?page=2"
        )
        self.assertEqual(len(response.context.get("page").object_list), 10)

    # Проверяем, что словарь context страницы /<username>/
    # содержит ожидаемые значения
    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            "posts:profile",
            kwargs={"username": "AndreyTurutov"}
        ))

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        first_post = response.context.get("page")[0]
        show_context = {
            first_post.text: "Тестовая запись",
            first_post.author.username: "AndreyTurutov",
            first_post.author.first_name: "Andrey",
            first_post.author.last_name: "Turutov",
            first_post.pub_date.strftime("%m/%d/%y"): self.date_now,
            len(first_post.image): len(self.uploaded),
        }

        for value, expected in show_context.items():
            with self.subTest():
                self.assertEqual(value, expected)

    # Проверяем, что словарь context страницы /<username>/<post_id>/
    # содержит ожидаемые значения
    def test_post_page_show_correct_context(self):
        """Шаблон post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            "posts:post",
            kwargs={"username": "AndreyTurutov", "post_id": "1"}
        ))

        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        show_context = {
            response.context.get("post").text: "Тестовая запись",
            response.context.get("post").author.username: "AndreyTurutov",
            response.context.get("post").author.first_name: "Andrey",
            response.context.get("post").author.last_name: "Turutov",
            response.context.get("post").pub_date.strftime("%m/%d/%y"):
                (self.date_now),
            len(response.context.get("post").image): len(self.uploaded),
        }

        for value, expected in show_context.items():
            with self.subTest():
                self.assertEqual(value, expected)

    # Проверяем, что словарь context страницы /<username>/<post_id>/edit/
    # содержит ожидаемые значения
    def test_post_edit_correct_context(self):
        """Шаблон new_post сформирован с правильным контекстом."""
        # Создаем пост авторизованным пользователем
        Post.objects.create(text="Тестовая запись",
                            author=self.user,
                            image=self.uploaded)

        Group.objects.create(title="Тестовое название группы",
                             slug="slug21",
                             description="Тестовое описание группы")

        response = self.authorized_client.get(reverse(
            "posts:post_edit",
            kwargs={"username": "AndreyT", "post_id": "21"}))
        # Список ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            "group": forms.fields.ChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }
        # Проверяем, что типы полей формы в словаре context
        # соответствуют ожиданиям
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get("form").fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    # Проверяем кеширование главной страницы index.html
    def test_cash_home_page(self):
        """Шаблон index кеширует главную страницу"""
        # Зайдем на главную страницу первый раз
        response = self.authorized_client.get(reverse("posts:index"))
        Post.objects.create(text="Тестовая запись для кеша",
                            author=self.user)
        # Зайдем на главную страницу второй раз
        response = self.authorized_client.get(reverse("posts:index"))
        context_none = response.context
        # Проверим, что шаблоны двух страниц одинаковые

        self.assertIsNone(context_none)
        # Чистим cache и проверяем что контекст появился
        cache.clear()

        # Зайдем на главную страницу третий раз
        response = self.authorized_client.get(reverse("posts:index"))
        context_none = response.context.get("post").text
        self.assertEqual(context_none, "Тестовая запись для кеша")

    def test_follower_is_follow(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок"""

        self.authorized_client.get(reverse(
            "posts:profile",
            kwargs={"username": "AndreyTurutov"}))

        # Подпишем пользователя на автора поста
        follow = Follow.objects.create(user=self.user, author=self.user_0)

        # Отпишем пользователя от автора поста
        unfollow = Follow.objects.all()
        unfollow.delete()
        unfollow = Follow.objects.all().count()

        un_or_follow_tab = {
            follow.author.username: "AndreyTurutov",
            follow.user.username: "AndreyT",
            unfollow: 0
        }

        for value, expected in un_or_follow_tab.items():
            with self.subTest(self):
                self.assertEqual(value, expected)

    def test_follow_feed(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан на него"""

        # Создаем авторизованный клиент, который не будет подписан на автора
        authorized_client_1 = Client()
        user_2 = get_user_model().objects.create(username="Iliya")
        authorized_client_1.force_login(user_2)

        # Подпишем пользователя на автора поста
        Follow.objects.create(user=self.user, author=self.user_0)

        # Создадим новый пост автором
        Post.objects.create(text="Тестовая запись follow",
                            author=self.user_0,
                            image=self.uploaded)

        response = self.authorized_client.get(reverse("posts:follow_index"))
        test_text = response.context.get("page")[0].text

        response = authorized_client_1.get(reverse("posts:follow_index"))
        len_text = response.context.get("page")

        un_or_follow = {
            test_text: "Тестовая запись follow",
            len(len_text): 0
        }

        for value, expected in un_or_follow.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)

    def test_comment_correct_context(self):
        """Только авторизированный пользователь может комментировать посты"""
        # Проверка comment для авторизованного и неавторизованного пользователя
        post = Post.objects.get(pk=1)

        # Создадим комментарий авторизованным пользователем
        Comment.objects.create(post=post,
                               author=self.user,
                               text="Текс комментария")

        # Проверим, что у поста появился комментарий авторизованного
        # пользователя
        # Зайдем на страницу поста авторизованным пользователем
        response_login = self.authorized_client.get(reverse(
            "posts:post",
            kwargs={"username": "AndreyTurutov", "post_id": "1"}
        ))

        comment_1 = response_login.context.get("comments")[0].text

        try:
            Comment.objects.create(post=post,
                                   author=None,
                                   text="Текс комментария 2")
            comment_2 = response_login.context.get("comments")[0].text
        except IntegrityError:
            comment_2 = "Комментарий не создан"

        comments = {
            comment_1: "Текс комментария",
            comment_2: "Комментарий не создан",
        }

        for value, expected in comments.items():
            with self.subTest(value=value):
                self.assertEqual(value, expected)
