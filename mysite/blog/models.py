from django.db import models
from django.utils import timezone


class Post(models.Model):

    class Status(models.TextChoices):
        # embeded class : allow to easily reference choice labels, values, or names from anywhere in the code
        # ex: Post.Status.DRAFT
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"
        # Post.Status.choices -> [('DF', 'Draft'), ('PB', 'Published')]
        # Post.Status.labels  -> ['Draft', 'Published']
        # Post.Status.values  -> ['DF', 'PB']
        # Post.Status.names   -> ['DRAFT', 'PUBLISHED']

    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    # from django.db.models.functions import Now
    # publish = models.DateTimeField(db_default=Now()) Same but with database-computed default
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=2,
                              choices=Status,
                              default=Status.DRAFT)

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        return self.title
