from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import StatusUpdate, UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100)
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea
    )
    profile_picture = forms.ImageField(
        required=False
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'full_name',
            'role',
            'bio',
            'profile_picture',
        )


class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(
        widget=forms.PasswordInput
    )

class StatusUpdateForm(forms.ModelForm):
    """Form used to create a status update."""

    class Meta:
        model = StatusUpdate
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'What are you thinking about?'
                }
            )
        }