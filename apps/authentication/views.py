from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator

from .forms import SignUpForm, LoginForm


class SignUpView(View):
    template_name = 'authentication/signup.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('questionnaires:list')
        form = SignUpForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f'Welcome to LeadFlow AI, {user.get_full_name()}!')
            return redirect('questionnaires:list')
        return render(request, self.template_name, {'form': form})


class LoginView(View):
    template_name = 'authentication/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('questionnaires:list')
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            next_url = request.GET.get('next', 'questionnaires:list')
            return redirect(next_url)
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'You have been logged out.')
        return redirect('authentication:login')

    def get(self, request):
        logout(request)
        return redirect('authentication:login')


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'authentication/profile.html'

    def get(self, request):
        return render(request, self.template_name, {})

    def post(self, request):
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.organization = request.POST.get('organization', user.organization)
        user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('authentication:profile')
