from django.urls import path
from . import views

app_name = "groups"

urlpatterns = [
    # Public/listing
    path("", views.groups_list, name="list"),
    path("mine/", views.my_groups, name="my_groups"),
    path("<int:pk>/", views.group_detail, name="detail"),
    path("<int:group_pk>/member/<int:user_pk>/", views.member_detail, name="member_detail"),
    # API for Select2
    path("api/groups/", views.groups_api, name="groups_api"),
    path("manage/create/", views.create_church_group, name="create_church_group"),
    path("manage/promote-admin/", views.promote_to_admin, name="promote_to_admin"),
    path("manage/<int:pk>/change-leader/", views.change_group_leader, name="change_group_leader"),
    path("manage/<int:pk>/delete/", views.delete_group, name="delete_group"),
    # Applications
    path("<int:pk>/apply/", views.apply_to_group, name="apply_to_group"),
    path("<int:group_pk>/applications/", views.group_applications, name="group_applications"),
    path("applications/<int:app_pk>/approve/", views.approve_application, name="approve_application"),
    path("applications/<int:app_pk>/reject/", views.reject_application, name="reject_application"),
]
