from django.db import models
from django.contrib.auth.models import User


class AnnouncementQuerySet(models.QuerySet):
	def visible_to(self, user: User):
		from groups.models import GroupMembership
		if not user.is_authenticated:
			return self.filter(visibility=Announcement.Visibility.PUBLIC)

		# Admins see all
		profile = getattr(user, 'profile', None)
		if profile and profile.is_admin:
			return self

		# Groups the user belongs to
		group_ids = GroupMembership.objects.filter(user=user).values_list('group_id', flat=True)
		return self.filter(
			models.Q(visibility=Announcement.Visibility.PUBLIC) |
			models.Q(visibility=Announcement.Visibility.GROUP, group_id__in=group_ids) |
			models.Q(visibility=Announcement.Visibility.LEADER_ONLY, group__memberships__user=user, group__memberships__is_leader=True)
		).distinct()


class AnnouncementManager(models.Manager.from_queryset(AnnouncementQuerySet)):
	pass


class Announcement(models.Model):
	class Visibility(models.TextChoices):
		PUBLIC = "PUBLIC", "Public"
		GROUP = "GROUP", "Group-specific"
		LEADER_ONLY = "LEADER_ONLY", "Leader-only"

	title = models.CharField(max_length=200)
	body = models.TextField()
	author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="announcements")
	visibility = models.CharField(max_length=16, choices=Visibility.choices, default=Visibility.PUBLIC)
	group = models.ForeignKey('groups.Group', on_delete=models.CASCADE, null=True, blank=True, related_name='announcements')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	objects = AnnouncementManager()

	def __str__(self) -> str:
		return self.title

	def can_edit(self, user: User) -> bool:
		profile = getattr(user, 'profile', None)
		if profile and profile.is_admin:
			return True
		# Author can edit their own public announcements
		if self.author_id == getattr(user, 'id', None):  # type: ignore[attr-defined]
			if self.visibility == self.Visibility.GROUP and self.group_id:  # type: ignore[attr-defined]
				# For group-specific, must be a leader of that group
				from groups.models import GroupMembership
				return GroupMembership.objects.filter(user=user, group_id=self.group_id, is_leader=True).exists()  # type: ignore[attr-defined]
			return True
		return False
