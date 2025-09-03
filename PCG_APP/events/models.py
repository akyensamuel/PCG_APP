from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify

from groups.models import Group


def event_image_upload_to(instance, filename: str) -> str:
	return f"events/{instance.event.id if hasattr(instance, 'event') and instance.event_id else 'tmp'}/{filename}"


class Event(models.Model):
	"""An upcoming event, either for a specific group or globally to all members."""

	title = models.CharField(max_length=200)
	slug = models.SlugField(max_length=220, unique=True, blank=True)
	created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_events")
	group = models.ForeignKey(Group, null=True, blank=True, on_delete=models.CASCADE, related_name="events")
	is_global = models.BooleanField(default=False, help_text="Visible to all members when checked.")

	start_date = models.DateField()
	end_date = models.DateField(null=True, blank=True)
	start_time = models.TimeField(null=True, blank=True)
	end_time = models.TimeField(null=True, blank=True)
	location = models.CharField(max_length=200, blank=True)

	featured_image = models.ImageField(upload_to="events/featured/", null=True, blank=True)
	body = models.TextField(blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ["start_date", "start_time", "title"]

	def __str__(self) -> str:
		if self.is_global:
			scope = "Global"
		elif self.group is not None:
			scope = self.group.name
		else:
			scope = "Unscoped"
		return f"{self.title} ({scope}) on {self.start_date}"

	def save(self, *args, **kwargs):
		if not self.slug:
			base = slugify(self.title)[:50]
			slug_candidate = base
			i = 2
			while Event.objects.filter(slug=slug_candidate).exclude(pk=self.pk).exists():
				slug_candidate = f"{base}-{i}"
				i += 1
			self.slug = slug_candidate
		super().save(*args, **kwargs)


class EventImage(models.Model):
	event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="images")
	image = models.ImageField(upload_to=event_image_upload_to)
	caption = models.CharField(max_length=200, blank=True)
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self) -> str:
		return f"Image for {self.event.title}"
