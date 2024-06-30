from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from notes.forms import WARNING
from notes.models import Note
from pytils.translit import slugify

User = get_user_model()


class TestCreateLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        """Тестирование возможности создания заметки авториз. пользователем"""
        url = reverse('notes:add')
        response = self.auth_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Тестирование невозможности создания заметки анон. пользователем"""
        url = reverse('notes:add')
        response = self.client.post(url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_empty_slug(self):
        """Тестирование логики slug: подстановка значения в пустое поле"""
        url = reverse('notes:add')
        self.form_data.pop('slug')
        response = self.auth_author.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)


class TestEditLogic(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.reader = User.objects.create(username='Читатель простой')
        cls.auth_reader = Client()
        cls.auth_reader.force_login(cls.reader)
        cls.author = User.objects.create(username='Лев Толстой')
        cls.auth_author = Client()
        cls.auth_author.force_login(cls.author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='note-slug',
            author=cls.author,
        )
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_not_unique_slug(self):
        """Тестирование логики slug: проверка уникальности"""
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.auth_author.post(url, data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Тестирование редактирования заметки автором"""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_author.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Тестирование редактирования заметки не автором"""
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.auth_reader.post(url, self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Тестирование редактирования заметки автором"""
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_author.post(url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Тестирование редактирования заметки не автором"""
        url = reverse('notes:delete', args=(self.note.slug,))
        response = self.auth_reader.post(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
