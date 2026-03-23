from django import template

from blog.models import Post

register = template.Library()


# To give the tag a different name than the function
# @register.simple_tag(name="my_tag")
@register.simple_tag
def total_posts():
    return Post.published.count()
