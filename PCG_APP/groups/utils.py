from django.contrib.auth.models import Group as AuthGroup, User

from accounts.models import Profile
from .models import GroupMembership


def _ensure_auth_group(name: str) -> AuthGroup:
    grp, _ = AuthGroup.objects.get_or_create(name=name)
    return grp


def sync_user_role_groups(user: User) -> None:
    """Ensure the user's Django auth groups reflect domain roles.

    - Everyone belongs to auth "Members"
    - If user leads any church group -> add to auth "Leaders"; remove if no longer leader anywhere
    - If user is admin (Profile role ADMIN or staff/superuser or in domain Admin group) -> add to auth "Admin"; remove if no longer admin
    """
    if not user or not isinstance(user, User):
        return

    members_auth = _ensure_auth_group("Members")
    leaders_auth = _ensure_auth_group("Leaders")
    admin_auth = _ensure_auth_group("Admin")

    # Always ensure user is in Members auth group
    user.groups.add(members_auth)

    # Leader status: any GroupMembership with is_leader
    leads_any = GroupMembership.objects.filter(user=user, is_leader=True).exists()
    if leads_any:
        user.groups.add(leaders_auth)
    else:
        user.groups.remove(leaders_auth)

    # Admin status: Profile role ADMIN, or staff/superuser, or domain Admin membership
    profile = getattr(user, "profile", None)
    is_admin = (getattr(user, "is_superuser", False) or getattr(user, "is_staff", False))
    if profile is not None:
        is_admin = is_admin or (profile.role == Profile.Role.ADMIN)
    in_domain_admin = GroupMembership.objects.filter(user=user, group__name="Admin").exists()
    if in_domain_admin:
        is_admin = True
    if is_admin:
        user.groups.add(admin_auth)
    else:
        user.groups.remove(admin_auth)

    # Save M2M updates
    user.save()
