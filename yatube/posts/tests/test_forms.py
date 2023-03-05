from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from faker import Faker
from mixer.backend.django import mixer

from ..models import Group, Post

User = get_user_model()
fake = Faker()


class PostFormTests(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = mixer.blend(User, username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_post(self) -> None:
        """Проверяет, что валидная форма создает запись в Posts."""
        data = {
            'text': fake.pystr(),
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=data, follow=True
        )
        self.assertEqual(Post.objects.count(), 1)

    def test_edit_post(self) -> None:
        """Проверяет, что при отправке валидной формы
        со страницы редактирования поста,
        происходит изменение поста в базе данных."""
        groups = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=self.user, group=groups[0])
        data = {'text': fake.pystr(), 'group': groups[1].id}
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.get(author=self.user).text, data.get('text')
        )
        self.assertEqual(
            Post.objects.get(author=self.user).group.id, data.get('group')
        )

    def test_anonym_create_post(self) -> None:
        """Проверяет, что анонимный пользователь не создает запись в Posts."""
        data = {
            'text': fake.pystr(),
        }
        self.client.post(reverse('posts:post_create'), data=data, follow=True)
        self.assertEqual(Post.objects.count(), 0)

    def test_anonym_edit_post(self) -> None:
        """Проверяет, что анонимный пользователь
        не может редактировать пост."""
        groups = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=self.user, group=groups[0])
        data = {'text': fake.pystr(), 'group': groups[1].id}
        self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=data,
            follow=True,
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).text, data.get('text')
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).group.id, data.get('group')
        )

    def test_not_auhtor_edit_post(self) -> None:
        """Проверяет, что пользователь, не являющийся автором,
        не может редактировать пост."""
        user = mixer.blend(User, username='auth1')
        new_authorized_client = Client()
        new_authorized_client.force_login(user)
        groups = mixer.cycle(2).blend(Group)
        post = mixer.blend(Post, author=self.user, group=groups[0])
        data = {'text': fake.pystr(), 'group': groups[1].id}
        new_authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=data,
            follow=True,
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).text, data.get('text')
        )
        self.assertNotEqual(
            Post.objects.get(author=self.user).group.id, data.get('group')
        )
