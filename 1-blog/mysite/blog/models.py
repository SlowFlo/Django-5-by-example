from django.db import models
from django.utils import timezone


class Post(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # if we want to use database-computed default value, we can do :
    # from django.db.models.functions import Now
    # publish = models.DateTimeField(db_default=Now())

    def __str__(self):
        return self.title
