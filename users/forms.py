from django import forms


class SignupForm(forms.Form):
    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control mb-3", "placeholder": "Enter username"}
        ),
    )
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(
            attrs={"class": "form-control mb-3", "placeholder": "Enter email"}
        ),
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Enter password"}
        ),
    )
    confirm_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Confirm password"}
        ),
    )


class LoginForm(forms.Form):
    email = forms.EmailField(
        max_length=100,
        widget=forms.EmailInput(
            attrs={"class": "form-control mb-3", "placeholder": "Enter email"}
        ),
    )
    password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Enter password"}
        ),
    )
    next = forms.CharField(
        max_length=100,
        widget=forms.HiddenInput(),
        required=False,
    )


class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control mb-3",
                "placeholder": "Enter current password",
            }
        ),
    )
    new_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Enter new password"}
        ),
    )
    confirm_new_password = forms.CharField(
        max_length=100,
        widget=forms.PasswordInput(
            attrs={"class": "form-control mb-3", "placeholder": "Confirm new password"}
        ),
    )
