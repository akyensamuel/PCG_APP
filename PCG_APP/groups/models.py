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
