from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import Post


def post_list(request: HttpRequest) -> HttpResponse:
    posts_list = Post.published.all()

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
        "posts": posts
    }
    return render(request, "blog/post/list.html", context=context)

def post_detail(request: HttpRequest, year, month, day, post) -> HttpResponse:
     context = {
         "post": get_object_or_404(Post,
                                   status=Post.Status.PUBLISHED,
                                   slug=post,
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day),
     }
     return render(request, "blog/post/detail.html", context=context)