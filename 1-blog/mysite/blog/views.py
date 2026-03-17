from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from blog.forms import EmailPostForm, CommentForm
from blog.models import Post


# Old post list function-based view
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # Pagination with 3 posts per page
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer get the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range get last page of results
        posts = paginator.page(paginator.num_pages)

    return render(
        request,
        "blog/post/list.html",
        {
            "posts": posts,
            "tag": tag,
        },
    )


class PostListView(ListView):
    """
    Alternative post list view.
    """

    # model = Post => django would define the queryset `Post.objects.all()` by default
    queryset = Post.published.all()
    context_object_name = "posts"  # The default object name is `object_list`
    paginate_by = 3

    # template default to `blog/post_list.html` if not set
    template_name = "blog/post/list.html"


def post_detail(request, year, month, day, post):
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post found.")
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )

    # List of active comments for this post
    comments = post.comments.filter(active=True)
    # Form for users to comment
    form = CommentForm()

    # List of similar posts
    # flat=True give us [1, 2, 3, ...] instead of [(1,), (2,), (3,) ...]
    post_tags_ids = post.tags.values_list("id", flat=True)

    # Get posts sharing at least one tag with the current post (tags__in performs
    # a JOIN filtered to matching tags only, so a post appears once per shared tag)
    similar_posts = Post.published.filter(
        tags__in=post_tags_ids,
    ).exclude(id=post.id)

    print(list(similar_posts))

    # Count("tags") counts only the shared tags (JOIN is already filtered above)
    similar_posts = similar_posts.annotate(
        same_tags=Count("tags"),
    ).order_by(
        "-same_tags", "-publish"
    )[:4]

    return render(
        request,
        "blog/post/detail.html",
        {
            "post": post,
            "comments": comments,
            "form": form,
            "similar_posts": similar_posts,
        },
    )


def post_share(request, post_id):
    # Retrieve post by id
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED,
    )
    sent = False

    if request.method == "POST":
        # Form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # Form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url(),
            )
            subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,  # use DEFAULT_FROM_EMAIL from the settings
                recipient_list=[cd["to"]],
            )
            sent = True

    else:
        form = EmailPostForm()

    return render(
        request,
        "blog/post/share.html",
        {
            "post": post,
            "form": form,
            "sent": sent,
        },
    )


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED,
    )
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()
    return render(
        request,
        "blog/post/comment.html",
        {
            "post": post,
            "form": form,
            "comment": comment,
        },
    )
