import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        # Создаем неавторизованный клиент
        cls.guest_client = Client()
        # Создаем авторизованый клиент
        cls.user = User.objects.create_user(username='user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # Создадим группу в БД
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы'
        )
        # Создадим пост в БД
        cls.post = Post.objects.create(
            text='Тестовая запись',
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()
        cache.clear()

    @classmethod
    # Удаление временной папки
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_create_post_with_image(self):
        """Валидная форма создает запись"""
        # Создаём подобие картинки
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='small/gif'
        )
        # Подсчитаем количество записей
        posts_count = Post.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
            'author': self.user,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostCreateFormTests.user})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с нашим слагом
        last_obj = Post.objects.all().latest('pk')
        self.assertEqual(last_obj.author, form_data['author'])
        self.assertEqual(last_obj.text, form_data['text'])
        self.assertEqual(last_obj.group.pk, form_data['group'])
        self.assertEqual(last_obj.image, f'posts/{uploaded}')

    def test_authorized_edit_post(self):
        """Редактирование записи создателем поста"""
        # Проверяем, что авторизованный пользователь
        # может редактировать пост
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.pk,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.group.pk)
        self.client.get(f'/posts/{post_edit.pk}/edit/')
        form_data = {
            'text': 'Измененный текст поста',
            'group': self.group.pk
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={
                        'post_id': post_edit.pk
                    }),
            data=form_data,
            follow=True,
        )
        post_edit = Post.objects.get(pk=self.group.pk)
        self.assertEqual(response_edit.status_code, 200)
        self.assertEqual(post_edit.text, 'Измененный текст поста')
        # Проверка редиректа на страницу поста
        self.assertRedirects(response_edit, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk}))
