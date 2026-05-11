"""
mixins.py

CompanyScopedMixin  — use on any ViewSet/APIView to:
  1. Automatically filter querysets to the current user's active company.
  2. Automatically stamp `company` on every created/updated object.
  3. Allow superusers to optionally pass ?company_id=X to inspect any company.
"""

from rest_framework.exceptions import PermissionDenied
from .models import Company, CompanyMembership


def _get_company_id_from_request(request):
    """
    Extract the active company ID from the request, checking all possible
    locations in priority order:
      1. X-Company-ID header  (Django 2.2+ case-insensitive dict)
      2. HTTP_X_COMPANY_ID in META  (WSGI / gunicorn fallback)
      3. ?company_id= query param
      4. company_id in POST/PUT body
    Returns a stripped string or None.
    """
    company_id = (
        request.headers.get('X-Company-ID')
        or request.META.get('HTTP_X_COMPANY_ID')
        or request.query_params.get('company_id')
        or request.data.get('company_id')
    )
    return str(company_id).strip() if company_id else None


def get_company_for_user(request):
    """
    Returns the Company for the authenticated user.

    Superusers:    respect company_id from any source; return None if not given.
    Regular users: respect X-Company-ID header first, then fall back to the
                   user's primary (first alphabetical) membership.

    Raises PermissionDenied if the user is not linked to a company or tries
    to access a company they don't belong to.
    """
    user = request.user

    # ── Superusers ─────────────────────────────────────────────────────────
    if user.is_superuser:
        company_id = _get_company_id_from_request(request)
        if company_id:
            try:
                return Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                raise PermissionDenied("Company not found.")
        return None  # No filter → superuser sees everything

    # ── Regular users ──────────────────────────────────────────────────────
    company_id = _get_company_id_from_request(request)

    if company_id:
        # Ensure the user actually belongs to the requested company
        try:
            membership = CompanyMembership.objects.select_related('company').get(
                user=user, company_id=company_id
            )
            return membership.company
        except CompanyMembership.DoesNotExist:
            raise PermissionDenied("You are not a member of that company.")

    # No header / param → fall back to first membership (alphabetical)
    membership = (
        CompanyMembership.objects
        .filter(user=user)
        .select_related('company')
        .order_by('company__name')
        .first()
    )
    if membership:
        return membership.company

    raise PermissionDenied("Your account is not linked to any company.")


class CompanyScopedMixin:
    """
    Drop-in mixin for ModelViewSet / ListCreateAPIView / RetrieveUpdateDestroyAPIView.

    • get_queryset()    → filtered to active company automatically.
    • perform_create()  → stamps company + user on the new instance.
    • perform_update()  → re-stamps company + user on the updated instance.
    • get_company()     → cached per-request helper; call from custom methods.

    Usage:
        class UserEntryViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
            queryset = UserEntry.objects.all()
            # company_field defaults to 'company' — change if your FK is named differently
    """

    company_field: str = 'company'

    def get_company(self):
        """Return (and cache) the active Company for this request."""
        if not hasattr(self, '_company_cache'):
            self._company_cache = get_company_for_user(self.request)
        return self._company_cache

    def get_queryset(self):
        qs = super().get_queryset()
        company = self.get_company()
        if company is None:
            # Superuser with no company filter — return all rows
            return qs
        return qs.filter(**{self.company_field: company})

    def perform_create(self, serializer):
        company = self.get_company()
        extra = {'user': self.request.user}
        if company:
            extra[self.company_field] = company
        serializer.save(**extra)

    def perform_update(self, serializer):
        company = self.get_company()
        extra = {'user': self.request.user}
        if company:
            extra[self.company_field] = company
        serializer.save(**extra)