import os
import tempfile

from PIL import Image

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse


from .models import Comment, Follow, Group, Post

User = get_user_model()


class TestPost(TestCase):
    def setUp(self):
        self.client = Client()
        self.client_authorized = Client()
        self.user = User.objects.create_user(
            username='human',
            email='hu.m@n.com',
            password='12345'
        )
        self.user_authorized = User.objects.create_user(
            username='goodman',
            email='goodman.m@n.com',
            password='54321'
        )
        self.client_authorized.force_login(self.user_authorized)
        self.post = Post.objects.create(text='text', author=self.user)
        self.text = 'It seems like Im in the matrix'
        self.group = Group.objects.create(
            title='title', slug='slug', description='description'
        )

    def test_profile(self):
        cache.clear()
        response = self.client.get(
            reverse('profile', args=[self.user.username])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page']), 1)
        self.assertIsInstance(response.context['author'], User)
        self.assertEqual(
            response.context['author'].username,
            self.user.username
        )

    def test_new_post_creation_unauthorized(self):
        Post.objects.filter(author=self.user).delete()
        response = self.client.post(
            reverse('new_post'),
            {'text': self.text, 'group': self.group.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        counter = Post.objects.filter(author=self.user).count()
        self.assertEqual(counter, 0)

    def test_new_post_creation_authorized(self):
        response = self.client_authorized.post(
            reverse('new_post'),
            {'text': self.text, 'group': self.group.id},
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        counter = self.user_authorized.posts.count()
        self.assertEqual(counter, 1)

    def post_is_present(self, response, response_key):
        cache.clear()
        pages = (
            reverse('index'),
            reverse('profile', args=[self.user_authorized.username]),
            reverse('post', args=[
                self.user_authorized.username,
                response_key
            ]
            )
        )
        for page in pages:
            page_response = self.client_authorized.get(page)
            with self.subTest('Поста нет на странице ' + page):
                if 'paginator' in page_response.context:
                    self.assertEqual(
                        response_key,
                        page_response.context['page'].object_list[0].pk)
                else:
                    self.assertEqual(
                        response_key,
                        page_response.context['post'].pk)

    def test_new_post_created(self):
        cache.clear()
        response = self.client_authorized.post(
            reverse('new_post'),
            {'text': self.text, 'group': self.group.id},
            follow=True
        )
        response_key = response.context['page'].object_list[0].pk
        self.post_is_present(response, response_key)
        self.assertEqual(response.status_code, 200)

    def test_post_edit(self):
        cache.clear()
        response = self.client_authorized.post(
            reverse('new_post'),
            {'text': self.text, 'group': self.group.id},
            follow=True
        )
        response2 = self.client_authorized.post(
            reverse(
                'post_edit',
                args=[
                    self.user_authorized.username,
                    response.context['page'].object_list[0].pk
                ]
            ),
            follow=True
        )
        self.assertEqual(response2.status_code, 200)
        response_key = response2.context['post'].pk
        self.post_is_present(response2, response_key)

    def test_404(self):
        response = self.client.get('invalid_address')
        self.assertEqual(response.status_code, 404)


class TestImage(TestCase):
    def setUp(self):
        self.client_authorized = Client()
        self.user_authorized = User.objects.create_user(
            username='goodman',
            email='goodman.m@n.com',
            password='54321'
        )
        self.group = Group.objects.create(
            title='group_title',
            slug='group_slug',
            description='group_description'
        )
        self.post = Post.objects.create(
            text='text',
            author=self.user_authorized,
            group=self.group)
        self.client_authorized.force_login(self.user_authorized)

    def test_image_contains(self):
        cache.clear()
        img2 = Image.new('RGB', (60, 30), color='red')
        img2.save('posts/picture.png')
        with open('posts/picture.png', 'rb') as img:
            self.client_authorized.post(
                reverse(
                    'post_edit',
                    kwargs={
                        'username': self.user_authorized.username,
                        'post_id': self.post.id
                    }
                ),
                {
                    'text': 'adding the image',
                    'image': img,
                    'group': self.group.id,
                }
            )
        pages = (
            reverse('index'),
            reverse(
                'profile',
                kwargs={'username': self.user_authorized.username}
            ),
            reverse(
                'post',
                kwargs={
                    'username': self.user_authorized.username,
                    'post_id': self.post.id
                }
            ),
            reverse('group', kwargs={'slug': self.group.slug}),
            )
        for page in pages:
            page_response = self.client_authorized.get(page)
            self.assertContains(page_response, '<img'.encode())
        os.remove('posts/picture.png')

    def test_not_an_image(self):
        cache.clear()
        with tempfile.TemporaryFile() as txt:
            txt.write(b'Hello world!')
            self.client_authorized.post(
                reverse(
                    'post_edit',
                    kwargs={
                        'username': self.user_authorized.username,
                        'post_id': self.post.id
                    }
                ),
                {
                    'text': 'adding the image',
                    'image': txt,
                    'group': self.group.id,
                }
            )
        pages = (
            reverse('index'),
            reverse('profile', kwargs={
                'username': self.user_authorized.username
            }
            ),
            reverse('post', kwargs={
                'username': self.user_authorized.username,
                'post_id': self.post.id
            }
            ),
            reverse('group', kwargs={'slug': self.group.slug}),
            )
        for page in pages:
            page_response = self.client_authorized.get(page)
            self.assertNotContains(page_response, '<txt')


class TestFollow(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.client3 = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@user.com',
            password='12345'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@user.com',
            password='54321'
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user1@user.com',
            password='13579'
        )
        self.group = Group.objects.create(
            title='group_title',
            slug='group_slug',
            description='group_description'
        )
        self.post = Post.objects.create(
            text='text',
            author=self.user1,
            group=self.group)
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)
        self.client3.force_login(self.user3)

    def test_follow(self):
        cache.clear()
        response = self.client1.get(
            reverse('profile_follow', args=[self.user2.username]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        follower_count = self.user1.follower.count()
        self.assertEqual(follower_count, 1)
        following_count = self.user2.following.count()
        self.assertEqual(following_count, 1)
        count = (
            Follow.objects.filter(
                user=self.user1
            ).filter(
                author=self.user2
            ).count()
        )
        self.assertEqual(count, 1)

    def test_unfollow(self):
        response = self.client1.get(
            reverse('profile_unfollow', args=[self.user2.username]),
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        follower_count = self.user1.follower.count()
        self.assertEqual(follower_count, 0)
        following_count = self.user2.following.count()
        self.assertEqual(following_count, 0)
        count = (
            Follow.objects.filter(
                user=self.user1
            ).filter(
                author=self.user2
            ).count()
        )
        self.assertEqual(count, 0)

    def test_follow_posts(self):
        self.client1.get(
            reverse('profile_follow', args=[self.user2.username]),
            follow=True
        )
        response = self.client2.post(
            reverse('new_post'),
            {'text': 'post for followers', 'group': self.group.id},
            follow=True
        )
        response_key = response.context['page'].object_list[0].pk
        page = reverse('follow_index')
        page_response = self.client1.get(page)
        self.assertEqual(
                        response_key,
                        page_response.context['page'].object_list[0].pk)
        page_response2 = self.client3.get(page)
        self.assertEqual(len(page_response2.context['page'].object_list), 0)


class TestComments(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@user.com',
            password='12345'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@user.com',
            password='54321'
        )
        self.group = Group.objects.create(
            title='group_title',
            slug='group_slug',
            description='group_description'
        )
        self.post = Post.objects.create(
            text='text',
            author=self.user1,
            group=self.group)
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)

    def test_comment_authorized(self):
        response = self.client1.post(
            reverse('new_post'),
            {'text': 'text', 'group': self.group.id},
            follow=True
        )
        self.client2.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': self.user1.username,
                    'post_id': response.context['page'].object_list[0].pk
                }
            ),
            {
                'text': 'adding the comment',
            }
        )
        page_response = self.client2.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user1.username,
                    'post_id': response.context['page'].object_list[0].pk
                }
            )
        )
        self.assertContains(page_response, 'adding the comment')

    def test_comment_unauthorized(self):
        cache.clear()
        Post.objects.filter(author=self.user1).delete()
        self.client2.logout()
        response = self.client1.post(
            reverse('new_post'),
            {'text': 'text', 'group': self.group.id},
            follow=True
        )
        self.client2.post(
            reverse(
                'add_comment',
                kwargs={
                    'username': self.user1.username,
                    'post_id': response.context['page'].object_list[0].pk
                }
            ),
            {
                'text': 'adding the comment',
            }
        )
        page_response = self.client2.get(
            reverse(
                'post',
                kwargs={
                    'username': self.user1.username,
                    'post_id': response.context['page'].object_list[0].pk
                }
            )
        )
        self.assertNotContains(page_response, 'adding the comment')
        counter = Comment.objects.filter(
            post=response.context['page'].object_list[0].pk
        ).filter(author=self.user2).count()
        self.assertEqual(counter, 0)
