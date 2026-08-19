from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages


def login_view(request):
    """
    User login for Designer / Admin / Clients.
    """
    if request.user.is_authenticated:
        return redirect('designer_dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'designer_dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """
    User logout.
    """
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


def register_view(request):
    """
    User registration.
    """
    if request.user.is_authenticated:
        return redirect('designer_dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome, {user.username}.")
            return redirect('designer_dashboard')
        else:
            messages.error(request, "Registration error. Please check the details provided.")
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})
