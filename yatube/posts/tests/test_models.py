from django.contrib.auth import get_user_model
from django.test import TestCase
from mixer.backend.django import mixer
from testdata import wrap_testdata

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    @wrap_testdata
    def setUpTestData(cls) -> None:
        cls.user = mixer.blend(User, username='auth')
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.user)

    def test_group_model_have_correct_string_representation(self) -> None:
        """Проверяет, правильно ли отображается значение поля __str__
        в объектах модели Group"""
        self.assertEqual(self.group.title, str(self.group))

    def test_post_model_have_correct_string_representation(self) -> None:
        """Проверяет, правильно ли отображается значение поля __str__
        в объектах модели Group"""
        self.assertEqual(self.post.text[:15], str(self.post))
