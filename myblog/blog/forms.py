from django import forms
from .models import Comment

class EmailPostForm(forms.Form):
    # Типы полей задаются чтобы выполнять валидацию данных в соответствии с полем
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False, widget=forms.Textarea)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["name", "email", "body"]