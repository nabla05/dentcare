from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User


def login_view(request):
    if request.user.is_authenticated:
        return redirect('clinic:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue, {user.first_name or user.username} !')
            if user.role in ('admin', 'doctor', 'receptionist'):
                return redirect('clinic:dashboard')
            else:
                return redirect('home:home')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe invalide.")

    return render(request, 'authentication/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('authentication:login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        username   = request.POST.get('username', '').strip()
        email      = request.POST.get('email', '').strip()
        password1  = request.POST.get('password', '')
        password2  = request.POST.get('password2', '')

        errors = []
        if not all([first_name, last_name, username, email, password1, password2]):
            errors.append('Veuillez remplir tous les champs obligatoires.')
        if password1 != password2:
            errors.append('Les mots de passe ne correspondent pas.')
        if len(password1) < 8:
            errors.append('Le mot de passe doit contenir au moins 8 caractères.')
        if User.objects.filter(username=username).exists():
            errors.append("Ce nom d'utilisateur est déjà pris.")
        if User.objects.filter(email=email).exists():
            errors.append('Un compte avec cet e-mail existe déjà.')

        if errors:
            for e in errors:
                messages.error(request, e)
        else:
            user = User.objects.create_user(
                username   = username,
                email      = email,
                password   = password1,
                first_name = first_name,
                last_name  = last_name,
                role       = 'patient',
            )
            from clinic.models import Patient
            from datetime import date as _date
            Patient.objects.create(
                user          = user,
                first_name    = first_name,
                last_name     = last_name,
                email         = email,
                phone         = '',
                date_of_birth = _date(2000, 1, 1),
                gender        = 'other',
            )
            login(request, user)
            messages.success(request, f'Bienvenue sur DentCare, {first_name} !')
            return redirect('home:home')

    return render(request, 'authentication/register.html')
