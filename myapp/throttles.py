# from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


# class CompanyBurstThrottle(UserRateThrottle):
#     """
#     Short-window burst limit — prevents a single company from
#     firing hundreds of requests in a few seconds.
#     """
#     scope = "company_burst"

#     def get_cache_key(self, request, view):
#         if request.user.is_authenticated:
#             try:
#                 company_id = request.user.membership.company_id
#                 return self.cache_format % {
#                     "scope": self.scope,
#                     "ident": f"company_{company_id}",
#                 }
#             except Exception:
#                 pass
#         return super().get_cache_key(request, view)


# class CompanySustainedThrottle(UserRateThrottle):
#     """
#     Hourly sustained limit — prevents one company from monopolising
#     the server across an hour.
#     """
#     scope = "company_sustained"

#     def get_cache_key(self, request, view):
#         if request.user.is_authenticated:
#             try:
#                 company_id = request.user.membership.company_id
#                 return self.cache_format % {
#                     "scope": self.scope,
#                     "ident": f"company_{company_id}",
#                 }
#             except Exception:
#                 pass
#         return super().get_cache_key(request, view)


# class StrictAnonThrottle(AnonRateThrottle):
#     """
#     Very tight limit on unauthenticated traffic (login endpoint,
#     registration, robots, etc.).
#     """
#     scope = "strict_anon"

from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class CompanyBurstThrottle(UserRateThrottle):
    """
    Short-window burst limit scoped per company.
    Allows a whole company team to load dashboards simultaneously
    without hitting a per-user limit.
    Rate: 300/minute (set in settings.py)
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
    Hourly sustained limit scoped per company.
    Prevents one company from monopolising the server all day.
    Rate: 5000/hour (set in settings.py)
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
    Tight limit on unauthenticated traffic.
    Covers login, registration, and public endpoints.
    Scoped per IP address.
    Rate: 30/minute (set in settings.py)
    """
    scope = "strict_anon"


class TokenRefreshThrottle(AnonRateThrottle):
    """
    Separate strict throttle ONLY for the token refresh endpoint.
    Scoped per IP — stops the infinite refresh loop from hammering
    the backend and causing 429 errors.

    Applied directly in urls.py — NOT in DEFAULT_THROTTLE_CLASSES
    so it does not affect other endpoints.

    Rate: 10/minute per IP (set in settings.py under 'token_refresh')
    """
    scope = "token_refresh"