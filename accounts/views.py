from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import AccountRegisterForm
from django.contrib import messages

def account_register(request):
	if request.method == "POST":
		form = AccountRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			#username = form.cleaned_data['username']
			#password = form.cleaned_data['password1']
			#user = authenticate(username=username, password=password)
			#login(request, user)
			#messages.success(request, ("Registration Successful!"))
			#return redirect('home')
			messages.success(request, ("Registration Successful! Please login..."))
			return redirect('login')
	else:
		form = AccountRegisterForm
	return render(request, 'accounts/register.html', {'form':form})

def account_login(request):
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(request, username=username, password=password)
		if user is not None and not user.is_superuser:
			login(request, user)
			return redirect('home')
		else:
			messages.success(request, ("Login Failed! Please try again!"))
			return redirect('login')
	else:
		return render(request, 'accounts/login.html', {})


def account_logout(request):
	logout(request)
	messages.success(request, ("Logout Successful!"))
	return redirect('login')
