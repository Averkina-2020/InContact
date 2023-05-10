from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class FriendshipApplication(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='outgoing'
    )
    applicant = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='incoming'
    )


class Friendship(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='outgoing_friendd'
    )
    friend = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='incoming_friendd'
    )
