from django.apps import AppConfig


class GroupsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'groups'
    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
