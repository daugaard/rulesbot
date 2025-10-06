"""
Views for the ads app.
"""

from django.http import HttpResponse


def ad_click_redirect(request, ad_id):
    """
    Placeholder view for ad click tracking and redirect.
    Will be fully implemented in Phase 3.
    """
    return HttpResponse("Ad click tracking - to be implemented in Phase 3", status=501)
