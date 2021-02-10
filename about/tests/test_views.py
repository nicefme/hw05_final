from django.test import Client, TestCase
from django.urls import reverse


class StaticViewsTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_page_accessible_by_name(self):
        """URL, генерируемый при помощи имени about:author(tech), доступен"""
        urls = {
            "about:author": "about/author.html",
            "about:tech": "about/tech.html",
        }

        for url in urls:
            with self.subTest():
                response = self.guest_client.get(reverse(url))
                self.assertEqual(response.status_code, 200)

    def test_about_page_uses_correct_template(self):
        """При запросе к about:author(tech) применяется правильный шаблон"""
        templates_url_names = {
            "about:author": "about/author.html",
            "about:tech": "about/tech.html",
        }

        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.guest_client.get(reverse(url))
                self.assertTemplateUsed(response, template)
