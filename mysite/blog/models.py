from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


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
    slug = models.SlugField(
        max_length=250, unique_for_date="publish"
    )  # unique_for_date doesn't check the time
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="blog_posts",  # allow to use: user.blog_posts
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    # from django.db.models.functions import Now
    # publish = models.DateTimeField(db_default=Now()) Same but with database-computed default
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT,
    )

    # The default manager (because declared first).
    # we can use default_manager_name in Meta to specify a different default manager
    objects = models.Manager()
    published = PublishedManager()  # Our custom manager.

    tags = TaggableManager()

    class Meta:
        ordering = ["-publish"]
        indexes = [
            models.Index(fields=["-publish"]),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse(
            "blog:post_detail",
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug],
        )


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)  # None by default if default isn't set

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"
