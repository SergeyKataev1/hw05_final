from django import forms

from .models import Comment, Follow, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': forms.Textarea(),
            'group': forms.Select()
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)


class FollowForm(forms.ModelForm):
    class Meta:
        model = Follow
        fields = ('user',)
