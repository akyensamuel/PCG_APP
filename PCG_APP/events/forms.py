from django import forms

from .models import Event, EventImage
from groups.models import Group, GroupMembership


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "title",
            "group",
            "is_global",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "location",
            "featured_image",
            "body",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "body": forms.Textarea(attrs={"rows": 10, "placeholder": "Write details about the event... You can include schedules, speakers, and any notes."}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        # Limit group choices to groups the user leads (for leaders); admins see all
        qs = Group.objects.order_by("name")
        if user and not (user.is_superuser or user.is_staff):
            lead_ids = GroupMembership.objects.filter(user=user, is_leader=True).values_list("group_id", flat=True)
            qs = qs.filter(id__in=lead_ids)
        field = self.fields.get("group")
        if isinstance(field, forms.ModelChoiceField):
            field.queryset = qs


class EventImageForm(forms.ModelForm):
    class Meta:
        model = EventImage
        fields = ["image", "caption"]


class MultiFileClearableInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class EventImageUploadForm(forms.Form):
    images = forms.FileField(widget=MultiFileClearableInput(attrs={"multiple": True}), required=False)