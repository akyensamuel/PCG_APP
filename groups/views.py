from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Prefetch
from django.utils import timezone
from django.http import JsonResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import HttpResponse

from accounts.models import Profile
from .forms import ChurchGroupForm, PromoteToAdminForm, ChangeLeaderForm, GroupApplicationForm, GroupActivityForm
from .models import Group, GroupMembership, GroupApplication, GroupActivity
from .utils import sync_user_role_groups
from notifications.models import Notification


def is_admin_user(user) -> bool:
	try:
		profile = getattr(user, "profile", None)
		# also consider explicit membership in base Admin group
		in_admin_group = GroupMembership.objects.filter(user=user, group__name="Admin").exists()
		is_admin = user.is_authenticated and (
			user.is_superuser or user.is_staff or (profile is not None and profile.role == Profile.Role.ADMIN)
			or in_admin_group
		)
		return bool(is_admin)
	except Exception:
		return bool(user.is_authenticated and (user.is_superuser or user.is_staff))
def groups_list(request):
	# Show all groups to everyone; restrict actions/details separately
	groups_qs = Group.objects.order_by("name")
	admin_flag = is_admin_user(request.user)
	if admin_flag:
		leaders_qs = GroupMembership.objects.filter(is_leader=True).select_related("user")
		groups_qs = groups_qs.prefetch_related(Prefetch("memberships", queryset=leaders_qs, to_attr="leader_memberships"))
	else:
		# Hide base groups from non-admins
		groups_qs = groups_qs.exclude(name__in=["Admin", "Leaders", "Members"])
	groups = groups_qs
	# map of group_id -> has_pending_app by current user
	pending_app_ids = set()
	member_group_ids = set()
	leader_group_ids = set()
	if request.user.is_authenticated:
		pending_app_ids = set(
			GroupApplication.objects.filter(user=request.user, status=GroupApplication.Status.PENDING)
			.values_list("group_id", flat=True)
		)
		member_group_ids = set(
			GroupMembership.objects.filter(user=request.user).values_list("group_id", flat=True)
		)
		leader_group_ids = set(
			GroupMembership.objects.filter(user=request.user, is_leader=True).values_list("group_id", flat=True)
		)
	return render(
		request,
		"groups/list.html",
		{
			"groups": groups,
			"is_admin": admin_flag,
			"pending_app_ids": pending_app_ids,
			"member_group_ids": member_group_ids,
			"leader_group_ids": leader_group_ids,
		},
	)


@login_required
def my_groups(request):
	# Admins see all groups they belong to, including Members; others hide Members
	base_qs = (
		GroupMembership.objects.select_related("group")
		.filter(user=request.user)
		.order_by("group__name")
	)
	memberships = base_qs
	if not is_admin_user(request.user):
		memberships = memberships.exclude(group__name__in=["Members", "Leaders", "Admin"])
	items = [{"group": m.group, "is_leader": m.is_leader} for m in memberships]
	return render(request, "groups/my_groups.html", {"items": items, "is_admin": is_admin_user(request.user)})


def group_detail(request, pk: int):
	group = get_object_or_404(Group, pk=pk)

	# Access control: admins can view any group; leaders can view groups they lead; members can view if they belong
	admin = is_admin_user(request.user)
	is_member = GroupMembership.objects.filter(group=group, user=request.user).exists()
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	if not (admin or is_member):
		raise Http404()

	members = GroupMembership.objects.select_related("user").filter(group=group).order_by("-is_leader", "user__first_name", "user__last_name")
	leader_members = [m for m in members if m.is_leader]
	context = {
		"group": group,
		"members": members,
		"leaders": leader_members,
		"is_admin": admin,
		"is_leader": is_leader,
	}
	return render(request, "groups/detail.html", context)


