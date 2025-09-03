from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q


class Group(models.Model):
	name = models.CharField(max_length=120, unique=True)
	description = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return self.name


class GroupMembership(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="memberships")
	group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="memberships")
	is_leader = models.BooleanField(default=False)
	joined_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ("user", "group")

	def __str__(self) -> str:
		return f"{self.user.username} -> {self.group.name} ({'Leader' if self.is_leader else 'Member'})"


class GroupApplication(models.Model):
	class Status(models.TextChoices):
		PENDING = "PENDING", "Pending"
		APPROVED = "APPROVED", "Approved"
		REJECTED = "REJECTED", "Rejected"

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="group_applications")
	group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="applications")
	message = models.TextField(blank=True)
	status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
	created_at = models.DateTimeField(auto_now_add=True)
	decided_at = models.DateTimeField(null=True, blank=True)
	decided_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="processed_group_applications")

	class Meta:
		constraints = [
			models.UniqueConstraint(fields=["user", "group"], condition=Q(status="PENDING"), name="unique_pending_group_application"),
		]

	def __str__(self) -> str:
		return f"Application {self.user.username} -> {self.group.name} ({self.status})"


class GroupActivity(models.Model):
	class Kind(models.TextChoices):
		MEETING = "MEETING", "Meeting"
		EVENT = "EVENT", "Event"
		OUTREACH = "OUTREACH", "Outreach"
		SERVICE = "SERVICE", "Service"
		OTHER = "OTHER", "Other"

	group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="activities")
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_group_activities")
	title = models.CharField(max_length=200)
	kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.MEETING)
	date = models.DateField()
	start_time = models.TimeField(null=True, blank=True)
	end_time = models.TimeField(null=True, blank=True)
	location = models.CharField(max_length=200, blank=True)
	attendance_count = models.PositiveIntegerField(null=True, blank=True)
	notes = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["-date", "-start_time", "-created_at"]

	def __str__(self) -> str:
		return f"{self.group.name}: {self.title} ({self.kind}) on {self.date}"
