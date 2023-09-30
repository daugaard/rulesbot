from django import forms


class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Enter username"}
        ),
    )
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter email"}
        ),
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        ),
    )
    confirm_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Confirm password"}
        ),
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Enter email"}
        ),
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Enter password"}
        ),
    )
    next = forms.CharField(
        max_length=100,
        widget=forms.HiddenInput(),
        required=False,
    )
