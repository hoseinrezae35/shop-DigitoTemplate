from django.core.cache import cache

from .models import PersonalInformation


def personal_information(request):
    information = cache.get_or_set(
        "personal_information_active",
        lambda: PersonalInformation.objects.filter(
            is_active=True
        ).first(),
        timeout=60 * 15,
    )

    return {
        "personal_information": information,
    }