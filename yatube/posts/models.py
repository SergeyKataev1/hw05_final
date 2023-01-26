from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):

    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Уникальная страница группы'
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    class Meta:
        verbose_name_plural = 'Группы'
        verbose_name = 'Группа'

    def __str__(self) -> str:
        return self.title


class Post(models.Model):

    text = models.TextField(
        verbose_name='Текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )

    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date', )
        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя автора',
    )
    text = models.TextField(
        max_length=300,
        verbose_name='Текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'], name='unique_following'
            )
        ]
