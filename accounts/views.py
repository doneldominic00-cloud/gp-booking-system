from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import PatientSignUpForm
from django.contrib.auth.decorators import login_required

def signup(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('appointments:available_slots')
    else:
        form = PatientSignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def profile(request):
    return render(request, 'accounts/profile.html')
