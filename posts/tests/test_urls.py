from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД для проверки доступности адреса new
        user = get_user_model().objects.create(username="Kseniya")

        Post.objects.create(text="Тестовая запись", author=user)

        Group.objects.create(title="Тестовое название группы",
                             slug="slug",
                             description="Тестовое описание группы")

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = get_user_model().objects.create(username="andrey")
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            "posts/index.html": reverse("posts:index"),
            "posts/group.html": reverse("posts:group",
                                        kwargs={"slug": "slug"}),
            "posts/new_post.html": reverse("posts:new_post"),
            "posts/profile.html": reverse("posts:profile",
                                          kwargs={"username": "Kseniya"}),
            "posts/post.html": reverse("posts:post",
                                       kwargs={
                                           "username": "Kseniya",
                                           "post_id": "1"
                                       })
        }
        for template, reverse_name in templates_url_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяем редиректы с доступными страницами для неавторизованного
    # пользователя
    def test_posts_urls_redirect_anonymous_user_accessible_pages(self):
        redirect_users = [
            reverse("posts:index"),
            reverse("posts:group", kwargs={"slug": "slug"}),
            reverse("posts:profile", kwargs={"username": "Kseniya"}),
            reverse("posts:post", kwargs={
                "username": "Kseniya",
                "post_id": "1"
            }),
        ]
        for url in redirect_users:
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    # Проверяем редиректы с недоступными страницами для неавторизованного
    # пользователя
    def test_posts_urls_redirect_anonymous_user_not_accessible_pages(self):
        redirect_users = {
            reverse("posts:new_post"):
                reverse("login") + "?next=" + reverse("posts:new_post"),
            reverse("posts:post_edit", kwargs={
                "username": "Kseniya",
                "post_id": "1"
            }):
            reverse("posts:post", kwargs={
                "username": "Kseniya",
                "post_id": "1"
            }),
        }
        for url, user_url in redirect_users.items():
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, user_url)

    # Проверяем доступность для авторизованного пользователя не автора поста
    def test_posts_urls_redirect_login_user_no_author(self):
        redirect_users = [
            reverse("posts:index"),
            reverse("posts:group", kwargs={"slug": "slug"}),
            reverse("posts:new_post"),
            reverse("posts:post_edit", kwargs={
                "username": "Kseniya",
                "post_id": "1"
            })
        ]
        for url in redirect_users:
            with self.subTest():
                response = self.authorized_client.get(url, follow=True)
                self.assertEqual(response.status_code, 200)

    # Проверяем доступность для автора поста
    def test_posts_urls_redirect_login_user_author(self):
        # Создаем пост авторизованным пользователем
        Post.objects.create(text="Тестовая запись", author=self.user)

        Group.objects.create(title="Тестовое название группы",
                             slug="slug1",
                             description="Тестовое описание группы")

        response = self.authorized_client.get(
            reverse("posts:post_edit", kwargs={
                "username": "andrey",
                "post_id": "2"
            }),
            follow=True
        )
        self.assertEqual(response.status_code, 200)

    # Проверяем возвращает ли сервер код 404, если страница не найдена
    def test_404_page_redirect_user(self):
        redirect_page = [
            reverse("posts:index") + "check_404",
            reverse("posts:group", kwargs={"slug": "slug_404"}),
            reverse("posts:new_post") + "check_404",
            reverse("posts:profile", kwargs={
                "username": "Kseniya",
            }) + "check_404",
            reverse("posts:post_edit", kwargs={
                "username": "Kseniya",
                "post_id": "1"
            }) + "check_404"
        ]
        for url in redirect_page:
            with self.subTest():
                response = self.guest_client.get(url, follow=True)
                self.assertEqual(response.status_code, 404)