@login_required
def apply_to_group(request, pk: int):
	group = get_object_or_404(Group, pk=pk)

	# Can't apply to base groups
	if group.name in ["Members", "Leaders", "Admin"]:
		raise Http404()

	# If already a member, redirect to detail
	if GroupMembership.objects.filter(group=group, user=request.user).exists():
		messages.info(request, "You're already a member of this group.")
		return redirect("groups:detail", pk=pk)

	if request.method == "POST":
		form = GroupApplicationForm(request.POST)
		if form.is_valid():
			app, created = GroupApplication.objects.get_or_create(
				user=request.user,
				group=group,
				status=GroupApplication.Status.PENDING,
				defaults={"message": form.cleaned_data.get("message", "")},
			)
			if created:
				# Notify group leaders and admins about new application
				leader_ids = list(GroupMembership.objects.filter(group=group, is_leader=True).values_list("user_id", flat=True))
				admin_ids = list(GroupMembership.objects.filter(group__name="Admin").values_list("user_id", flat=True))
				recipients = set(leader_ids + admin_ids)
				for rid in recipients:
					Notification.objects.create(
						actor=request.user,
						recipient_id=rid,
						text=f"{request.user.get_username()} applied to join {group.name}",
						url=reverse('groups:group_applications', kwargs={'group_pk': group.pk}),
					)
				messages.success(request, "Application submitted.")
			else:
				messages.info(request, "You already have a pending application.")
			return redirect("groups:list")
	else:
		form = GroupApplicationForm()
	return render(request, "groups/apply.html", {"form": form, "group": group})


@login_required
def group_applications(request, group_pk: int):
	group = get_object_or_404(Group, pk=group_pk)
	admin = is_admin_user(request.user)
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	if not (admin or is_leader):
		raise Http404()
	apps = GroupApplication.objects.select_related("user").filter(group=group, status=GroupApplication.Status.PENDING).order_by("-created_at")
	return render(request, "groups/applications.html", {"group": group, "applications": apps, "is_admin": admin, "is_leader": is_leader})


@login_required
@transaction.atomic
def approve_application(request, app_pk: int):
	app = get_object_or_404(GroupApplication, pk=app_pk, status=GroupApplication.Status.PENDING)
	group = app.group
	admin = is_admin_user(request.user)
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	if not (admin or is_leader):
		raise Http404()
	# Add member
	GroupMembership.objects.get_or_create(user=app.user, group=group)
	app.status = GroupApplication.Status.APPROVED
	app.decided_by = request.user
	app.decided_at = timezone.now()
	app.save(update_fields=["status", "decided_by", "decided_at"])
	# Notify applicant
	Notification.objects.create(
		actor=request.user,
		recipient=app.user,
		text=f"Your application to join {group.name} was approved.",
		url=reverse('groups:detail', args=[group.pk]),
	)
	messages.success(request, f"Approved application for {app.user.get_username()}.")
	return redirect("groups:group_applications", group_pk=group.pk)


@login_required
@transaction.atomic
def reject_application(request, app_pk: int):
	app = get_object_or_404(GroupApplication, pk=app_pk, status=GroupApplication.Status.PENDING)
	group = app.group
	admin = is_admin_user(request.user)
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	if not (admin or is_leader):
		raise Http404()
	app.status = GroupApplication.Status.REJECTED
	app.decided_by = request.user
	app.decided_at = timezone.now()
	app.save(update_fields=["status", "decided_by", "decided_at"])
	# Notify applicant
	Notification.objects.create(
		actor=request.user,
		recipient=app.user,
		text=f"Your application to join {group.name} was rejected.",
		url=reverse('groups:list'),
	)
	messages.info(request, f"Rejected application for {app.user.get_username()}.")
	return redirect("groups:group_applications", group_pk=group.pk)


@login_required
def member_detail(request, group_pk: int, user_pk: int):
	"""Leaders of the group and Admins can view minimal member info and remove the member."""
	group = get_object_or_404(Group, pk=group_pk)
	target_user = get_object_or_404(User, pk=user_pk)

	admin = is_admin_user(request.user)
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	# Must be admin or leader of this group
	if not (admin or is_leader):
		raise Http404()

	membership = GroupMembership.objects.filter(group=group, user=target_user).first()
	if membership is None:
		raise Http404()

	# Handle removal via POST
	if request.method == "POST":
		# Leaders cannot remove other leaders or admins; admins can remove anyone
		target_is_leader = membership.is_leader
		target_is_admin = is_admin_user(target_user)
		if admin or (is_leader and not target_is_leader and not target_is_admin and target_user != request.user):
			membership.delete()
			messages.success(request, f"Removed {target_user.get_username()} from {group.name}.")
			# Signals will re-sync auth groups; redirect back to group detail
			return redirect("groups:detail", pk=group.pk)
		else:
			messages.error(request, "You don't have permission to remove this member.")

	# Minimal, non-sensitive member info
	info = {
		"username": target_user.username,
		"full_name": target_user.get_full_name() or None,
		"email": target_user.email,
		"date_joined": target_user.date_joined,
		"is_current_leader": membership.is_leader,
	}

	# Add additional profile information for admins only
	if admin:
		profile = getattr(target_user, 'profile', None)
		if profile:
			info.update({
				"phone": profile.phone,
				"age": profile.age,
				"date_of_birth": profile.date_of_birth,
				"avatar": profile.avatar,
				"role": profile.get_role_display(),
			})

	return render(
		request,
		"groups/member_detail.html",
		{
			"group": group,
			"member": target_user,
			"membership": membership,
			"info": info,
			"is_admin": admin,
			"is_leader": is_leader,
		},
	)


