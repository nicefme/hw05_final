import shutil
import tempfile
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.models import Post, Group


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем временную папку для медиа-файлов;
        # на момент теста медиа папка будет перопределена
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

        # Создаем запись в базе данных для проверки сушествующего slug
        user = get_user_model().objects.create(username="AndreyTurutov",
                                               first_name="Andrey",
                                               last_name="Turutov")

        Post.objects.create(text="Тестовая запись", author=user)

        Group.objects.create(title="Тестовое название группы",
                             slug="slug",
                             description="Тестовое описание группы")

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorized_client = Client()
        self.user = get_user_model().objects.create(username="AndreyT")
        self.authorized_client.force_login(self.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        # Модуль shutil - библиотека Python с прекрасными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок|файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post(self):
        """Валидная форма создает запись в базе данных."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()

        form_data = {
            "title": "Тестовое название группы",
            "text": "Тестовая запись",
            "image": self.uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse("posts:new_post"),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse("posts:index"))
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        """Валидная форма редактирует запись в базе данных."""
        # Подсчитаем количество записей в Post
        posts_count = Post.objects.count()

        # Создадим в БД запись авторизованного пользователя
        Post.objects.create(text="Тестовая запись", author=self.user,)

        Group.objects.create(title="Тестовое название группы",
                             slug="slug1",
                             description="Тестовое описание группы")

        form_data = {
            "group": Group.objects.filter(id=2).update(
                title="Тестовое название группы new"
            ),
            "text": "Тестовая запись new",
            "image": self.uploaded,
        }
        # Отправляем POST-запрос с корректировкой поста
        response = self.authorized_client.post(
            reverse("posts:post_edit", kwargs={"username": "AndreyT",
                                               "post_id": "2"}),
            data=form_data,
        )

        # Проверяем, поменялся текст, изображение и название группы
        self.assertEqual(Post.objects.get(id=2).text, "Тестовая запись new")
        self.assertEqual(
            Group.objects.get(id=2).title,
            "Тестовое название группы new"
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(
            response,
            reverse("posts:post",
                    kwargs={"username": "AndreyT", "post_id": "2"})
        )
        # Проверяем, увеличилось ли число постов после добавления и
        # редактирования
        self.assertEqual(Post.objects.count(), posts_count + 1)
