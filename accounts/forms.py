from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class AccountRegisterForm(UserCreationForm):
	username = forms.CharField(min_length=3, max_length=120, widget=forms.TextInput(attrs={'class':'form-control'}))
	first_name = forms.CharField(min_length=2, max_length=30, widget=forms.TextInput(attrs={'class':'form-control'}))
	last_name = forms.CharField(min_length=2, max_length=30, widget=forms.TextInput(attrs={'class':'form-control'}))
	email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
	password1 = forms.CharField(min_length=8, label='Password', widget=forms.PasswordInput(attrs={'class':'form-control'}))
	password2 = forms.CharField(min_length=8, label='Password confirmation', widget=forms.PasswordInput(attrs={'class':'form-control'}))

	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
