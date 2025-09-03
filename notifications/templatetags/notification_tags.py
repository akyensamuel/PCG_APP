from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def unread_notifications_count(context):
    request = context.get('request')
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated:
        return 0
    # Avoid complex query chains in template; compute here
    return user.notifications.filter(read=False).count()
