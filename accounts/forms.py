from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from groups.models import Group
from groups.utils import sync_user_role_groups
from django.urls import reverse
from notifications.models import Notification
from groups.models import GroupMembership, GroupApplication
from .models import Profile


class SignupForm(UserCreationForm):
    # Extra fields
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=32, required=True)
    age = forms.IntegerField(min_value=0, max_value=130, required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={"type": "date"}))
    avatar = forms.ImageField(required=False)
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.none(),
        required=True,
        widget=forms.SelectMultiple(
            attrs={
                "class": "js-groups-select",
                "data-url": "/groups/api/groups/",  # TODO: replace with actual endpoint when groups API is ready
                "data-placeholder": "Select groups",
            }
        ),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.email = self.cleaned_data.get('email', '')
        if commit:
            user.save()

        # Ensure profile exists
        profile = getattr(user, 'profile', None)
        if profile is None:
            from .models import Profile
            profile, _ = Profile.objects.get_or_create(user=user)

        # Assign profile fields
        profile.age = self.cleaned_data.get('age')
        profile.date_of_birth = self.cleaned_data.get('date_of_birth')
        profile.phone = self.cleaned_data.get('phone', '')
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            profile.avatar = avatar
        if commit:
            profile.save()

        # Instead of direct membership, create applications for selected groups
        selected_groups = self.cleaned_data.get('groups')
        if selected_groups:
            for g in selected_groups:
                app, created = GroupApplication.objects.get_or_create(
                    user=user,
                    group=g,
                    status=GroupApplication.Status.PENDING,
                    defaults={"message": ""},
                )
                if created:
                    # Notify group leaders and Admins
                    leader_ids = list(GroupMembership.objects.filter(group=g, is_leader=True).values_list("user_id", flat=True))
                    admin_ids = list(GroupMembership.objects.filter(group__name="Admin").values_list("user_id", flat=True))
                    recipients = set(leader_ids + admin_ids)
                    for rid in recipients:
                        Notification.objects.create(
                            actor=user,
                            recipient_id=rid,
                            text=f"{user.get_username()} applied to join {g.name}",
                            url=reverse('groups:group_applications', kwargs={'group_pk': g.pk}),
                        )

        # Always add default base membership to Members
        members_group, _ = Group.objects.get_or_create(name="Members")
        GroupMembership.objects.get_or_create(user=user, group=members_group)

        # Sync Django auth groups to reflect domain memberships/roles
        try:
            sync_user_role_groups(user)
        except Exception:
            pass

        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate groups queryset at runtime
        field = self.fields.get('groups')
        if isinstance(field, forms.ModelMultipleChoiceField):
            field.queryset = Group.objects.exclude(name__in=["Leaders", "Members", "Admin"]).order_by('name')
            field.label = "Groups you'd like to join"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile information"""
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Profile
        fields = ['phone', 'age', 'date_of_birth', 'avatar']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Remove avatar field in production to avoid file upload issues
        from django.conf import settings
        if not settings.DEBUG:
            if 'avatar' in self.fields:
                del self.fields['avatar']
        
        if self.user:
            # Pre-populate user fields
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['email'].initial = self.user.email
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            # Check if email exists for other users
            if User.objects.filter(email__iexact=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError("A user with this email already exists.")
        return email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if self.user and commit:
            # Update user fields
            self.user.first_name = self.cleaned_data.get('first_name', '')
            self.user.last_name = self.cleaned_data.get('last_name', '')
            self.user.email = self.cleaned_data.get('email', '')
            self.user.save()
            
            # Update profile
            profile.user = self.user
            try:
                profile.save()
            except Exception as e:
                # Handle file upload errors in production
                if 'avatar' in str(e).lower() or 'media' in str(e).lower():
                    # Save without avatar if there's a file upload issue
                    avatar = profile.avatar
                    profile.avatar = None
                    profile.save()
                    # Try to save avatar separately
                    if avatar:
                        try:
                            profile.avatar = avatar
                            profile.save()
                        except:
                            pass  # Ignore avatar save errors in production
                else:
                    raise e
        
        return profile
