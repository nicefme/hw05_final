from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Post, Group


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = get_user_model().objects.create()

        Post.objects.create(text="Тестовая запись", author=user)

        Group.objects.create(title="Тестовое название группы",
                             slug="slug",
                             description="Тестовое описание группы")

        cls.post = Post.objects.get(id=1)
        cls.group = Group.objects.get(id=1)

    def test_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            "text": "Текст поста",
            "group": "Группа"
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            "text": "* Обязательно поле",
            "group": "Укажите наименование группы",
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)

    def test_object_name_is_title_fild(self):
        """__str__  проверка отображения значения поля title"""
        group = PostModelTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))

    def test_object_name_is_text_fild(self):
        """__str__  проверка отображения значения поля text"""
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))
