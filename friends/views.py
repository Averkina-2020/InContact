from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import FriendshipApplication, Friendship, User


@login_required
def friendship_offer(request, username):
    applicant = get_object_or_404(User, username=username)
    incoming_check = (
            FriendshipApplication.objects.filter(
                user=request.user
            ).filter(applicant=applicant).exists()
        )
    friendship_check = (
            Friendship.objects.filter(
                user=request.user
            ).filter(friend=applicant).exists()
        )
    if not friendship_check:
        if not incoming_check:
            if applicant != request.user:
                FriendshipApplication.objects.get_or_create(user=request.user, applicant=applicant)
        else:
            delete_incoming_application(request, username)
            friendship_creation(request, username)
    return redirect('profile', username=username)


def friendship_creation(request, username):
    applicant = get_object_or_404(User, username=username)
    if applicant != request.user:
        Friendship.objects.get_or_create(user=request.user, friend=applicant)
    return redirect('profile', username=username)

# Удаление друзей

@login_required
def delete_outgoing_application(request, username):
    applicant = get_object_or_404(User, username=username)
    if applicant != request.user:
        FriendshipApplication.objects.filter(user=request.user).filter(applicant=applicant).delete()
    return redirect('outgoing_friends', username=request.user.username)


@login_required
def delete_incoming_application(request, username):
    applicant = get_object_or_404(User, username=username)
    if applicant != request.user:
        FriendshipApplication.objects.filter(user=applicant).filter(applicant=request.user).delete()
    return redirect('incoming_friends', username=request.user.username)


@login_required
def delete_friend(request, username):
    applicant = get_object_or_404(User, username=username)
    if applicant != request.user:
        Friendship.objects.filter(user=request.user).filter(friend=applicant).delete()
    return redirect('friends', username=request.user.username)



# Отображение друзей

@login_required
def outgoing_friends(request, username):
    author = get_object_or_404(User, username=username)
    outgoing_list = author.outgoing.all().select_related('user')
    paginator = Paginator(outgoing_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'friends_list.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'page_type': 'outgoing',
            'page_name': 'Исходящие заявки',
        }
    )


@login_required
def incoming_friends(request, username):
    author = get_object_or_404(User, username=username)
    incoming_list = author.incoming.all()
    paginator = Paginator(incoming_list, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'friends_list.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'page_type': 'incoming',
            'page_name': 'Входящие заявки',
        }
    )


@login_required
def friends(request, username):
    author = get_object_or_404(User, username=username)
    listt = author.outgoing_friend.all()
    paginator = Paginator(listt, 5)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'friends_list.html',
        {
            'author': author,
            'page': page,
            'paginator': paginator,
            'page_type': 'friends',
            'page_name': 'Друзья',
        }
    )