from django.contrib.auth.models import User
from django.db import models


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User)
