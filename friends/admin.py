from django.contrib import admin

from .models import FriendshipApplication, Friendship

class FriendshipApplicationAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'applicant')


class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'friend')


admin.site.register(FriendshipApplication, FriendshipApplicationAdmin)
admin.site.register(Friendship, FriendshipAdmin)
