from django.urls import path
from . import views

app_name = "events"

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("api/events/", views.api_events, name="api_events"),
    path("new/", views.event_create, name="create"),
    path("<slug:slug>/", views.event_detail, name="detail"),
    path("<slug:slug>/edit/", views.event_edit, name="edit"),
    path("image/<int:image_id>/delete/", views.delete_event_image, name="delete_image"),
]
