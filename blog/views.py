from django.shortcuts import render, reverse
from django.views.generic.list import ListView
from django.views.generic import CreateView
from django.views import View
from django.http import HttpResponseRedirect

from .models import Post
from .forms import CommentForm
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm


class IndexView(ListView):
    model = Post
    template_name = "blog/index.html"
    context_object_name = "posts"
    ordering = ["date"]

    def get_queryset(self):
        query = super().get_queryset()
        data = query[:3]
        return data


class PostsView(ListView):
    template_name = "blog/all-posts.html"
    model = Post
    context_object_name = "posts"
    ordering = ["date"]


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
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy('login'))
        form = CommentForm(request.POST)
        post = Post.objects.get(slug=slug)
        comments = post.comments.all().order_by("-id")
        if form.is_valid() and request.user.is_authenticated:
            comment = form.save(commit=False)
            comment.post = post
            comment.user = self.request.user
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


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'blog/signup.html'

