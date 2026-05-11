"""
views.py  —  Multi-tenant, fully company-scoped edition.

Every endpoint filters data to the user's ACTIVE company, determined by:
  1. X-Company-ID request header  (set by the frontend on company switch)
  2. ?company_id= query param  (superadmin convenience)
  3. First membership fallback  (single-company users never need to set a header)

Superusers pass ?company_id= or X-Company-ID to act on any company.
"""

from decimal import Decimal
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.utils import timezone
from datetime import datetime, timedelta

from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView

from .mixins import CompanyScopedMixin, get_company_for_user
from .models import (
    Company, CompanyMembership, PaymentRecord,
    DataEntry, Debt, Notification, NotificationPreference,
    StockItem, StockItem2,
    UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock,
)
from .serializers import (
    CompanyRegistrationSerializer, AuthenticatedCompanyRegistrationSerializer,
    CompanySerializer, CompanyListSerializer,
    GrantAccessSerializer, PaymentRecordSerializer,
    CreateCompanyStaffSerializer, CompanyMembershipSerializer,
    DataEntrySerializer, DebtSerializer, NotificationSerializer,
    StockItem2RestockSerializer, StockItemRestockSerializer,
    StockItemSerializer, StockItemSerializer2,
    UserEntrySerializer, UserEntrySerializer2,
    UserEntrySerializerExpense, UserEntrySerializerOutofstock,
    UserCompanySerializer,
)


# ---------------------------------------------------------------------------
# INTERNAL HELPERS
# ---------------------------------------------------------------------------

def _get_company_filter(request):
    """Return a dict suitable for .filter(**cf) to scope a queryset."""
    company = get_company_for_user(request)
    return {"company": company} if company else {}


def _qs_to_date_dict(queryset, value_field):
    """Convert values('date').annotate(...) queryset → {date: value} O(1) dict."""
    return {row["date"]: row[value_field] for row in queryset}


# ---------------------------------------------------------------------------
# COMPANY REGISTRATION  (public — no auth required)
# ---------------------------------------------------------------------------

