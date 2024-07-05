from notes.forms import NoteForm
from notes.tests.base import TestBase


class TestDetailPage(TestBase):

    def test_note_for_authorized_client(self):
        """Тестирование наличия заметки у автора и не автора"""
        users = (
            (self.auth_author, True),
            (self.auth_reader, False)
        )
        for user, note_in_list in users:
            response = user.get(self.url_notes_list)
            object_list = response.context['object_list']
            self.assertIs((self.note in object_list), note_in_list)

    def test_form_for_clients(self):
        """Тестируем наличие формы создания и редактирования"""
        for url in (self.url_notes_add, self.url_notes_edit):
            response = self.auth_author.get(url)
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], NoteForm)
