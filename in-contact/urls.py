from django.conf import settings
from django.conf.urls import handler404, handler500
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

from friends import views as friends_views


handler404 = 'posts.views.page_not_found'  # noqa
handler500 = 'posts.views.server_error'  # noqa

urlpatterns = [
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
    path(
        'about-author/', views.flatpage,
        {'url': '/about-author/'}, name='about_author'
    ),
    path(
        'about-spec/', views.flatpage,
        {'url': '/about-spec/'}, name='about_spec'
    ),
    path(
        '<str:username>/outgoing_friends/',
        friends_views.outgoing_friends,
        name='outgoing_friends'
    ),
    path(
        '<str:username>/incoming_friends/',
        friends_views.incoming_friends,
        name='incoming_friends'
    ),
    path(
        '<str:username>/friendship_offer/',
        friends_views.friendship_offer,
        name='friendship_offer'
    ),
    path(
        '<str:username>/delete_outgoing_application/',
        friends_views.delete_outgoing_application,
        name='delete_outgoing_application'
    ),
    path('', include('posts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