@login_required
def activities_list(request, group_pk: int):
	group = get_object_or_404(Group, pk=group_pk)
	# Members of group and admins can view; leaders can manage
	admin = is_admin_user(request.user)
	is_member = GroupMembership.objects.filter(group=group, user=request.user).exists()
	if not (admin or is_member):
		raise Http404()
	activities = GroupActivity.objects.filter(group=group).order_by("-date", "-start_time")
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	return render(request, "groups/activities_list.html", {"group": group, "activities": activities, "is_admin": admin, "is_leader": is_leader})


@login_required
@transaction.atomic
def activity_create(request, group_pk: int):
	group = get_object_or_404(Group, pk=group_pk)
	admin = is_admin_user(request.user)
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	if not (admin or is_leader):
		raise Http404()
	if request.method == "POST":
		form = GroupActivityForm(request.POST)
		if form.is_valid():
			act: GroupActivity = form.save(commit=False)
			act.group = group
			act.created_by = request.user
			act.save()
			# Optional: notify members
			if form.cleaned_data.get("notify_members"):
				kind_label_map = {
					GroupActivity.Kind.MEETING.value: "meeting",
					GroupActivity.Kind.EVENT.value: "event",
					GroupActivity.Kind.OUTREACH.value: "outreach",
					GroupActivity.Kind.SERVICE.value: "service",
					GroupActivity.Kind.OTHER.value: "activity",
				}
				kind_label = kind_label_map.get(act.kind, "activity")
				member_ids = list(GroupMembership.objects.filter(group=group).values_list("user_id", flat=True))
				for uid in member_ids:
					Notification.objects.create(
						actor=request.user,
						recipient_id=uid,
						text=f"New {kind_label} in {group.name}: {act.title} on {act.date}",
						url=reverse('groups:activities_list', kwargs={'group_pk': group.pk}),
					)
			messages.success(request, "Activity recorded.")
			return redirect("groups:activities_list", group_pk=group.pk)
	else:
		form = GroupActivityForm()
	return render(request, "groups/activity_form.html", {"form": form, "group": group, "mode": "create"})


@login_required
@transaction.atomic
def activity_edit(request, activity_pk: int):
	act = get_object_or_404(GroupActivity, pk=activity_pk)
	group = act.group
	admin = is_admin_user(request.user)
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	if not (admin or is_leader):
		raise Http404()
	if request.method == "POST":
		form = GroupActivityForm(request.POST, instance=act)
		if form.is_valid():
			form.save()
			if form.cleaned_data.get("notify_members"):
				kind_label_map = {
					GroupActivity.Kind.MEETING.value: "meeting",
					GroupActivity.Kind.EVENT.value: "event",
					GroupActivity.Kind.OUTREACH.value: "outreach",
					GroupActivity.Kind.SERVICE.value: "service",
					GroupActivity.Kind.OTHER.value: "activity",
				}
				kind_label = kind_label_map.get(act.kind, "activity")
				member_ids = list(GroupMembership.objects.filter(group=group).values_list("user_id", flat=True))
				for uid in member_ids:
					Notification.objects.create(
						actor=request.user,
						recipient_id=uid,
						text=f"Updated {kind_label} in {group.name}: {act.title} on {act.date}",
						url=reverse('groups:activities_list', kwargs={'group_pk': group.pk}),
					)
			messages.success(request, "Activity updated.")
			return redirect("groups:activities_list", group_pk=group.pk)
	else:
		form = GroupActivityForm(instance=act)
	return render(request, "groups/activity_form.html", {"form": form, "group": group, "mode": "edit", "activity": act})


