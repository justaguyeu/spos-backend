"""
middleware.py

Blocks any authenticated non-superuser whose company's access has expired or
been revoked.  Superusers always pass through.

Add to settings.py MIDDLEWARE list (after SessionMiddleware / AuthMiddleware):
    'myapp.middleware.CompanyAccessMiddleware',
"""

from django.http import JsonResponse
from django.utils import timezone


EXEMPT_PATHS = (
    '/api/token/',
    '/api/token/refresh/',
    '/admin/',
    '/api/company/register/',   # allow new registration
)


class CompanyAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Let unauthenticated requests through (JWT auth handles 401s)
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return self.get_response(request)

        # Superusers always pass
        if request.user.is_superuser:
            return self.get_response(request)

        # Exempt paths
        if any(request.path.startswith(p) for p in EXEMPT_PATHS):
            return self.get_response(request)

        # Check membership & company access
        try:
            membership = request.user.membership  # CompanyMembership OneToOne
            company = membership.company

            if not company.is_access_valid():
                days = company.days_until_expiry()
                if days == 0 or days is None:
                    reason = "Your company's subscription has expired. Please contact the administrator to renew access."
                else:
                    reason = f"Access is currently suspended. Please contact the administrator."

                return JsonResponse(
                    {
                        'error': 'access_suspended',
                        'message': reason,
                        'company': company.name,
                        'is_active': company.is_active,
                        'access_expires_at': (
                            company.access_expires_at.isoformat()
                            if company.access_expires_at else None
                        ),
                    },
                    status=403,
                )

        except Exception:
            # If no membership found, block access
            return JsonResponse(
                {
                    'error': 'no_company',
                    'message': 'Your account is not linked to any company. Contact the administrator.',
                },
                status=403,
            )

        return self.get_response(request)