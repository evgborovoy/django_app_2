from django.core.mail import send_mail
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.views.decorators.http import require_POST
from django.db.models import Count

from .models import Post, Comment
from .forms import EmailPostForm, CommentForm

from taggit.models import Tag


def post_list(request: HttpRequest, tag_slug=None) -> HttpResponse:
    posts_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])
    # Постраничная разбивка с 3 постами на страницу
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get("page", 1)
    try:
        posts = paginator.page(page_number)
    except EmptyPage:
        # Если page_number находится вне диапазона, то выдать последнюю страницу
        posts = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        # Если page_number не целое число, то покажем первую(1) страницу
        posts = paginator.page(1)
    context = {
        "posts": posts,
        "tag": tag,
    }
    return render(request, "blog/post/list.html", context=context)


def post_detail(request: HttpRequest, year, month, day, post) -> HttpResponse:
    post = get_object_or_404(Post,
                             status=Post.Status.PUBLISHED,
                             slug=post,
                             publish__year=year,
                             publish__month=month,
                             publish__day=day)
    comments = post.comments.filter(active=True)
    form = CommentForm()
    # Список похожих постов
    post_tags_ids = post.tags.values_list("id", flat=True) # flat=True для получения значений, а не одиночных кортежей
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by("-same_tags", "publish")[:4]

    context = {
        "post": post,
        "comments": comments,
        "form": form,
        "similar_posts": similar_posts
    }
    return render(request, "blog/post/detail.html", context=context)


class PostListView(ListView):
    queryset = Post.published.all()  # Альтернатива model=Post, чтобы использовать свой менеджер запросов
    context_object_name = "posts"  # для использования в шаблоне
    paginate_by = 3  # количество постов на странице
    template_name = "blog/post/list.html"  # используемый шаблон


def post_share(request: HttpRequest, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == "POST":
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, "google@Gmail.com", [cd["to"]])
            sent = True
    else:
        form = EmailPostForm()

    context = {"post": post,
               "form": form,
               "sent": sent,
               }
    return render(request, "blog/post/share.html", context=context)


@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None
    # Комментарий был отправлен
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Создать коммент не сохраняя его в базу
        comment = form.save(commit=False)
        # Назначить пост для комментария
        comment.post = post
        # Сохранить коммент
        comment.save()
    context = {
        "post": post,
        "form": form,
        "comment": comment,
    }
    return render(request, "blog/post/comment.html", context=context)
