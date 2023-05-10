from django.urls import path

from . import views

urlpatterns = [
    path(
        'outgoing_friends/',
        views.outgoing_friends,
        name='outgoing_friends'
    ),
    path(
        'incoming_friends/',
        views.incoming_friends,
        name='incoming_friends'
    ),
    path(
        'friends/',
        views.friends,
        name='friends'
    ),
    path(
        'friendship_offer/',
        views.friendship_offer,
        name='friendship_offer'
    ),
    path(
        'delete_outgoing_application/',
        views.delete_outgoing_application,
        name='delete_outgoing_application'
    ),
    path(
        'delete_incoming_application/',
        views.delete_incoming_application,
        name='delete_incoming_application'
    ),
    path(
        'delete_friend/',
        views.delete_friend,
        name='delete_friend'
    ),
]
