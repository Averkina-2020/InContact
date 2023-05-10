from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .models import FriendshipApplication, User


@login_required
# def profile_follow(request, username):
def friendship_offer(request, username):
    applicant = get_object_or_404(User, username=username)
    if applicant != request.user:
        FriendshipApplication.objects.get_or_create(user=request.user, applicant=applicant)
    return redirect('profile', username=username)


@login_required
# def profile_unfollow(request, username):
def delete_outgoing_application(request, username):
    applicant = get_object_or_404(User, username=username)
    if applicant != request.user:
        FriendshipApplication.objects.filter(user=request.user).filter(applicant=applicant).delete()
    return redirect('profile', username=username)


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
    listt = author.incoming.all()
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
            'page_type': 'incoming',
            'page_name': 'Входящие заявки',
        }
    )