@login_required
@transaction.atomic
def activity_delete(request, activity_pk: int):
	act = get_object_or_404(GroupActivity, pk=activity_pk)
	group = act.group
	admin = is_admin_user(request.user)
	is_leader = GroupMembership.objects.filter(group=group, user=request.user, is_leader=True).exists()
	if not (admin or is_leader):
		raise Http404()
	if request.method == "POST":
		act.delete()
		messages.success(request, "Activity deleted.")
		return redirect("groups:activities_list", group_pk=group.pk)
	return render(request, "groups/confirm_activity_delete.html", {"group": group, "activity": act})


@login_required
@user_passes_test(is_admin_user)
def activities_report(request, group_pk: int):
	"""Admin-only activity report for a group, with optional CSV export.

	Query params:
	- start: YYYY-MM-DD (inclusive)
	- end: YYYY-MM-DD (inclusive)
	- kind: optional activity kind value
	- format: 'csv' to download CSV; default is HTML view
	"""
	group = get_object_or_404(Group, pk=group_pk)

	qs = GroupActivity.objects.filter(group=group)
	# Filters
	start = request.GET.get("start")
	end = request.GET.get("end")
	kind = request.GET.get("kind")
	if start:
		try:
			start_date = timezone.datetime.fromisoformat(start).date()
			qs = qs.filter(date__gte=start_date)
		except Exception:
			pass
	if end:
		try:
			end_date = timezone.datetime.fromisoformat(end).date()
			qs = qs.filter(date__lte=end_date)
		except Exception:
			pass
	if kind:
		qs = qs.filter(kind=kind)

	qs = qs.order_by("date", "start_time")

	# Aggregates
	total_count = qs.count()
	total_attendance = sum((a.attendance_count or 0) for a in qs)

	# Format toggle
	if request.GET.get("format") == "csv":
		# CSV export
		import csv
		response = HttpResponse(content_type="text/csv")
		filename = f"activities_{group.pk}.csv"
		response["Content-Disposition"] = f"attachment; filename={filename}"
		writer = csv.writer(response)
		writer.writerow(["Date", "Kind", "Title", "Location", "Start", "End", "Attendance"]) 
		for a in qs:
			writer.writerow([
				a.date.isoformat(),
				a.kind,
				a.title,
				a.location or "",
				a.start_time.isoformat() if a.start_time else "",
				a.end_time.isoformat() if a.end_time else "",
				a.attendance_count or 0,
			])
		# Summary row
		writer.writerow([])
		writer.writerow(["Totals", "", "", "", "", "", total_attendance])
		return response

	kinds = [(k, v) for k, v in GroupActivity.Kind.choices]
	context = {
		"group": group,
		"activities": qs,
		"total_count": total_count,
		"total_attendance": total_attendance,
		"kinds": kinds,
		"filters": {"start": start or "", "end": end or "", "kind": kind or ""},
	}
	return render(request, "groups/activities_report.html", context)


@login_required
@user_passes_test(is_admin_user)
@transaction.atomic
def change_group_leader(request, pk: int):
	group = get_object_or_404(Group, pk=pk)
	if request.method == "POST":
		form = ChangeLeaderForm(request.POST)
		if form.is_valid():
			new_leader: User = form.cleaned_data["leader"]
			# Capture previous leaders (signals won't fire on bulk update)
			prev_leader_ids = list(
				GroupMembership.objects.filter(group=group, is_leader=True).values_list("user_id", flat=True)
			)
			# Clear previous leaders
			GroupMembership.objects.filter(group=group, is_leader=True).update(is_leader=False)
			# Ensure membership and set leader
			membership, _ = GroupMembership.objects.get_or_create(group=group, user=new_leader)
			membership.is_leader = True
			membership.save(update_fields=["is_leader"])
			# Move into Leaders base group and update profile.role
			leaders_group, _ = Group.objects.get_or_create(name="Leaders")
			GroupMembership.objects.get_or_create(user=new_leader, group=leaders_group)
			prof, _ = Profile.objects.get_or_create(user=new_leader)
			prof.role = Profile.Role.LEADER
			prof.save(update_fields=["role"])
			# Sync new leader auth groups
			sync_user_role_groups(new_leader)
			# Re-sync any previous leaders to remove auth 'Leaders' if they no longer lead
			for uid in prev_leader_ids:
				if uid == new_leader.pk:
					continue
				try:
					u = User.objects.get(pk=uid)
					sync_user_role_groups(u)
				except User.DoesNotExist:
					pass
			messages.success(request, f"{new_leader.get_username()} is now the leader of {group.name}.")
			return redirect("groups:detail", pk=group.pk)
	else:
		form = ChangeLeaderForm()
	return render(request, "groups/change_leader.html", {"form": form, "group": group})


