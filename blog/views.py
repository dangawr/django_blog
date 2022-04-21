from django.shortcuts import render, get_object_or_404, reverse
from django.views.generic.list import ListView
from django.views import View
from django.http import HttpResponseRedirect

from .models import Post, Author, Tag, Comment
from .forms import CommentForm
from datetime import date


# Create your views here.

# posts_data = [
#     {
#         "slug": "hike-in-the-mountains",
#         "image": "mountains.jpg",
#         "author": "Maximilian",
#         "date": date(2021, 7, 21),
#         "title": "Mountain Hiking",
#         "excerpt": "There's nothing like the views you get when hiking in the mountains! And I wasn't even prepared for what happened whilst I was enjoying the view!",
#         "content": """
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#         """
#     },
#     {
#         "slug": "programming-is-fun",
#         "image": "coding.jpg",
#         "author": "Maximilian",
#         "date": date(2022, 3, 10),
#         "title": "Programming Is Great!",
#         "excerpt": "Did you ever spend hours searching that one error in your code? Yep - that's what happened to me yesterday...",
#         "content": """
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#         """
#     },
#     {
#         "slug": "into-the-woods",
#         "image": "woods.jpg",
#         "author": "Maximilian",
#         "date": date(2020, 8, 5),
#         "title": "Nature At Its Best",
#         "excerpt": "Nature is amazing! The amount of inspiration I get when walking in nature is incredible!",
#         "content": """
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#
#           Lorem ipsum dolor sit amet consectetur adipisicing elit. Officiis nobis
#           aperiam est praesentium, quos iste consequuntur omnis exercitationem quam
#           velit labore vero culpa ad mollitia? Quis architecto ipsam nemo. Odio.
#         """
#     }
# ]


# def index(request):
#     post_data = Post.objects.all().order_by('-date')[:3]
#     return render(request, "blog/index.html", {
#         "posts": post_data
#     })

class IndexView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "posts"
    ordering = ["date"]

    def get_queryset(self):
        query = super().get_queryset()
        data = query[:3]
        return data


# def posts(request):
#     post_data = Post.objects.all()
#     return render(request, "blog/all-posts.html", {
#         "posts": post_data
#     })


class PostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    context_object_name = "posts"
    ordering = ["date"]


# def post_detail(request, slug):
#     post = get_object_or_404(Post, slug=slug)
#     # post = next(post for post in post_data if post['slug'] == slug)
#     return render(request, "blog/post-detail.html", {
#         "post": post
#     })

class PostDetailView(View):
    def to_read(self, request, post_id):
        stored_posts = request.session.get("read_later")
        if stored_posts is not None:
            to_read = post_id in stored_posts
        else:
            to_read = False
        return to_read

    def get(self, request, slug):
        form = CommentForm()
        post = Post.objects.get(slug=slug)
        comments = post.comments.all().order_by("-id")
        return render(request, "blog/post-detail.html", {
            "form": form,
            "post": post,
            "post_tags": post.tags.all(),
            "comments": comments,
            "saved_for_later": self.to_read(request, post.id)
        })

    def post(self, request, slug):
        form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)
        comments = post.comments.all().order_by("-id")
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return HttpResponseRedirect(reverse("post-detail-page", args=[slug]))

        return render(request, "blog/post-detail.html", {
            "form": form,
            "post": post,
            "post_tags": post.tags.all(),
            "comments": comments,
            "saved_for_later": self.to_read(request, post.id),
        })


class ReadLaterView(View):
    def get(self, request):
        stored_posts = request.session.get("read_later")
        context = {}
        if stored_posts is None or len(stored_posts) == 0:
            context["posts"] = []
            context["has_posts"] = False
        else:
            posts = Post.objects.filter(id__in=stored_posts)
            context["posts"] = posts
            context["has_posts"] = True
        return render(request, "blog/read-later.html", context)

    def post(self, request):
        stored_posts = request.session.get("read_later")
        if stored_posts is None:
            stored_posts = []
        post_id = int(request.POST["post_id"])
        if post_id not in stored_posts:
            stored_posts.append(post_id)
            request.session["read_later"] = stored_posts
        else:
            stored_posts.remove(post_id)
            request.session["read_later"] = stored_posts
        return HttpResponseRedirect("/")


