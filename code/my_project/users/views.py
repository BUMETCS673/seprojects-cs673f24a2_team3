from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import LoginForm, RegistrationForm

def index(request):
    """
    View function for the home page of the site.
    """
    # Context data to pass to the template, such as any necessary information for rendering
    context = {
        'page_title': 'Movie Data Visualizations Platform',
        'message': 'Welcome to the Movie Data Visualizations Platform!',
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'analysis/index.html', context)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, 'users/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['account_name'],
                password=form.cleaned_data['password']
            )
            user.profile.user_id = form.cleaned_data['user_id']
            user.save()
            messages.success(request, "Account created successfully. You can now log in.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'users/register.html', {'form': form})
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')
def secure_view(request):
    return render(request, 'users/secure_template.html')