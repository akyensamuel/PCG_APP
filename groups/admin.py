from django.contrib import admin
from .models import Group, GroupMembership
from .models import GroupApplication, GroupActivity


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
	list_display = ("name", "created_at")
	search_fields = ("name",)


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
	list_display = ("user", "group", "is_leader", "joined_at")
	list_filter = ("is_leader", "group")
	search_fields = ("user__username", "user__first_name", "user__last_name", "group__name")
@admin.register(GroupApplication)
class GroupApplicationAdmin(admin.ModelAdmin):
	list_display = ("user", "group", "status", "created_at", "decided_at")
	list_filter = ("status", "group")


@admin.register(GroupActivity)
class GroupActivityAdmin(admin.ModelAdmin):
	list_display = ("group", "title", "kind", "date", "start_time", "attendance_count")
	list_filter = ("kind", "group")
	search_fields = ("title", "notes", "group__name")
