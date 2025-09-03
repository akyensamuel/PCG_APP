from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Notification


@login_required
def notifications_list(request):
	notes = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:200]
	return render(request, 'notifications/list.html', { 'notifications': notes })


@login_required
def mark_read(request, pk: int):
	note = get_object_or_404(Notification, pk=pk, recipient=request.user)
	note.read = True
	note.save(update_fields=["read"])
	# Prefer going to the target URL if available
	if note.url:
		return redirect(note.url)
	return redirect('notifications:list')

# Create your views here.
