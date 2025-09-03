from django.shortcuts import render

from announcements.models import Announcement

def home(request):
    anns = (Announcement.objects  # type: ignore[attr-defined]
            .visible_to(request.user)  # type: ignore[attr-defined]
            .select_related('author', 'group')
            .order_by('-created_at')[:10])
    context = {
        "site_name": "PCG - A.N.T",
        "announcements": anns,
    }
    return render(request, "core/home.html", context)
