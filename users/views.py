from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse

from users.forms import LoginForm, SignupForm


def sign_up_view(request):
    form = SignupForm()
    if request.method == "POST":
        # Create user
        form = SignupForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            confirm_password = form.cleaned_data["confirm_password"]
            if password == confirm_password:
                # check username and email are unique
                if User.objects.filter(username=username).exists():
                    form.add_error("username", "Username already exists")
                    return render(request, "users/sign_up.html", {"form": form})
                if User.objects.filter(email=email).exists():
                    form.add_error("email", "Email already exists")
                    return render(request, "users/sign_up.html", {"form": form})

                User.objects.create_user(
                    username=username, email=email, password=password
                )
                return redirect(reverse("users:account"))
            else:
                form.add_error("confirm_password", "Passwords do not match")

    return render(request, "users/sign_up.html", {"form": form})


def login_view(request):
    next = request.GET.get("next")
    print(next)
    form = LoginForm(initial={"next": next})

    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            next = form.cleaned_data["next"]
            # We need to check if the user exists based on the email first
            if not User.objects.filter(email=email).exists():
                form.add_error("email", "Email or password incorrect")
                return render(request, "users/login.html", {"form": form})
            # Then we login the user using the username
            username = User.objects.get(email=email).username
            user = authenticate(username=username, password=password)
            login(request, user)

            if user is not None:
                if next:
                    return redirect(next)
                else:
                    return redirect(reverse("users:account"))
            else:
                form.add_error("email", "Email or password incorrect")

    return render(request, "users/login.html", {"form": form})


def account_view(request):
    # check we're logged in
    if not request.user.is_authenticated:
        return redirect(reverse("users:login"))
    return render(request, "users/account.html", {"user": request.user})
