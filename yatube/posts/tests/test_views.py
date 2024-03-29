from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from mixer.backend.django import mixer
from yatube.settings import NOTES_NUMBER

from ..models import Group, Post

User = get_user_model()


class PostUrlTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = mixer.blend(User, username='auth')
        cls.group = mixer.blend(Group)
        cls.post = mixer.blend(Post, author=cls.user, group=cls.group)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_pages_uses_correct_template(self) -> None:
        """Проверяет, что view-функция использует соответствующий шаблон."""
        pages_names_templates = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ): 'posts/group_list.html',
            (
                reverse(
                    'posts:profile', kwargs={'username': self.user.username}
                )
            ): 'posts/profile.html',
            (
                reverse('posts:post_detail', kwargs={'post_id': self.post.id})
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (
                reverse('posts:post_edit', kwargs={'post_id': self.post.id})
            ): 'posts/create_post.html',
        }
        for reverse_name, template in pages_names_templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_show_correct_recors_count(self) -> None:
        """Проверяет паджинатор на странице."""
        mixer.cycle(13).blend(Post, author=self.user, group=self.group)
        pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for page in pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(
                    len(response.context['page_obj']), NOTES_NUMBER
                )

    def test_index_page_show_correct_context(self) -> None:
        """Проверяет, что шаблон index сформирован с правильным контекстом."""
        response = self.client.get(reverse("posts:index"))
        expected = list(Post.objects.all()[:NOTES_NUMBER])
        self.assertEqual(
            response.context.get('page_obj').object_list, expected
        )

    def test_group_list_page_show_correct_context(self) -> None:
        """Проверяет, что шаблон group_list сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        expected = list(Post.objects.filter(group=self.group)[:NOTES_NUMBER])
        self.assertEqual(
            response.context.get('page_obj').object_list, expected
        )

    def test_profile_page_show_correct_context(self) -> None:
        """Проверяет, что шаблон profile сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        expected = list(Post.objects.filter(author=self.user)[:NOTES_NUMBER])
        self.assertEqual(
            response.context.get('page_obj').object_list, expected
        )

    def test_post_detail_page_show_correct_context(self) -> None:
        """Проверяет, что шаблон post_detail сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        expected = Post.objects.get(id=self.post.id)
        self.assertEqual(response.context.get('post'), expected)

    def test_post_create_page_show_correct_context(self) -> None:
        """Проверяет, что шаблон post_create сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self) -> None:
        """Проверяет, что шаблон post_edit сформирован
        с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_is_on_pages_if_has_group(self) -> None:
        """Проверяет, что если при создании поста указать группу,
        то этот пост появляется на странице"""
        pages_objects = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            (
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ): Post.objects.get(group=self.post.group),
            (
                reverse(
                    'posts:profile', kwargs={'username': self.user.username}
                )
            ): Post.objects.get(group=self.post.group),
        }
        for page, object in pages_objects.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertIn(object, response.context.get('page_obj'))

    def test_post_is_not_on_another_group_page(self) -> None:
        """Проверяет, что пост не попал в группу,
        для которой не был предназначен."""
        mixer.blend(Group, slug='test-slug2')
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug2'})
        )
        self.assertNotEqual(response.context.get('group'), self.post.group)
