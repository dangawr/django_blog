from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Tag(models.Model):
    caption = models.CharField(max_length=50)

    def __str__(self):
        return self.caption


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Post(models.Model):
    title = models.CharField(max_length=50)
    excerpt = models.TextField(max_length=150)
    image = models.ImageField(upload_to="images", null=True)
    date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(default='', null=True, db_index=True)
    content = models.TextField(max_length=500)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name="posts")
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    text = models.TextField()
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    date = models.DateTimeField(auto_now=True)
