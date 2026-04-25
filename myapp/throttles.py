from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class CompanyBurstThrottle(UserRateThrottle):
    """
    Short-window burst limit — prevents a single company from
    firing hundreds of requests in a few seconds.
    """
    scope = "company_burst"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            try:
                company_id = request.user.membership.company_id
                return self.cache_format % {
                    "scope": self.scope,
                    "ident": f"company_{company_id}",
                }
            except Exception:
                pass
        return super().get_cache_key(request, view)


class CompanySustainedThrottle(UserRateThrottle):
    """
    Hourly sustained limit — prevents one company from monopolising
    the server across an hour.
    """
    scope = "company_sustained"

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            try:
                company_id = request.user.membership.company_id
                return self.cache_format % {
                    "scope": self.scope,
                    "ident": f"company_{company_id}",
                }
            except Exception:
                pass
        return super().get_cache_key(request, view)


class StrictAnonThrottle(AnonRateThrottle):
    """
    Very tight limit on unauthenticated traffic (login endpoint,
    registration, robots, etc.).
    """
    scope = "strict_anon"