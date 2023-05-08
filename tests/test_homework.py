import re
import tempfile

import pytest
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.db.models import fields

try:
    from posts.models import Post
except ImportError:
    assert False, 'Не найдена модель Post'


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None


def search_refind(execution, user_code):
    """Поиск запуска"""
    for temp_line in user_code.split('\n'):
        if re.search(execution, temp_line):
            return True
    return False


class TestPost:

    def test_post_model(self):
        model_fields = Post._meta.fields
        text_field = search_field(model_fields, 'text')
        assert text_field is not None, 'Добавьте название события `text` модели `Post`'
        assert type(text_field) == fields.TextField, \
            'Свойство `text` модели `Post` должно быть текстовым `TextField`'

        pub_date_field = search_field(model_fields, 'pub_date')
        assert pub_date_field is not None, 'Добавьте дату и время проведения события `pub_date` модели `Post`'
        assert type(pub_date_field) == fields.DateTimeField, \
            'Свойство `pub_date` модели `Post` должно быть датой и время `DateTimeField`'
        assert pub_date_field.auto_now_add, 'Свойство `pub_date` модели `Post` должно быть `auto_now_add`'

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, 'Добавьте пользователя, автор который создал событие `author` модели `Post`'
        assert type(author_field) == fields.related.ForeignKey, \
            'Свойство `author` модели `Post` должно быть ссылкой на другую модель `ForeignKey`'
        assert author_field.related_model == get_user_model(), \
            'Свойство `author` модели `Post` должно быть ссылкой на модель пользователя `User`'

        image_field = search_field(model_fields, 'image')
        assert image_field is not None, 'Добавьте свойство `image` в модель `Post`'
        assert type(image_field) == fields.files.ImageField, \
            'Свойство `image` модели `Post` должно быть `ImageField`'
        assert image_field.upload_to == 'posts/', \
            "Свойство `image` модели `Post` должно быть с атрибутом `upload_to='posts/'`"

    @pytest.mark.django_db(transaction=True)
    def test_post_create(self, user):
        text = 'Тестовый пост'
        author = user

        assert Post.objects.all().count() == 0

        image = tempfile.NamedTemporaryFile(suffix=".jpg").name
        post = Post.objects.create(text=text, author=author, image=image)
        assert Post.objects.all().count() == 1
        assert Post.objects.get(text=text, author=author).pk == post.pk

    def test_post_admin(self):
        admin_site = site

        assert Post in admin_site._registry, 'Зарегестрируйте модель `Post` в админской панели'

        admin_model = admin_site._registry[Post]

        assert 'text' in admin_model.list_display, \
            'Добавьте `text` для отображения в списке модели административного сайта'
        assert 'pub_date' in admin_model.list_display, \
            'Добавьте `pub_date` для отображения в списке модели административного сайта'
        assert 'author' in admin_model.list_display, \
            'Добавьте `author` для отображения в списке модели административного сайта'

        assert 'text' in admin_model.search_fields, \
            'Добавьте `text` для поиска модели административного сайта'

        assert 'pub_date' in admin_model.list_filter, \
            'Добавьте `pub_date` для фильтрации модели административного сайта'

        assert hasattr(admin_model, 'empty_value_display'), \
            'Добавьте дефолтное значение `-пусто-` для пустого поля'
        assert admin_model.empty_value_display == '-пусто-', \
            'Добавьте дефолтное значение `-пусто-` для пустого поля'

