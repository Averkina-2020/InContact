from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=30, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Введите текст',
        help_text='введите любой текст'
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Выберите группу',
        help_text='вы можете выбрать группу из списка'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        date_formated = self.pub_date.date()
        author = self.author
        text_excerpt = self.text[:30]
        result = f'{date_formated} - {author} - {text_excerpt}...'
        return result


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Введите текст',
        help_text='введите любой текст'
    )
    created = models.DateTimeField('date published', auto_now_add=True)

    def __str__(self):
        date_formated = self.created.date()
        author = self.author
        text = self.text[:30]
        result = f'{date_formated} - {author} - {text}'
        return result


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        unique_together = ("user", "author")
