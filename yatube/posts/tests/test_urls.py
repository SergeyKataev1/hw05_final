from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title="Тестовая заголовок",
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.pk}
            ): 'posts/post_create.html',
        }
        for url, template, in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
                self.assertEqual(response.status_code, 200)

    def test_urls_for_guest(self):
        """Страницы главная, группы, профиль и детальная информация о посте
         доступны неавторизованному клиенту"""
        url_names = {
            '/',
            f'/group/{self.group.slug}/',
            f'/profile/{self.user.username}/',
            f'/posts/{self.post.pk}/',
        }
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_create_and_post_edit_for_authorized(self):
        """Страницы create и post_edit недоступны неавторизованному клиенту"""
        url_names = {
            '/create/',
            f'/posts/{self.post.pk}/edit/',
        }
        for url in url_names:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, 302)

    def test_create_url_redirect_guest(self):
        """Страница /create/ перенаправляет неавторизованного клиента
        на страницу авторизации."""
        response = self.guest_client.get(reverse('posts:post_create'))
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_post_edit_url_redirect_guest(self):
        """Страница posts/post_id/edit/ перенаправляет
         неавторизованного клиента на страницу авторизации."""
        response = self.guest_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': self.post.pk}
        ))
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.pk}/edit/')

    def test_wrong_uri_returns_404(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
