from django.contrib import admin

from .models import Event, EventImage


class EventImageInline(admin.TabularInline):
	model = EventImage
	extra = 0


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
	list_display = ("title", "start_date", "group", "is_global", "created_by")
	list_filter = ("is_global", "group", "start_date")
	prepopulated_fields = {"slug": ("title",)}
	inlines = [EventImageInline]


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
	list_display = ("event", "caption", "uploaded_at")
