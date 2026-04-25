"""
mixins.py

CompanyScopedMixin  — use on any ViewSet/APIView to:
  1. Automatically filter querysets to the current user's company.
  2. Automatically stamp `company` on every created/updated object.
  3. Allow superusers to optionally pass ?company_id=X to inspect any company.
"""

from rest_framework.exceptions import PermissionDenied
from .models import Company


def get_company_for_user(request):
    """
    Returns the Company for the authenticated user.
    Superusers may pass ?company_id= to act on any company.
    Raises PermissionDenied if no company is found / user not linked.
    """
    user = request.user

    if user.is_superuser:
        company_id = request.query_params.get('company_id') or request.data.get('company_id')
        if company_id:
            try:
                return Company.objects.get(pk=company_id)
            except Company.DoesNotExist:
                raise PermissionDenied("Company not found.")
        # Superuser without company_id — they typically call company-management
        # endpoints, not data endpoints; return None and handle in the view.
        return None

    # Regular users: pull from their membership
    try:
        return request.user.membership.company
    except Exception:
        raise PermissionDenied("Your account is not linked to any company.")


class CompanyScopedMixin:
    """
    Mixin for ModelViewSet / APIView subclasses.

    Usage:
        class UserEntryViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
            queryset = UserEntry.objects.all()
            company_field = 'company'   # FK field name on the model (default 'company')
    """

    company_field: str = 'company'

    def get_company(self):
        if not hasattr(self, '_company'):
            self._company = get_company_for_user(self.request)
        return self._company

    def get_queryset(self):
        qs = super().get_queryset()
        company = self.get_company()
        if company is None:
            # Superuser with no company filter: return all
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