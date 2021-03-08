from django import forms
from django.forms import ModelForm

from .models import Post, Comment, Follow, Group#, PostRate


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["group", "text", "image"]

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields["group"].empty_label = ""

    def clean_text(self):
        data = self.cleaned_data["text"]

        if data is None:
            raise forms.ValidationError("Текст отсутствует!")
        return data


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]


class FollowForm(ModelForm):
    class Meta:
        model = Follow
        fields = []


class GroupForm(ModelForm):
    class Meta:
        model = Group
        fields = ["title", "description",]

        
#class PostRateForm(ModelForm):
 #   class Meta:
 #       model = PostRate
 #       fields = []