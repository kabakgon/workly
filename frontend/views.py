from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Strona logowania"""
    if request.user.is_authenticated:
        return redirect('frontend:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.POST.get('next') or request.GET.get('next', '')
        
        if username and password:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('frontend:dashboard')
            else:
                messages.error(request, 'Nieprawidłowa nazwa użytkownika lub hasło.')
        else:
            messages.error(request, 'Proszę wypełnić wszystkie pola.')
    
    return render(request, 'frontend/login.html', {'next': request.GET.get('next', '')})


@login_required
@require_http_methods(["POST", "GET"])
def logout_view(request):
    """Strona wylogowania"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Zostałeś pomyślnie wylogowany.')
        return redirect('frontend:login')
    return render(request, 'frontend/logout.html')


@login_required
def dashboard(request):
    return render(request, 'frontend/dashboard.html')


@login_required
def projects_list(request):
    return render(request, 'frontend/projects.html')


@login_required
def tasks_list(request):
    return render(request, 'frontend/tasks.html')


@login_required
def project_detail(request, pk):
    return render(request, 'frontend/project_detail.html', {'project_id': pk})


@login_required
def project_gantt(request, pk):
    return render(request, 'frontend/gantt.html', {'project_id': pk})


@login_required
def project_dependencies(request, pk):
    return render(request, 'frontend/dependencies.html', {'project_id': pk})

