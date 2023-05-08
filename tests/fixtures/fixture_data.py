import pytest
import tempfile


@pytest.fixture
def post(user):
    from posts.models import Post
    image = tempfile.NamedTemporaryFile(suffix=".jpg").name
    return Post.objects.create(text='Тестовый пост 1', author=user, image=image)