@login_required
@user_passes_test(is_admin_user)
@transaction.atomic
def delete_group(request, pk: int):
	group = get_object_or_404(Group, pk=pk)
	if request.method == "POST":
		name = group.name
		# Users who were leaders may lose leader status after deletion
		affected_user_ids = list(GroupMembership.objects.filter(group=group, is_leader=True).values_list("user_id", flat=True))
		group.delete()
		messages.success(request, f"Group '{name}' deleted.")
		# Re-sync affected users
		for uid in affected_user_ids:
			try:
				u = User.objects.get(pk=uid)
				sync_user_role_groups(u)
			except User.DoesNotExist:
				pass
		return redirect("groups:list")
	return render(request, "groups/confirm_delete.html", {"group": group})


def groups_api(request):
	# Select2 expects { results: [{id, text}], pagination: {more} }
	q = request.GET.get("q", "").strip()
	page = int(request.GET.get("page", "1") or 1)
	page_size = 20
	qs = Group.objects.exclude(name__in=["Leaders", "Members", "Admin"])  # base groups not selectable at signup
	if q:
		qs = qs.filter(name__icontains=q)
	total = qs.count()
	start = (page - 1) * page_size
	end = start + page_size
	items = [
		{"id": g.pk, "text": g.name}
		for g in qs.order_by("name")[start:end]
	]
	more = end < total
	return JsonResponse({"results": items, "pagination": {"more": more}})

    


@login_required
@user_passes_test(is_admin_user)
@transaction.atomic
def create_church_group(request):
	if request.method == "POST":
		form = ChurchGroupForm(request.POST)
		if form.is_valid():
			group: Group = form.save()
			leader: User = form.cleaned_data["leader"]

			# Mark leader in this group
			GroupMembership.objects.update_or_create(user=leader, group=group, defaults={"is_leader": True})

			# Ensure leader belongs to the base "Leaders" group and not just Members
			leaders_group, _ = Group.objects.get_or_create(name="Leaders")
			members_group, _ = Group.objects.get_or_create(name="Members")
			GroupMembership.objects.get_or_create(user=leader, group=leaders_group)
			# Remove from Members if present
			GroupMembership.objects.filter(user=leader, group=members_group).delete()

			# Update profile role
			leader_profile, _ = Profile.objects.get_or_create(user=leader)
			leader_profile.role = Profile.Role.LEADER
			leader_profile.save(update_fields=["role"]) 

			# Sync auth groups for leader
			sync_user_role_groups(leader)

			messages.success(request, f"Group '{group.name}' created and {leader.get_username()} set as leader.")
			return redirect("groups:create_church_group")
	else:
		form = ChurchGroupForm()
	return render(request, "groups/create_church_group.html", {"form": form})


@login_required
@user_passes_test(is_admin_user)
@transaction.atomic
def promote_to_admin(request):
	if request.method == "POST":
		form = PromoteToAdminForm(request.POST)
		if form.is_valid():
			user: User = form.cleaned_data["user"]

			# Update profile role to ADMIN
			profile, _ = Profile.objects.get_or_create(user=user)
			profile.role = Profile.Role.ADMIN
			profile.save(update_fields=["role"]) 

			# Ensure user belongs to base "Admins" group, and remove from Members if desired
			admins_group, _ = Group.objects.get_or_create(name="Admin")
			members_group, _ = Group.objects.get_or_create(name="Members")
			GroupMembership.objects.get_or_create(user=user, group=admins_group)
			GroupMembership.objects.filter(user=user, group=members_group).delete()

			messages.success(request, f"{user.get_username()} promoted to Admin.")
			sync_user_role_groups(user)
			return redirect("groups:promote_to_admin")
	else:
		form = PromoteToAdminForm()
	return render(request, "groups/promote_to_admin.html", {"form": form})
