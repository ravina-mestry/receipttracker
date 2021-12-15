from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .forms import AccountRegisterForm
from django.contrib import messages

# account_register function returns the render regsiter.html template with AccountRegisterForm if it is a GET request
# if request method is POST and form inputs pass the validation, then save it to regsiter user and store it in db. Return the success message and redirect to login page.
# if request method is POST and form inputs do not pass the validation, form errors are sent in the render request to regsiter.html template to show them on page.
def account_register(request):
	if request.method == "POST":
		form = AccountRegisterForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, ("Registration Successful! Please login..."))
			return redirect('login')
	else:
		form = AccountRegisterForm
	return render(request, 'accounts/register.html', {'form':form})

# account_login function returns the render login.html template to show login page if it is a GET request
# if the request method is POST, it will capture the username and password, then use django authenticate function to authenticate the users.
# if the user is authenticated (exists) and it's not a superuser (djano admin login) then use django login function to login and redirect to home page.
# if the user is not authenticated or it's a superuser (djano admin login) then show login fail message and redirect to login page to try again.
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

# account_logout function uses django logout function to logout the user.
def account_logout(request):
	logout(request)
	messages.success(request, ("Logout Successful!"))
	return redirect('login')
