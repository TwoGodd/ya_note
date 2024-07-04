from django.urls import reverse
from notes.tests.base import TestBase


class TestRoutes(TestBase):

    # def test_pages_availability(self):
    #     """Функция проверки доступов к страницам"""
    #     urls = (
    #         ('notes:home', None),
    #         ('users:login', None),
    #         ('users:logout', None),
    #         ('users:signup', None),
    #     )
    #     for name, args in urls:
    #         with self.subTest(name=name):
    #             url = reverse(name, args=args)
    #             response = self.client.get(url)
    #             self.assertEqual(response.status_code, self.http_status_ok)

    # def test_pages_availability_for_auth_user(self):
    #     """Тестирование доступности страниц для авторизованного пользователя"""
    #     urls = ('notes:list', 'notes:add', 'notes:success')
    #     for name in urls:
    #         url = reverse(name)
    #         response = self.auth_author.get(url)
    #         self.assertEqual(response.status_code, self.http_status_ok)

    def test_availability(self):
        """Тестирование доступности страниц"""
        users_statuses = (
            (self.url_notes_home, self.client, self.http_ok),
            (self.url_users_login, self.client, self.http_ok),
            (self.url_users_logout, self.client, self.http_ok),
            (self.url_users_signup, self.client, self.http_ok),
            (self.url_notes_add, self.auth_author, self.http_ok),
            (self.url_notes_list, self.auth_author, self.http_ok),
            (self.url_notes_success, self.auth_author, self.http_ok),
            (self.url_notes_detail, self.auth_author, self.http_ok),
            (self.url_notes_detail, self.auth_reader, self.http_not_found),
            (self.url_notes_edit, self.auth_author, self.http_ok),
            (self.url_notes_edit, self.auth_reader, self.http_not_found),
            (self.url_notes_delete, self.auth_author, self.http_ok),
            (self.url_notes_delete, self.auth_reader, self.http_not_found),
        )
        for url, user, status in users_statuses:
            with self.subTest():
                response = user.get(url)
                self.assertEqual(response.status_code, status)

    def test_redirect(self):
        """Тестирование редиректов"""
        urls = (
            self.url_notes_detail,
            self.url_notes_edit,
            self.url_notes_delete,
            self.url_notes_add,
            self.url_notes_success,
            self.url_notes_list,
        )
        for reversed_url in urls:
            with self.subTest():
                redirect_url = f'{self.url_users_login}?next={reversed_url}'
                response = self.client.get(reversed_url)
                self.assertRedirects(response, redirect_url)
