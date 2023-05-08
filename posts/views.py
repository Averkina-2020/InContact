from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm
from .models import Follow, Post, User


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
    return render(
        request,
        'profile.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'following': following
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


@login_required
def follow_index(request):
    current_user = get_object_or_404(User, username=request.user)
    post_list = Post.objects.filter(
        author__following__user=current_user
    )
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'follow.html',
        {'page': page, 'paginator': paginator}
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user).filter(author=author).delete()
    return redirect('profile', username=username)
