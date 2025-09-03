from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User

from accounts.models import Profile
from .models import GroupMembership
from .utils import sync_user_role_groups


@receiver(post_save, sender=User)
def sync_on_user_create(sender, instance: User, created, **kwargs):
    if created:
        sync_user_role_groups(instance)


@receiver(post_save, sender=Profile)
def sync_on_profile_change(sender, instance: Profile, **kwargs):
    sync_user_role_groups(instance.user)


@receiver(post_save, sender=GroupMembership)
def sync_on_membership_save(sender, instance: GroupMembership, **kwargs):
    sync_user_role_groups(instance.user)


@receiver(post_delete, sender=GroupMembership)
def sync_on_membership_delete(sender, instance: GroupMembership, **kwargs):
    sync_user_role_groups(instance.user)
