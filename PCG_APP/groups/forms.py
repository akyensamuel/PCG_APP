from django import forms
from django.contrib.auth.models import User
from .models import Group, GroupMembership, GroupApplication


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