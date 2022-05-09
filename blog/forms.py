from django.forms.models import ModelForm

from .models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ["post", "user"]
        labels = {
            "text": "Your Comment:"
        }
