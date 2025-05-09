from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout ,get_user_model
from .models import CustomUser
from .forms import RegistrationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

User = get_user_model()


def register_view(request):
    if request.method == "POST":
        print(request.POST)

        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
        else:
            print(form.errors)
    else:
        form = RegistrationForm()
    
    return render(request, "users/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "").strip()

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, "users/login.html")

        try:
            user = CustomUser.objects.get(email=email)
            print(f"user = {user} = {user.email} = {user.password}")
        except CustomUser.DoesNotExist:
            messages.error(request, "Invalid email or password.")
            return render(request, "users/login.html")

        if not user.check_password(password):  
            messages.error(request, "Invalid email or password.")
            print("Invalid email or password.")

            return render(request, "users/login.html")
        print("issue in passowrd")

        if not user.is_active:
            messages.error(request, "Your account is inactive. Please confirm your email.")
            return render(request, "users/login.html")
        print("hello")

        login(request, user)
        messages.success(request, "Login successful!")
        return redirect("dashboard")

    return render(request, "users/login.html")



def logout_view(request):
    logout(request)
    return redirect('login')
