from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, ProfileEditForm
from .models import Profile


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


@login_required
def profile_edit_view(request):
	"""View for editing user profile information"""
	try:
		profile = request.user.profile
	except Profile.DoesNotExist:
		profile = Profile.objects.create(user=request.user)
	
	if request.method == 'POST':
		form = ProfileEditForm(request.POST, request.FILES, instance=profile, user=request.user)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, 'Your profile has been updated successfully!')
				return redirect('profile_edit')
			except Exception as e:
				messages.error(request, f'Error saving profile: {str(e)}')
		else:
			messages.error(request, 'Please correct the errors below.')
	else:
		form = ProfileEditForm(instance=profile, user=request.user)
	
	return render(request, 'accounts/profile_edit.html', {'form': form})

# Create your views here.
