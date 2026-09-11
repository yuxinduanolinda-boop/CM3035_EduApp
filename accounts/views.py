from django.contrib.auth import authenticate, login, logout
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden

from .forms import LoginForm, StatusUpdateForm, RegistrationForm
from .models import StatusUpdate, UserProfile


def register(request):
    """Register a new user and create their profile."""
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)

        if form.is_valid():
            user = form.save()

            UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                full_name=form.cleaned_data['full_name'],
                bio=form.cleaned_data['bio'],
                profile_picture=form.cleaned_data['profile_picture'],
            )

            login(request, user)

            return redirect('home')

    else:
        form = RegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form}
    )


def login_view(request):
    """Authenticate an existing user."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(
                request,
                username=username,
                password=password
            )

            if user is not None:
                login(request, user)
                return redirect('home')

    else:
        form = LoginForm()

    return render(
        request,
        'accounts/login.html',
        {'form': form}
    )


def logout_view(request):
    """Log out the current user."""
    if request.method == 'POST':
        logout(request)

    return redirect('home')


def home(request):
    """Display the correct home page for the current user."""
    if not request.user.is_authenticated:
        return render(request, 'home.html')

    profile = get_object_or_404(
        UserProfile,
        user=request.user
    )

    status_updates = StatusUpdate.objects.filter(
        user=request.user
    ).order_by('-created_at')

    context = {
        'profile': profile,
        'status_updates': status_updates,
    }

    if profile.role == 'teacher':
        return render(
            request,
            'accounts/teacher_home.html',
            context
        )

    context['status_form'] = StatusUpdateForm()

    return render(
        request,
        'accounts/student_home.html',
        context
    )

def create_status_update(request):
    """Create a new status update for the logged-in user."""
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method != 'POST':
        return redirect('home')

    form = StatusUpdateForm(request.POST)

    if form.is_valid():
        status_update = form.save(commit=False)
        status_update.user = request.user
        status_update.save()

    return redirect('home')

def search_users(request):
    """Allow teachers to search for students and teachers."""
    if not request.user.is_authenticated:
        return redirect('login')

    if request.user.profile.role != 'teacher':
        return HttpResponseForbidden(
            'Only teachers can search for users.'
        )

    query = request.GET.get('q', '').strip()

    users = User.objects.filter(
        is_active=True
    ).select_related('profile')

    if query:
        users = users.filter(
            Q(username__icontains=query)
            | Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(profile__full_name__icontains=query)
        )

    users = users.order_by('username')

    return render(
        request,
        'accounts/search_users.html',
        {
            'users': users,
            'query': query,
        }
    )

def user_profile(request, username):
    """Display a user's public profile and status updates."""
    if not request.user.is_authenticated:
        return redirect('login')

    profile_user = get_object_or_404(
        User.objects.select_related('profile'),
        username=username,
        is_active=True,
        profile__isnull=False
    )

    status_updates = StatusUpdate.objects.filter(
        user=profile_user
    ).order_by('-created_at')

    return render(
        request,
        'accounts/user_profile.html',
        {
            'profile_user': profile_user,
            'status_updates': status_updates,
        }
    )