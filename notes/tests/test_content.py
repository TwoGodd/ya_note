from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestDetailPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.non_author = User.objects.create(username='Человек простой')
        cls.note = Note.objects.create(
            title='Заметка новость',
            text='Просто текст.',
            slug='notton',
            author=cls.author,
        )
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))

    def test_note_for_authorized_client(self):
        """Тестирование наличия заметки у автора и не автора"""
        url = reverse('notes:list')
        users = (
            (self.author, True),
            (self.non_author, False)
        )
        for user, note_in_list in users:
            self.client.force_login(user)
            response = self.client.get(url)
            object_list = response.context['object_list']
            self.assertIs((self.note in object_list), note_in_list)

    def test_form_for_clients(self):
        """Тестируем наличие формы создания и редактирования"""
        self.client.force_login(self.author)
        for url in (self.add_url, self.edit_url):
            response = self.client.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
