from django.forms.models import ModelForm

from .models import Comment


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        exclude = ["post"]
        labels = {
            "user_name": "Your name:",
            "e_mail": "Your E-mail:",
            "text": "Your Comment:"
        }
