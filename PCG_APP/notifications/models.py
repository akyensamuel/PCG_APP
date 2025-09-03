from django.db import models
from django.contrib.auth.models import User


class Notification(models.Model):
	actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications_sent")
	recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
	text = models.CharField(max_length=255)
	url = models.CharField(max_length=255, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	read = models.BooleanField(default=False)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self) -> str:
		return f"To {self.recipient.username}: {self.text}"
