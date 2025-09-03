from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("recipient", "text", "url", "created_at", "read")
	list_filter = ("read",)

# Register your models here.
