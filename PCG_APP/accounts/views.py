from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .forms import SignupForm


def signup_view(request):
	if request.method == 'POST':
		form = SignupForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			messages.success(request, 'Account created. You can now sign in.')
			return redirect('login')
	else:
		form = SignupForm()
	return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
	if request.method == 'POST':
		# Support login via email or username by mapping email to username
		data = request.POST.copy()
		posted_username = data.get('username', '')
		if '@' in posted_username:
			try:
				user_obj = User.objects.get(email__iexact=posted_username)
				data['username'] = user_obj.username
			except User.DoesNotExist:
				pass
		form = AuthenticationForm(request, data=data)
		if form.is_valid():
			user = form.get_user()
			login(request, user)
			messages.success(request, f'Welcome back, {user.username}!')
			return redirect('home')
	else:
		form = AuthenticationForm(request)
	return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
	logout(request)
	messages.info(request, 'Signed out successfully.')
	return redirect('home')

# Create your views here.
