from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestBase(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.client = Client()
        cls.auth_author = cls.client
        cls.auth_author.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_reader = cls.client
        cls.auth_reader.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author,
        )
        cls.http_status_ok = 200
        cls.http_status_not_found = 404
        cls.url_notes_home = reverse('notes:home')
        cls.url_notes_list = reverse('notes:list')
        cls.url_notes_detail = reverse('notes:detail', args=(cls.note.slug,))
        cls.url_notes_add = reverse('notes:add')
        cls.url_notes_success = reverse('notes:success')
        cls.url_notes_edit = reverse('notes:edit', args=(cls.note.slug,))
        cls.url_notes_delete = reverse('notes:delete', args=(cls.note.slug,))
        cls.url_users_login = reverse('users:login')
        cls.url_users_logout = reverse('users:logout')
        cls.url_users_signup = reverse('users:signup')
