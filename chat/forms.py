from django import forms


class ChatForm(forms.Form):
    question = forms.CharField(
        max_length=1000,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ask your question here"}
        ),
    )
