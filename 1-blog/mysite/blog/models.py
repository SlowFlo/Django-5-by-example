from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    # good practice: define choices inside the model class.
    # -> allow to reference choice labels, values, or names from anywhere;
    # ex: Post.Status.DRAFT
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=250)
    slug = models.SlugField(
        max_length=250,
        unique_for_date="publish",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT,
    )

    # if we want to use database-computed default value, we can do :
    # from django.db.models.functions import Now
    # publish = models.DateTimeField(db_default=Now())

    objects = models.Manager()  # default manager.
    published = PublishedManager()  # Our custom manager.

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
            args=[
                self.publish.year,
                self.publish.month,
                self.publish.day,
                self.slug,
            ],
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",  # default: comment_set
    )
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["created"]
        indexes = [
            models.Index(fields=["created"]),
        ]

    def __str__(self):
        return f"Comment by {self.name} on {self.post}"


# Exemple of CompositePrimaryKey :
# A composite key could be used for a new model to track a user’s favorite posts, where the important
# data comes from two foreign keys – first to the user, and then to the post – and these columns help to
# ensure uniqueness in the composite key

# Models who use it cannot, for now, be registered in the Admin interface, see this ticket:
# https://code.djangoproject.com/ticket/35953
# class FavouritePost(models.Model):
#     pk = models.CompositePrimaryKey(
#         "user",
#         "post",
#     )
#     user = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#     )
#     post = models.ForeignKey(
#         "blog.Post",
#         on_delete=models.CASCADE,
#     )
#     created = models.DateTimeField(auto_now_add=True)
