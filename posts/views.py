from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm
from .models import Follow, Post, User
from friends.models import FriendshipApplication, Friendship


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'index.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def new_post(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('index')
    return render(
        request, 'posts/new_post.html',
        {'form': form, 'flag': False}
    )

@login_required
def get_status(request, username):
    applicant = get_object_or_404(User, username=username)
    incoming_check = (
        FriendshipApplication.objects.filter(
            user=request.user
        ).filter(applicant=applicant).exists()
    )
    if incoming_check:
        return 'исходящая заявка от вас'
    outgoing_check = (
        FriendshipApplication.objects.filter(
            user=applicant
        ).filter(applicant=request.user).exists()
    )
    if outgoing_check:
        return 'входящая заявка от пользователя'
    friendship_check = (
        Friendship.objects.filter(
            user=request.user
        ).filter(friend=applicant)
    )
    if friendship_check:
        return 'друг'
    else:
        return 'отсутствует'


@login_required
def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    following = False
    if not request.user.is_anonymous or request.user.is_authenticated:
        following = (
            Follow.objects.filter(
                user=request.user
            ).filter(author=author).exists()
        )
        incoming = (
            FriendshipApplication.objects.filter(
                user=request.user
            ).filter(applicant=author).exists()
        )
        friend = (
            Friendship.objects.filter(
                user=request.user
            ).filter(user=author).exists()
        )
    status = get_status(request, username)
    return render(
        request,
        'profile.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'following': following,
            'incoming': incoming,
            'friend': friend,
            'status': status,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(
        Post, id=post_id,
        author__username=username
    )
    author = post.author
    following = False
    if not request.user.is_anonymous or request.user.is_authenticated:
        following = (
            Follow.objects.filter(
                user=request.user
            ).filter(author=author).exists()
        )
    return render(
        request,
        'posts/post.html',
        {
            'post': post,
            'author': author,
            'following': following
        }
    )


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, id=post_id, author__username=username)
    author = post.author
    if author != request.user:
        return post_view(request, username, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)
    return render(
        request, 'posts/new_post.html',
        {'form': form, 'author': author, 'post': post, 'flag': True}
    )


def page_not_found(request, exception):
    return render(
        request,
        'misc/404.html',
        {'path': request.path},
        status=404
    )


def server_error(request):
    return render(request, 'misc/500.html', status=500)
