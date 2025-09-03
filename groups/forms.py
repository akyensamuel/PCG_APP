from django import forms
from django.contrib.auth.models import User
from .models import Group, GroupMembership, GroupApplication, GroupActivity


class ChurchGroupForm(forms.ModelForm):
    leader = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("first_name", "last_name", "username"),
        required=True,
        help_text="Select the leader; they will be moved to the Leaders group automatically.",
        widget=forms.Select(attrs={"class": "w-full"}),
    )

    class Meta:
        model = Group
        fields = ["name", "description",]


class PromoteToAdminForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("first_name", "last_name", "username"),
        required=True,
        widget=forms.Select(attrs={"class": "w-full"}),
    )


class ChangeLeaderForm(forms.Form):
    leader = forms.ModelChoiceField(
        queryset=User.objects.all().order_by("first_name", "last_name", "username"),
        required=True,
        widget=forms.Select(attrs={"class": "w-full"}),
        help_text="Select the new leader for this group.",
    )


class GroupApplicationForm(forms.ModelForm):
    class Meta:
        model = GroupApplication
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 3, "placeholder": "Optional message"}),
        }


class GroupActivityForm(forms.ModelForm):
    notify_members = forms.BooleanField(required=False, label="Notify all group members after saving")
    class Meta:
        model = GroupActivity
        fields = [
            "title",
            "kind",
            "date",
            "start_time",
            "end_time",
            "location",
            "attendance_count",
            "notes",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }