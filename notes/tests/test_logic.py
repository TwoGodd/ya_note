from notes.forms import WARNING
from notes.models import Note
from notes.tests.base import TestBase
from pytils.translit import slugify


class TestCreateLogic(TestBase):
    def test_user_can_create_note(self):
        """Тестирование возможности создания заметки авториз. пользователем"""
        Note.objects.get().delete()
        response = self.auth_author.post(self.url_notes_add,
                                         data=self.form_data)
        self.assertRedirects(response, self.url_notes_success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get(slug=self.form_data['slug'])
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, self.form_data['slug'])
        self.assertEqual(new_note.author, self.author)

    def test_anonymous_user_cant_create_note(self):
        """Тестирование невозможности создания заметки анон. пользователем"""
        count_before_test = Note.objects.count()
        response = self.client.post(self.url_notes_add, data=self.form_data)
        expected_url = f'{self.url_users_login}?next={self.url_notes_add}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), count_before_test)

    def test_empty_slug(self):
        """Тестирование логики slug: подстановка значения в пустое поле"""
        Note.objects.get().delete()
        self.form_data.pop('slug')
        response = self.auth_author.post(self.url_notes_add,
                                         data=self.form_data)
        self.assertRedirects(response, self.url_notes_success)
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(new_note.slug, expected_slug)

    def test_not_unique_slug(self):
        """Тестирование логики slug: проверка уникальности"""
        count_before_test = Note.objects.count()
        self.form_data['slug'] = self.note.slug
        response = self.auth_author.post(self.url_notes_add,
                                         data=self.form_data)
        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        self.assertEqual(Note.objects.count(), count_before_test)

    def test_author_can_edit_note(self):
        """Тестирование редактирования заметки автором"""
        response = self.auth_author.post(self.url_notes_edit,
                                         self.form_data)
        self.assertRedirects(response, self.url_notes_success)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.form_data['title'])
        self.assertEqual(self.note.text, self.form_data['text'])
        self.assertEqual(self.note.slug, self.form_data['slug'])

    def test_other_user_cant_edit_note(self):
        """Тестирование редактирования заметки не автором"""
        response = self.auth_reader.post(self.url_notes_edit,
                                         self.form_data)
        self.assertEqual(response.status_code, self.http_not_found)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(self.note.title, note_from_db.title)
        self.assertEqual(self.note.text, note_from_db.text)
        self.assertEqual(self.note.slug, note_from_db.slug)

    def test_author_can_delete_note(self):
        """Тестирование редактирования заметки автором"""
        response = self.auth_author.post(self.url_notes_delete)
        self.assertRedirects(response, self.url_notes_success)
        self.assertEqual(Note.objects.count(), 0)

    def test_other_user_cant_delete_note(self):
        """Тестирование редактирования заметки не автором"""
        response = self.auth_reader.post(self.url_notes_delete)
        self.assertEqual(response.status_code, self.http_not_found)
        self.assertEqual(Note.objects.count(), 1)