class CompanyRegisterView(APIView):
    """POST /api/company/register/ — creates company + owner account (inactive)."""
    permission_classes = []

    def post(self, request):
        serializer = CompanyRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            company = serializer.save()
            return Response(
                {
                    "message": (
                        f'Welcome to SPOS! Your company "{company.name}" has been registered. '
                        "An administrator will activate your 30-day free trial once payment is confirmed."
                    ),
                    "company": company.name,
                    "owner": company.owner.username,
                    "is_active": company.is_active,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthenticatedCompanyRegisterView(APIView):
    """POST /api/company/register-new/ — existing user adds a new company."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AuthenticatedCompanyRegistrationSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            company = serializer.save()
            memberships = CompanyMembership.objects.filter(
                user=request.user
            ).select_related("company")
            companies_data = UserCompanySerializer(memberships, many=True).data
            return Response(
                {
                    "message": (
                        f'Your new company "{company.name}" has been registered. '
                        "An administrator will activate your 30-day free trial once payment is confirmed."
                    ),
                    "company": company.name,
                    "companies": companies_data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# SUPERADMIN PERMISSION
# ---------------------------------------------------------------------------

class IsSuperAdmin(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


# ---------------------------------------------------------------------------
# SUPERADMIN — COMPANY MANAGEMENT
# ---------------------------------------------------------------------------

class AdminCompanyListView(APIView):
    """GET /api/admin/companies/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        companies = Company.objects.all().order_by("-registered_at")
        return Response(CompanyListSerializer(companies, many=True).data)


class AdminCompanyDetailView(APIView):
    """GET / PATCH /api/admin/companies/<id>/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def _obj(self, pk):
        return get_object_or_404(Company, pk=pk)

    def get(self, request, pk):
        return Response(CompanySerializer(self._obj(pk)).data)

    def patch(self, request, pk):
        company = self._obj(pk)
        allowed = {"notes", "is_active", "access_expires_at"}
        data = {k: v for k, v in request.data.items() if k in allowed}
        serializer = CompanySerializer(company, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminGrantAccessView(APIView):
    """POST /api/admin/companies/<id>/grant-access/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        serializer = GrantAccessSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        months = serializer.validated_data["months"]
        company.grant_access(months=months)

        amount_paid = request.data.get("amount_paid")
        if amount_paid:
            PaymentRecord.objects.create(
                company=company,
                amount_paid=Decimal(str(amount_paid)),
                payment_method=request.data.get("payment_method", "cash"),
                payment_date=request.data.get("payment_date", timezone.now().date()),
                months_granted=months,
                recorded_by=request.user,
                reference=request.data.get("reference", ""),
                notes=request.data.get("notes", ""),
            )

        return Response({
            "message": f"Access granted for {months} month(s).",
            "company": company.name,
            "is_active": company.is_active,
            "access_expires_at": company.access_expires_at,
            "days_until_expiry": company.days_until_expiry(),
        })


class AdminRevokeAccessView(APIView):
    """POST /api/admin/companies/<id>/revoke-access/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        company.revoke_access()
        return Response({
            "message": f"Access revoked for {company.name}.",
            "is_active": company.is_active,
        })


class AdminPaymentListCreateView(APIView):
    """GET / POST /api/admin/companies/<id>/payments/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        payments = company.payments.order_by("-payment_date")
        return Response(PaymentRecordSerializer(payments, many=True).data)

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        data = request.data.copy()
        data["company"] = company.pk
        serializer = PaymentRecordSerializer(data=data)
        if serializer.is_valid():
            serializer.save(recorded_by=request.user, company=company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AdminAllPaymentsView(APIView):
    """GET /api/admin/payments/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        payments = PaymentRecord.objects.select_related("company").order_by("-payment_date")
        return Response(PaymentRecordSerializer(payments, many=True).data)


class AdminCompanyMembersView(APIView):
    """GET /api/admin/companies/<id>/members/"""
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        members = company.members.select_related("user").all()
        return Response(CompanyMembershipSerializer(members, many=True).data)


# ---------------------------------------------------------------------------
# COMPANY-ADMIN — STAFF MANAGEMENT
# ---------------------------------------------------------------------------

class IsCompanyAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        if request.user.is_superuser:
            return True
        try:
            company = get_company_for_user(request)
            if not company:
                return False
            membership = CompanyMembership.objects.get(user=request.user, company=company)
            return membership.role == "admin"
        except Exception:
            return False


class CompanyStaffListCreateView(APIView):
    """GET / POST /api/company/staff/"""
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def get(self, request):
        if request.query_params.get("all_companies") == "true":
            if request.user.is_superuser:
                members = CompanyMembership.objects.select_related("user", "company").all()
            else:
                admin_companies = CompanyMembership.objects.filter(
                    user=request.user, role="admin"
                ).values_list("company", flat=True)
                members = CompanyMembership.objects.filter(
                    company__in=admin_companies
                ).select_related("user", "company")
            return Response(CompanyMembershipSerializer(members, many=True).data)

        company = get_company_for_user(request)
        if not company:
            return Response({"error": "company_id required for superadmin."}, status=400)
        members = company.members.select_related("user", "company").all()
        return Response(CompanyMembershipSerializer(members, many=True).data)

    def post(self, request):
        company_id = request.data.get("company_id")
        if company_id:
            if not request.user.is_superuser:
                if not CompanyMembership.objects.filter(
                    user=request.user, company_id=company_id, role="admin"
                ).exists():
                    return Response({"error": "You are not an admin of that company."}, status=403)
            company = get_object_or_404(Company, pk=company_id)
        else:
            company = get_company_for_user(request)

        if not company:
            return Response({"error": "company_id required for superadmin."}, status=400)

        serializer = CreateCompanyStaffSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username=serializer.validated_data["username"],
            password=serializer.validated_data["password"],
        )
        membership = CompanyMembership.objects.create(
            user=user,
            company=company,
            role=serializer.validated_data["role"],
        )
        return Response(
            {
                "message": f"User '{user.username}' created in '{company.name}'.",
                "user_id": user.pk,
                "role": membership.role,
            },
            status=status.HTTP_201_CREATED,
        )


class CompanyStaffDeleteView(APIView):
    """DELETE /api/company/staff/<user_id>/"""
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def delete(self, request, user_id):
        if request.user.pk == int(user_id):
            return Response({"error": "Cannot delete your own account."}, status=400)
        try:
            membership = CompanyMembership.objects.get(user_id=user_id)
            if not request.user.is_superuser:
                if not CompanyMembership.objects.filter(
                    user=request.user, company=membership.company, role="admin"
                ).exists():
                    return Response(
                        {"error": "You do not have permission to delete this user."}, status=403
                    )
        except CompanyMembership.DoesNotExist:
            return Response({"error": "User not found."}, status=404)

        username = membership.user.username
        membership.user.delete()
        return Response({"message": f"User '{username}' removed."}, status=204)


# ---------------------------------------------------------------------------
# USER COMPANIES — company switcher
# ---------------------------------------------------------------------------

class UserCompaniesView(APIView):
    """GET /company/my-companies/ — all companies the user belongs to."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        memberships = (
            CompanyMembership.objects
            .filter(user=request.user)
            .select_related("company")
            .order_by("company__name")
        )
        return Response(UserCompanySerializer(memberships, many=True).data)


# ---------------------------------------------------------------------------
# COMPANY PROFILE
# ---------------------------------------------------------------------------

class CompanyProfileView(APIView):
    """GET / PATCH /api/company/profile/"""
    permission_classes = [IsAuthenticated]

    def _get_company(self, request):
        if request.user.is_superuser:
            return None
        return get_company_for_user(request)

    def get(self, request):
        company = self._get_company(request)
        if not company:
            return Response({"error": "No company linked."}, status=404)
        return Response({
            "name":              company.name,
            "email":             company.email or "",
            "phone_number":      company.phone_number or "",
            "business_location": company.business_location or "",
            "is_active":         company.is_active,
            "access_expires_at": (
                company.access_expires_at.isoformat() if company.access_expires_at else None
            ),
            "days_until_expiry": company.days_until_expiry(),
        })

    def patch(self, request):
        company = self._get_company(request)
        if not company:
            return Response({"error": "No company linked."}, status=404)
        try:
            membership = CompanyMembership.objects.get(user=request.user, company=company)
            role = membership.role
        except CompanyMembership.DoesNotExist:
            role = None
        if role != "admin" and not request.user.is_superuser:
            return Response({"error": "Only company admins can update the profile."}, status=403)

        allowed = {"email", "phone_number", "business_location", "name"}
        updated = []
        for field in allowed:
            if field in request.data:
                setattr(company, field, request.data[field])
                updated.append(field)
        if updated:
            company.save(update_fields=updated)
        return Response({
            "message":           "Profile updated.",
            "updated_fields":    updated,
            "name":              company.name,
            "email":             company.email or "",
            "phone_number":      company.phone_number or "",
            "business_location": company.business_location or "",
        })

# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"message": "Invalid credentials."}, status=401)

        # Block suspended companies before issuing token
        if not user.is_superuser:
            memberships = CompanyMembership.objects.filter(
                user=user
            ).select_related("company")
            if not memberships.exists():
                return Response(
                    {
                        "error": "no_company",
                        "message": "Account not linked to any company. Contact the administrator.",
                    },
                    status=403,
                )
            active_memberships = [m for m in memberships if m.company.is_access_valid()]
            if not active_memberships:
                first_company = memberships.first().company
                return Response(
                    {
                        "error": "access_suspended",
                        "message": (
                            "Your company's subscription has expired or been suspended. "
                            "Please contact the administrator to renew access."
                        ),
                        "company": first_company.name,
                        "is_active": first_company.is_active,
                        "access_expires_at": (
                            first_company.access_expires_at.isoformat()
                            if first_company.access_expires_at else None
                        ),
                    },
                    status=403,
                )

        response = super().post(request, *args, **kwargs)
        response.data["is_staff"]     = user.is_staff
        response.data["is_superuser"] = user.is_superuser

        if user.is_superuser:
            response.data["role"]      = "superadmin"
            response.data["message"]   = "Welcome, superadmin!"
            response.data["companies"] = []
        else:
            memberships = CompanyMembership.objects.filter(
                user=user
            ).select_related("company")
            companies_data = UserCompanySerializer(memberships, many=True).data
            first = memberships.first()
            response.data["role"]              = first.role if first else "unknown"
            response.data["company_id"]        = first.company.pk if first else None
            response.data["company_name"]      = first.company.name if first else ""
            response.data["is_company_active"] = first.company.is_access_valid() if first else False
            response.data["access_expires_at"] = (
                first.company.access_expires_at.isoformat()
                if first and first.company.access_expires_at else None
            )
            response.data["days_until_expiry"] = first.company.days_until_expiry() if first else None
            response.data["companies"]         = companies_data
            response.data["message"]           = f"Welcome, {username}!"

        return response


# ---------------------------------------------------------------------------
# DATA ENTRY VIEWS  (all company-scoped via CompanyScopedMixin)
# ---------------------------------------------------------------------------

class DataEntryListCreateView(CompanyScopedMixin, generics.ListCreateAPIView):
    serializer_class   = DataEntrySerializer
    permission_classes = [IsAuthenticated]
    queryset           = DataEntry.objects.all()


class UserEntryViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset           = UserEntry.objects.all()
    serializer_class   = UserEntrySerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserEntryViewSet2(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset           = UserEntry2.objects.all()
    serializer_class   = UserEntrySerializer2
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserEntryViewSetExpense(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset           = UserEntryExpense.objects.all()
    serializer_class   = UserEntrySerializerExpense
    permission_classes = [IsAuthenticated]


class UserEntryViewSetOutofstock(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset           = UserEntryOutofstock.objects.all()
    serializer_class   = UserEntrySerializerOutofstock
    permission_classes = [IsAuthenticated]


# Aliases kept for URL compatibility
UserEntryViewSeta        = UserEntryViewSet
UserEntryViewSet2a       = UserEntryViewSet2
UserEntryViewSetExpensea = UserEntryViewSetExpense


# ---------------------------------------------------------------------------
# STOCK VIEWS  (all company-scoped)
# ---------------------------------------------------------------------------

class StockItemListCreateView(CompanyScopedMixin, generics.ListCreateAPIView):
    """
    GET  /api/stock/  — list stock for active company (optionally filtered by ?month=YYYY-MM)
    POST /api/stock/  — restock an existing item by quantity
    """
    queryset           = StockItem.objects.all()
    serializer_class   = StockItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs = StockItem.objects.filter(company=company) if company else StockItem.objects.all()
        if month:
            try:
                sm = datetime.strptime(month, "%Y-%m").date()
                qs = qs.filter(added_date__year=sm.year, added_date__month=sm.month)
            except ValueError:
                return Response({"error": "Use YYYY-MM."}, status=400)
        return Response(StockItemSerializer(qs, many=True).data)

    def post(self, request, *args, **kwargs):
        company          = self.get_company()
        item_name        = request.data.get("item_name")
        restock_quantity = int(request.data.get("quantity", 0))
        try:
            stock_item          = StockItem.objects.get(name=item_name, company=company)
            stock_item.quantity += restock_quantity
            stock_item.save()
            return Response({"message": f"Stock updated for {item_name}."}, status=200)
        except StockItem.DoesNotExist:
            return Response({"error": "Item not found in your active company."}, status=404)


class StockItemListCreateView2(CompanyScopedMixin, generics.ListCreateAPIView):
    """
    GET  /api/stock2/  — list area-based stock for active company
    POST /api/stock2/  — restock an existing area-based item
    """
    queryset           = StockItem2.objects.all()
    serializer_class   = StockItemSerializer2
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs = StockItem2.objects.filter(company=company) if company else StockItem2.objects.all()
        if month:
            try:
                sm = datetime.strptime(month, "%Y-%m").date()
                qs = qs.filter(added_date__year=sm.year, added_date__month=sm.month)
            except ValueError:
                return Response({"error": "Use YYYY-MM."}, status=400)
        return Response(StockItemSerializer2(qs, many=True).data)

    def post(self, request, *args, **kwargs):
        company          = self.get_company()
        item_name        = request.data.get("item_name")
        restock_quantity = Decimal(request.data.get("area_in_square_meters", 0))
        try:
            stock_item = StockItem2.objects.get(stock_name=item_name, company=company)
            stock_item.area_in_square_meters += restock_quantity
            stock_item.save()
            return Response({"message": f"Stock updated for {item_name}."}, status=200)
        except StockItem2.DoesNotExist:
            return Response({"error": "Item not found in your active company."}, status=404)


class StockItemListCreateViewa(CompanyScopedMixin, generics.ListCreateAPIView):
    """
    GET    /api/stocka/  — list unit-based stock (with month filter)
    POST   /api/stocka/  — add new stock item or restock existing
    DELETE /api/stocka/  — remove a stock item
    """
    queryset           = StockItem.objects.all()
    serializer_class   = StockItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs = StockItem.objects.filter(company=company) if company else StockItem.objects.all()
        if month:
            try:
                sm = datetime.strptime(month, "%Y-%m").date()
                qs = qs.filter(added_date__year=sm.year, added_date__month=sm.month)
            except ValueError:
                return Response({"error": "Use YYYY-MM."}, status=400)
        return Response(StockItemSerializer(qs, many=True).data)

    def post(self, request, *args, **kwargs):
        company        = self.get_company()
        name           = request.data.get("name")
        quantity       = request.data.get("quantity")
        price_per_unit = request.data.get("price_per_unit")
        buying_price   = request.data.get("buying_price")
        selling_price  = request.data.get("selling_price")
        added_date     = request.data.get("added_date")

        if StockItem.objects.filter(name=name, company=company).exists():
            stock_item           = StockItem.objects.get(name=name, company=company)
            stock_item.quantity += int(quantity)
            if buying_price:
                stock_item.buying_price  = buying_price
            if selling_price:
                stock_item.selling_price = selling_price
            stock_item.save()
            return Response({"message": f"Stock updated for {name}."}, status=200)
        else:
            StockItem.objects.create(
                name=name,
                quantity=quantity,
                price_per_unit=price_per_unit,
                buying_price=buying_price,
                selling_price=selling_price,
                added_date=added_date,
                company=company,
            )
            return Response({"message": f"{name} added to stock."}, status=201)

    def delete(self, request, *args, **kwargs):
        company = self.get_company()
        name    = request.data.get("name")
        if not name:
            return Response({"error": "Item name required."}, status=400)
        try:
            StockItem.objects.get(name=name, company=company).delete()
            return Response({"message": f"{name} deleted."}, status=204)
        except StockItem.DoesNotExist:
            return Response({"error": "Item not found in your active company."}, status=404)


class StockItemListCreateView2a(CompanyScopedMixin, generics.ListCreateAPIView):
    """
    GET    /api/stock2a/  — list area-based stock
    POST   /api/stock2a/  — add new or restock existing
    DELETE /api/stock2a/  — remove a stock item
    """
    queryset           = StockItem2.objects.all()
    serializer_class   = StockItemSerializer2
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs = StockItem2.objects.filter(company=company) if company else StockItem2.objects.all()
        if month:
            try:
                sm = datetime.strptime(month, "%Y-%m").date()
                qs = qs.filter(added_date__year=sm.year, added_date__month=sm.month)
            except ValueError:
                return Response({"error": "Use YYYY-MM."}, status=400)
        return Response(StockItemSerializer2(qs, many=True).data)

    def post(self, request, *args, **kwargs):
        company               = self.get_company()
        stock_name            = request.data.get("stock_name")
        area_in_square_meters = request.data.get("area_in_square_meters")
        price_per_square_meter = request.data.get("price_per_square_meter")
        added_date            = request.data.get("added_date")

        if StockItem2.objects.filter(stock_name=stock_name, company=company).exists():
            stock_item = StockItem2.objects.get(stock_name=stock_name, company=company)
            stock_item.area_in_square_meters += Decimal(area_in_square_meters)
            stock_item.save()
            return Response({"message": f"Stock updated for {stock_name}."}, status=200)
        else:
            StockItem2.objects.create(
                stock_name=stock_name,
                area_in_square_meters=area_in_square_meters,
                price_per_square_meter=price_per_square_meter,
                added_date=added_date,
                company=company,
            )
            return Response({"message": f"{stock_name} added to stock."}, status=201)

    def delete(self, request, *args, **kwargs):
        company = self.get_company()
        name    = request.data.get("name")
        if not name:
            return Response({"error": "Item name required."}, status=400)
        try:
            StockItem2.objects.get(stock_name=name, company=company).delete()
            return Response({"message": f"{name} deleted."}, status=204)
        except StockItem2.DoesNotExist:
            return Response({"error": "Item not found in your active company."}, status=404)


class StockItemDetailView(CompanyScopedMixin, generics.RetrieveUpdateDestroyAPIView):
    """
    GET / PUT / PATCH / DELETE /api/stock/<pk>/
    Automatically scoped to active company via CompanyScopedMixin —
    users cannot access stock items from other companies by guessing PKs.
    """
    queryset           = StockItem.objects.all()
    serializer_class   = StockItemSerializer
    permission_classes = [IsAuthenticated]


class AvailableStockItemsView(APIView):
    """GET /available-stock/ — unit-based items with remaining stock > 0, scoped to active company."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_company_for_user(request)
        qs = StockItem.objects.filter(quantity__gt=F("quantity_used"))
        if company:
            qs = qs.filter(company=company)
        return Response(StockItemSerializer(qs, many=True).data)


class AvailableStockItemsView2(APIView):
    """GET /available-stock2/ — area-based items with remaining area > 0, scoped to active company."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_company_for_user(request)
        qs = StockItem2.objects.filter(
            area_in_square_meters__gt=F("area_used_in_square_meters")
        )
        if company:
            qs = qs.filter(company=company)
        return Response(StockItemSerializer2(qs, many=True).data)


# ---------------------------------------------------------------------------
# RESTOCK
# ---------------------------------------------------------------------------

class RestockView(APIView):
    """POST /api/restock/ — add quantity/area to an existing stock item."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company   = get_company_for_user(request)
        item_data = request.data.get("item")
        item_type = request.data.get("item_type")

        if item_type == "StockItem":
            serializer = StockItemRestockSerializer(data=item_data)
            if serializer.is_valid():
                name     = serializer.validated_data["name"]
                quantity = serializer.validated_data["quantity"]
                try:
                    si                   = StockItem.objects.get(name=name, company=company)
                    si.quantity         += quantity
                    si.restock_quantity  = quantity
                    si.last_restock_date = datetime.now().date()
                    si.save()
                    return Response({"message": "StockItem restocked successfully."}, status=200)
                except StockItem.DoesNotExist:
                    return Response(
                        {"error": "StockItem not found in your active company."}, status=404
                    )
            return Response(serializer.errors, status=400)

        elif item_type == "StockItem2":
            serializer = StockItem2RestockSerializer(data=item_data)
            if serializer.is_valid():
                stock_name = serializer.validated_data["stock_name"]
                area       = serializer.validated_data["area_in_square_meters"]
                try:
                    si                           = StockItem2.objects.get(
                        stock_name=stock_name, company=company
                    )
                    si.area_in_square_meters    += area
                    si.last_restock_date         = datetime.now().date()
                    si.save()
                    return Response({"message": "StockItem2 restocked successfully."}, status=200)
                except StockItem2.DoesNotExist:
                    return Response(
                        {"error": "StockItem2 not found in your active company."}, status=404
                    )
            return Response(serializer.errors, status=400)

        return Response({"error": "Invalid item type."}, status=400)

# ---------------------------------------------------------------------------
# DEBT
# ---------------------------------------------------------------------------

class DebtEntryViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset           = Debt.objects.all()
    serializer_class   = DebtSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------------------------------------------------------
# REPORTING VIEWS  (all company-scoped, O(n) dict lookups)
# ---------------------------------------------------------------------------

class MonthlyReportView(generics.GenericAPIView):
    """GET /data/monthly/?month=YYYY-MM"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get("month")
        if not month:
            return Response({"error": "Month parameter is required."}, status=400)

        try:
            year, month_number = map(int, month.split("-"))
            start_date = datetime(year, month_number, 1).strftime("%Y-%m-%d")
            end_date   = (
                datetime(year + 1, 1, 1).strftime("%Y-%m-%d")
                if month_number == 12
                else datetime(year, month_number + 1, 1).strftime("%Y-%m-%d")
            )
        except ValueError:
            return Response({"error": "Use YYYY-MM."}, status=400)

        cf              = _get_company_filter(request)
        user_entries    = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        user_entries2   = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        debt_entries    = Debt.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        oos_entries     = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date, **cf)

        sales1 = _qs_to_date_dict(
            user_entries.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        sales2 = _qs_to_date_dict(
            user_entries2.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        combined_sales = {}
        for d in set(sales1) | set(sales2):
            combined_sales[d] = (sales1.get(d) or 0) + (sales2.get(d) or 0)

        exp_by_date  = _qs_to_date_dict(
            expense_entries.values("date").annotate(total_expenses=Sum("expenses")), "total_expenses"
        )
        debt_by_date = _qs_to_date_dict(
            debt_entries.values("date").annotate(total_debts=Sum("amount")), "total_debts"
        )
        oos_by_date  = _qs_to_date_dict(
            oos_entries.values("date").annotate(total_outofstock=Sum("price")), "total_outofstock"
        )

        all_dates = (
            set(combined_sales) | set(exp_by_date) | set(debt_by_date) | set(oos_by_date)
        )

        combined_daily = []
        for date in sorted(all_dates):
            s   = combined_sales.get(date, 0) or 0
            exp = exp_by_date.get(date, 0) or 0
            dbt = debt_by_date.get(date, 0) or 0
            oos = oos_by_date.get(date, 0) or 0
            combined_daily.append({
                "date":             date,
                "total_sales":      s,
                "total_expenses":   exp,
                "total_debts":      dbt,
                "total_outofstock": oos,
                "profit":           s + oos - exp,
            })

        total_sales    = sum(combined_sales.values())
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0
        total_debts    = debt_entries.aggregate(Sum("total_price"))["total_price__sum"] or 0
        total_oos      = oos_entries.aggregate(Sum("price"))["price__sum"] or 0

        return Response({
            "daily_totals": combined_daily,
            "monthly_totals": {
                "total_sales":      total_sales,
                "total_expenses":   total_expenses,
                "total_debts":      total_debts,
                "total_outofstock": total_oos,
                "profit":           total_sales + total_oos - total_expenses,
            },
        })


class WeeklyReportView(generics.GenericAPIView):
    """GET /data/weekly/?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get("start_date")
        end_date   = request.query_params.get("end_date")
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date required."}, status=400)

        try:
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date   = datetime.strptime(end_date,   "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Use YYYY-MM-DD."}, status=400)

        cf              = _get_company_filter(request)
        user_entries    = UserEntry.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
        user_entries2   = UserEntry2.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
        debt_entries    = Debt.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
        oos_entries     = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lte=end_date, **cf)

        sales1 = _qs_to_date_dict(
            user_entries.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        sales2 = _qs_to_date_dict(
            user_entries2.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        combined_sales = {}
        for d in set(sales1) | set(sales2):
            combined_sales[d] = (sales1.get(d) or 0) + (sales2.get(d) or 0)

        exp_by_date  = _qs_to_date_dict(
            expense_entries.values("date").annotate(total_expenses=Sum("expenses")), "total_expenses"
        )
        debt_by_date = _qs_to_date_dict(
            debt_entries.values("date").annotate(total_debts=Sum("amount")), "total_debts"
        )
        oos_by_date  = _qs_to_date_dict(
            oos_entries.values("date").annotate(total_outofstock=Sum("price")), "total_outofstock"
        )

        all_dates = (
            set(combined_sales) | set(oos_by_date) | set(debt_by_date) | set(exp_by_date)
        )

        combined_daily = []
        for date in sorted(all_dates):
            s   = combined_sales.get(date, 0) or 0
            exp = exp_by_date.get(date, 0) or 0
            dbt = debt_by_date.get(date, 0) or 0
            oos = oos_by_date.get(date, 0) or 0
            combined_daily.append({
                "date":             date.strftime("%Y-%m-%d"),
                "total_sales":      s,
                "total_debts":      dbt,
                "total_outofstock": oos,
                "total_expenses":   exp,
                "profit":           s + oos - exp,
            })

        total_sales    = sum(combined_sales.values())
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0
        total_debts    = debt_entries.aggregate(Sum("amount"))["amount__sum"] or 0
        total_oos      = oos_entries.aggregate(Sum("price"))["price__sum"] or 0

        return Response({
            "daily_totals": combined_daily,
            "weekly_totals": {
                "total_sales":      total_sales,
                "total_debts":      total_debts,
                "total_outofstock": total_oos,
                "total_expenses":   total_expenses,
                "profit":           total_sales + total_oos - total_expenses,
            },
        })


class MonthlyReportView2(generics.GenericAPIView):
    """GET /data/monthly2/?month=YYYY-MM  (UserEntry2 / area-based sales)"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month = request.query_params.get("month")
        if not month:
            return Response({"error": "Month parameter is required."}, status=400)

        try:
            year, month_number = map(int, month.split("-"))
            start_date = datetime(year, month_number, 1).strftime("%Y-%m-%d")
            end_date   = (
                datetime(year + 1, 1, 1).strftime("%Y-%m-%d")
                if month_number == 12
                else datetime(year, month_number + 1, 1).strftime("%Y-%m-%d")
            )
        except ValueError:
            return Response({"error": "Use YYYY-MM."}, status=400)

        cf              = _get_company_filter(request)
        user_entries    = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date, **cf)

        sales_by_date = _qs_to_date_dict(
            user_entries.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        exp_by_date = _qs_to_date_dict(
            expense_entries.values("date").annotate(total_expenses=Sum("expenses")), "total_expenses"
        )

        all_dates = set(sales_by_date) | set(exp_by_date)
        combined  = []
        for date in sorted(all_dates):
            s   = sales_by_date.get(date, 0) or 0
            exp = exp_by_date.get(date, 0) or 0
            combined.append({
                "date": date, "total_sales": s, "total_expenses": exp, "profit": s - exp
            })

        total_sales    = user_entries.aggregate(Sum("total_price"))["total_price__sum"] or 0
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0

        return Response({
            "daily_totalss": combined,
            "monthly_totalss": {
                "total_sales":    total_sales,
                "total_expenses": total_expenses,
                "profit":         total_sales - total_expenses,
            },
        })


class YearlyReportView(generics.GenericAPIView):
    """GET /data/yearly/?year=YYYY"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        year = request.query_params.get("year")
        if not year:
            return Response({"error": "Year required."}, status=400)

        try:
            year       = int(year)
            start_date = datetime(year, 1, 1).strftime("%Y-%m-%d")
            end_date   = datetime(year + 1, 1, 1).strftime("%Y-%m-%d")
        except ValueError:
            return Response({"error": "Use YYYY."}, status=400)

        cf              = _get_company_filter(request)
        user_entries    = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        user_entries2   = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date, **cf)

        sales1 = _qs_to_date_dict(
            user_entries.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        sales2 = _qs_to_date_dict(
            user_entries2.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        combined_sales = {}
        for d in set(sales1) | set(sales2):
            combined_sales[d] = (sales1.get(d) or 0) + (sales2.get(d) or 0)

        exp_by_date = _qs_to_date_dict(
            expense_entries.values("date").annotate(total_expenses=Sum("expenses")), "total_expenses"
        )

        all_dates = set(combined_sales) | set(exp_by_date)
        combined_daily = []
        for date in sorted(all_dates):
            s   = combined_sales.get(date, 0) or 0
            exp = exp_by_date.get(date, 0) or 0
            combined_daily.append({
                "date": date, "total_sales": s, "total_expenses": exp, "profit": s - exp
            })

        total_sales    = sum(combined_sales.values())
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0

        return Response({
            "daily_totals": combined_daily,
            "monthly_totals": {
                "total_sales":    total_sales,
                "total_expenses": total_expenses,
                "profit":         total_sales - total_expenses,
            },
        })


class StockReportView(APIView):
    """GET /api/stock/report/?month=YYYY-MM  — unit-based stock report for active company."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get("month")
        start_date = end_date = None
        if month:
            try:
                y, m       = map(int, month.split("-"))
                start_date = datetime(y, m, 1)
                end_date   = (start_date + timedelta(days=31)).replace(day=1)
            except ValueError:
                return Response({"error": "Invalid month format."}, status=400)

        company = get_company_for_user(request)
        stock_items = (
            StockItem.objects.filter(company=company)
            .only("name", "quantity", "price_per_unit")
            if company
            else StockItem.objects.all().only("name", "quantity", "price_per_unit")
        )

        report = []
        for stock in stock_items:
            # IMPORTANT: scope UserEntry lookup to the SAME company
            ue = UserEntry.objects.filter(item_name=stock.name, company=company)
            if start_date and end_date:
                ue = ue.filter(date__gte=start_date, date__lt=end_date)
            qty_used  = ue.aggregate(Sum("quantity"))["quantity__sum"] or 0
            remaining = stock.quantity - qty_used
            report.append({
                "item_name":          stock.name,
                "total_quantity":     stock.quantity,
                "quantity_used":      qty_used,
                "remaining_stock":    remaining,
                "total_value_used":   qty_used  * stock.price_per_unit,
                "total_value_unused": remaining * stock.price_per_unit,
                "total_value_stock":  stock.quantity * stock.price_per_unit,
            })
        return JsonResponse(report, safe=False)


class StockReportView2(APIView):
    """GET /api/stock/report2/?month=YYYY-MM  — area-based stock report for active company."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        month = request.query_params.get("month")
        start_date = end_date = None
        if month:
            try:
                y, m       = map(int, month.split("-"))
                start_date = datetime(y, m, 1)
                end_date   = (start_date + timedelta(days=31)).replace(day=1)
            except ValueError:
                return Response({"error": "Invalid month format."}, status=400)

        company = get_company_for_user(request)
        stock_items = (
            StockItem2.objects.filter(company=company)
            .only("stock_name", "area_in_square_meters", "price_per_square_meter")
            if company
            else StockItem2.objects.all()
            .only("stock_name", "area_in_square_meters", "price_per_square_meter")
        )

        report = []
        for stock in stock_items:
            # IMPORTANT: scope UserEntry2 lookup to the SAME company
            ue = UserEntry2.objects.filter(item_name=stock.stock_name, company=company)
            if start_date and end_date:
                ue = ue.filter(date__gte=start_date, date__lt=end_date)
            area_used = (
                ue.aggregate(Sum("area_in_square_meters"))["area_in_square_meters__sum"] or 0
            )
            remaining = stock.area_in_square_meters - area_used
            report.append({
                "item_name":          stock.stock_name,
                "total_quantity":     stock.area_in_square_meters,
                "quantity_used":      area_used,
                "remaining_stock":    remaining,
                "total_value_used":   area_used  * stock.price_per_square_meter,
                "total_value_unused": remaining  * stock.price_per_square_meter,
                "total_value_stock":  stock.area_in_square_meters * stock.price_per_square_meter,
            })
        return JsonResponse(report, safe=False)


# ---------------------------------------------------------------------------
# USER MANAGEMENT
# ---------------------------------------------------------------------------

class UserListCreateView(ListCreateAPIView):
    queryset               = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAdminUser]

    def get(self, request, *args, **kwargs):
        users = User.objects.all().values("id", "username")
        return Response(users, status=200)

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        if not username or not password:
            return Response({"error": "Username and password required."}, status=400)
        User.objects.create(username=username, password=make_password(password))
        return Response({"message": "User created."}, status=201)


class UserDeleteView(DestroyAPIView):
    queryset               = User.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAdminUser]

    def delete(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=kwargs["pk"])
            user.delete()
            return Response({"message": "User deleted."}, status=204)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=404)


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes     = [IsAuthenticated]

    def post(self, request):
        user         = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            return Response({"error": "Both passwords required."}, status=400)
        if not user.check_password(old_password):
            return Response({"error": "Old password incorrect."}, status=400)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password updated."}, status=200)


# ---------------------------------------------------------------------------
# NOTIFICATIONS
# ---------------------------------------------------------------------------

@api_view(["GET"])
def get_notifications(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user)
        return JsonResponse({
            "notifications": [
                {"message": n.message, "created_at": n.created_at} for n in notifications
            ]
        })
    return JsonResponse({"notifications": []})


@api_view(["POST"])
def update_preferences(request):
    preferences, _ = NotificationPreference.objects.get_or_create(user=request.user)
    data = request.data
    preferences.email              = data.get("email", False)
    preferences.receive_push       = data.get("push", False)
    preferences.receive_sms        = data.get("text", False)
    preferences.receive_phone_call = data.get("phone_call", False)
    preferences.save()
    return Response({"message": "Preferences updated"}, status=200)


@api_view(["GET"])
def fetch_notifications(request):
    if not request.user.is_authenticated:
        return Response({"notifications": []})
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return Response({"notifications": NotificationSerializer(notifications, many=True).data})


@api_view(["POST"])
def mark_notification_as_read(request, notification_id):
    try:
        n         = Notification.objects.get(id=notification_id)
        n.is_read = True
        n.save()
        return Response({"success": "Marked as read"})
    except Notification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)


# ---------------------------------------------------------------------------
# ROBOTS
# ---------------------------------------------------------------------------

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /api/\nDisallow: /admin/\n",
        content_type="text/plain",
    )