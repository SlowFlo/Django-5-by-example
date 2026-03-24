import markdown
from django import template
from django.db.models import Count
from django.utils.safestring import mark_safe

from blog.models import Post

register = template.Library()


# To give the tag a different name than the function
# @register.simple_tag(name="my_tag")
@register.simple_tag
def total_posts():
    return Post.published.count()


@register.inclusion_tag("blog/post/latest_posts.html")
def show_latest_posts(count=5):
    latest_posts = Post.published.order_by("-publish")[:count]
    return {"latest_posts": latest_posts}


@register.simple_tag
def get_most_commented_posts(count=5):
    return Post.published.annotate(total_comments=Count("comments")).order_by(
        "-total_comments"
    )[:count]


# To prevent a name clash between the function name and the markdown module, we have named the function markdown_format
# and we have named the filter markdown for use in templates, such as {{ variable|markdown }}.
@register.filter(name="markdown")
def markdown_format(text):
    return mark_safe(markdown.markdown(text))
