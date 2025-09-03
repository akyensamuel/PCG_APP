from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
	class Role(models.TextChoices):
		ADMIN = "ADMIN", "Admin"
		LEADER = "LEADER", "Leader/President"
		MEMBER = "MEMBER", "Member"

	user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
	role = models.CharField(max_length=16, choices=Role.choices, default=Role.MEMBER)
	phone = models.CharField(max_length=32, blank=True)
	age = models.PositiveSmallIntegerField(null=True, blank=True)
	date_of_birth = models.DateField(null=True, blank=True)
	avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return f"{self.user.get_username()} ({self.role})"

	@property
	def is_admin(self) -> bool:
		# Superusers or staff considered admins as well
		return self.role == self.Role.ADMIN or self.user.is_superuser or self.user.is_staff

	def is_group_leader(self, group: "Group") -> bool:  # type: ignore[name-defined]
		# Lazy import to avoid circulars
		from groups.models import GroupMembership
		return GroupMembership.objects.filter(user=self.user, group=group, is_leader=True).exists()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance: User, created, **kwargs):
	if created:
		Profile.objects.create(user=instance)
	else:
		# Ensure profile exists even if created before signal connected
		Profile.objects.get_or_create(user=instance)
