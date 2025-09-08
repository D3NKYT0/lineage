from django import forms
from .models import Friendship


class FriendshipForm(forms.ModelForm):
    class Meta:
        model = Friendship
        fields = ['friend']
