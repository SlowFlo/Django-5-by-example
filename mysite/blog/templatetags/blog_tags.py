from django import template

from blog.models import Post

register = template.Library()


@register.simple_tag  # (name="my_tag") to use the function with a different name inside templates
def total_posts():
    return Post.published.count()


@register.inclusion_tag("blog/post/latest_posts.html")
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by("-publish")[:count]
    return {"latest_posts": latest_posts}
