from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверят, что валидная форма создает запись в Posts."""
        post_count = Post.objects.count()
        form_data = {
            'author': self.user,
            'text': 'Тестовый текст',
        }
        self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_edit_post(self):
        """Проверят, что при отправке валидной формы
        со страницы редактирования поста,
        происходит изменение поста в базе данных."""
        form_data = {
            'author': self.user,
            'text': 'Проверка редактирования',
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.get(author=self.user).text, form_data.get('text')
        )
