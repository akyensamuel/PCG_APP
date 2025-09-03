import calendar
from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone

from groups.models import GroupMembership, Group
from accounts.models import Profile
from .models import Event, EventImage
from .forms import EventForm, EventImageUploadForm


def _is_admin(user) -> bool:
	try:
		profile = getattr(user, "profile", None)
		in_admin_group = GroupMembership.objects.filter(user=user, group__name="Admin").exists()
		return user.is_authenticated and (user.is_superuser or user.is_staff or (profile and profile.role == Profile.Role.ADMIN) or in_admin_group)
	except Exception:
		return bool(user.is_authenticated and (user.is_superuser or user.is_staff))


@login_required
def calendar_view(request):
	"""Overview calendar: upcoming events the user is allowed to see.

	- Admins: see all events
	- Leaders/Members: see global events + events for groups they belong to
	"""
	today = timezone.localdate()

	# Base queryset with visibility rules
	base_qs = Event.objects.all()
	if not _is_admin(request.user):
		member_group_ids = list(
			GroupMembership.objects.filter(user=request.user).values_list("group_id", flat=True)
		)
		base_qs = base_qs.filter(Q(is_global=True) | Q(group_id__in=member_group_ids))

	# Upcoming events: starting today or later, or continuing through today; show next 8
	upcoming_qs = base_qs.filter(
		Q(end_date__gte=today) | Q(end_date__isnull=True, start_date__gte=today)
	).select_related("group").order_by("start_date", "start_time")[:8]

	ctx = {
		"upcoming_events": list(upcoming_qs),
	}
	return render(request, "events/calendar.html", ctx)


@login_required
def event_detail(request, slug: str):
	ev = get_object_or_404(Event, slug=slug)
	# Visibility rules
	if not _is_admin(request.user):
		in_group = GroupMembership.objects.filter(user=request.user, group=ev.group).exists() if getattr(ev, "group", None) else False
		if not (ev.is_global or in_group):
			return redirect("events:calendar")
	return render(request, "events/detail.html", {"event": ev})


@login_required
def event_create(request):
	# Admins can create global or for any group; leaders can create for groups they lead (is_global must be False)
	if request.method == "POST":
		form = EventForm(request.POST, request.FILES, user=request.user)
		upload_form = EventImageUploadForm(request.POST, request.FILES)
		if form.is_valid() and upload_form.is_valid():
			ev: Event = form.save(commit=False)
			if not _is_admin(request.user):
				ev.is_global = False
			ev.created_by = request.user
			ev.save()
			# Save gallery images
			for f in request.FILES.getlist("images"):
				EventImage.objects.create(event=ev, image=f)
			messages.success(request, "Event created.")
			return redirect("events:detail", slug=ev.slug)
	else:
		form = EventForm(user=request.user)
		upload_form = EventImageUploadForm()
	return render(request, "events/form.html", {"form": form, "upload_form": upload_form, "mode": "create"})


@login_required
def event_edit(request, slug: str):
	ev = get_object_or_404(Event, slug=slug)
	# Author, leader of the group, or admin can edit
	is_leader = bool(getattr(ev, "group", None)) and GroupMembership.objects.filter(group=ev.group, user=request.user, is_leader=True).exists()
	if not (_is_admin(request.user) or is_leader or (ev.created_by and ev.created_by.pk == request.user.pk)):
		return redirect("events:detail", slug=slug)
	if request.method == "POST":
		form = EventForm(request.POST, request.FILES, instance=ev, user=request.user)
		upload_form = EventImageUploadForm(request.POST, request.FILES)
		if form.is_valid() and upload_form.is_valid():
			ev = form.save()
			for f in request.FILES.getlist("images"):
				EventImage.objects.create(event=ev, image=f)
			messages.success(request, "Event updated.")
			return redirect("events:detail", slug=ev.slug)
	else:
		form = EventForm(instance=ev, user=request.user)
		upload_form = EventImageUploadForm()
	return render(request, "events/form.html", {"form": form, "upload_form": upload_form, "mode": "edit", "event": ev})


@login_required
def delete_event_image(request, image_id: int):
	img = get_object_or_404(EventImage, pk=image_id)
	ev = img.event
	is_leader = ev.group and GroupMembership.objects.filter(group=ev.group, user=request.user, is_leader=True).exists()
	if not (_is_admin(request.user) or is_leader or (ev.created_by and ev.created_by.pk == request.user.pk)):
		return redirect("events:detail", slug=ev.slug)
	img.delete()
	messages.info(request, "Image removed.")
	return redirect("events:edit", slug=ev.slug)


@login_required
def api_events(request):
	"""Return events as JSON for a given date range, for FullCalendar.

	Query params: start, end (ISO dates); returns events the user can see.
	"""
	start = request.GET.get("start")
	end = request.GET.get("end")
	qs = Event.objects.all()
	if start and end:
		try:
			start_d = timezone.datetime.fromisoformat(start).date()
			end_d = timezone.datetime.fromisoformat(end).date()
			qs = qs.filter(Q(start_date__lte=end_d) & (Q(end_date__isnull=True, start_date__gte=start_d) | Q(end_date__gte=start_d)))
		except Exception:
			pass
	if not _is_admin(request.user):
		member_group_ids = list(GroupMembership.objects.filter(user=request.user).values_list("group_id", flat=True))
		qs = qs.filter(Q(is_global=True) | Q(group_id__in=member_group_ids))
	qs = qs.select_related("group").order_by("start_date", "start_time")

	items = []
	for ev in qs:
		# Compose title with group/global tag
		postfix = ""
		if ev.group is not None:
			postfix = f" · {ev.group.name}"
		elif ev.is_global:
			postfix = " · Global"
		start_dt = timezone.datetime.combine(ev.start_date, ev.start_time) if ev.start_time else timezone.datetime(ev.start_date.year, ev.start_date.month, ev.start_date.day)
		if ev.end_date:
			end_dt = timezone.datetime.combine(ev.end_date, ev.end_time) if ev.end_time else timezone.datetime(ev.end_date.year, ev.end_date.month, ev.end_date.day)
		else:
			end_dt = start_dt
		items.append({
			"id": ev.slug,
			"title": f"{ev.title}{postfix}",
			"start": start_dt.isoformat(),
			"end": end_dt.isoformat(),
			"url": request.build_absolute_uri(reverse("events:detail", args=[ev.slug])),
			"allDay": ev.start_time is None and ev.end_time is None,
		})
	return JsonResponse(items, safe=False)
