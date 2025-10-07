"""
Views for the ads app.
"""

from django.http import HttpResponseRedirect

from ads.models import Ad
from ads.services import record_ad_click


def ad_click_redirect(request, ad_id):
    """
    Placeholder view for ad click tracking and redirect.
    Will be fully implemented in Phase 3.
    """
    ad = Ad.objects.filter(id=ad_id).first()
    if ad and ad.link:
        record_ad_click(ad)
        return HttpResponseRedirect(ad.link)
    # if the ad doesn't exist or has no link, try to redirect to the referrer or homepage
    referrer = request.META.get("HTTP_REFERER", "/")
    return HttpResponseRedirect(referrer)
