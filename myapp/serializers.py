# from django import forms
# from rest_framework import serializers
# from django.contrib.auth.models import User
# from .models import DataEntry, Debt, Notification, StockItem, StockItem2, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock

# class DataEntrySerializer(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only=True)
#     class Meta:
#         model = DataEntry
#         fields = ['user', 'date', 'item_name', 'quantity', 'price', 'expense_name', 'expenses']

# class StockItemSerializer(serializers.ModelSerializer):
#     month = serializers.SerializerMethodField()
#     class Meta:
#         model = StockItem
#         fields = ['id', 'name', 'quantity', 'price_per_unit','added_date','month', "restock_quantity" ,"last_restock_date"]

#     def get_month(self, obj):
#      return obj.get_month()

# class StockItemSerializer2(serializers.ModelSerializer):
#     month = serializers.SerializerMethodField()
#     class Meta:
#         model = StockItem2
#         fields = ['id', 'stock_name', 'area_in_square_meters', 'price_per_square_meter','added_date','month', 'restock_area_in_square_meters','last_restock_date' ]

#     def get_month(self, obj):
#      return obj.get_month()
# class UserEntrySerializer(serializers.ModelSerializer):
#     item = serializers.StringRelatedField()
#     user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

#     class Meta:
#         model = UserEntry
#         fields = '__all__'

# class UserEntrySerializer2(serializers.ModelSerializer):
#     item = serializers.StringRelatedField()
#     user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

#     class Meta:
#         model = UserEntry2
#         fields = '__all__'

# class UserEntrySerializerExpense(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

#     class Meta:
#         model = UserEntryExpense
#         fields = '__all__'

# class UserEntrySerializerOutofstock(serializers.ModelSerializer):
#     user = serializers.CharField(source='user.username', read_only=True)  # Mark as read-only

#     class Meta:
#         model = UserEntryOutofstock
#         fields = '__all__'        

# class StockReportSerializer(serializers.ModelSerializer):
#     remaining_stock = serializers.SerializerMethodField()
#     total_value_used = serializers.SerializerMethodField()
#     total_value_unused = serializers.SerializerMethodField()

#     class Meta:
#         model = StockItem
#         fields = ['name', 'quantity_used', 'remaining_stock', 'total_value_used', 'total_value_unused']

#     def get_remaining_stock(self, obj):
#         return obj.remaining_stock()

#     def get_total_value_used(self, obj):
#         return obj.total_value_used()

#     def get_total_value_unused(self, obj):
#         return obj.total_value_unused()

# class StockItemRestockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StockItem
#         fields = ['name', 'quantity']

# class StockItem2RestockSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = StockItem2
#         fields = ['stock_name', 'area_in_square_meters']


# class DebtSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Debt
#         fields = ['id', 'stock_name', 'debtor_name', 'stock_dimensions', 'amount', 'date', 'status', 'user']
#         read_only_fields = ['user']

#     # def validate_amount(self, value):
#     #     if value is None:
#     #         raise serializers.ValidationError("Amount is required")
#     #     if value <= 0:
#     #         raise serializers.ValidationError("Amount must be greater than 0")
#     #     return value



# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username']

# class UserCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['username', 'password']

#     def create(self, validated_data):
#         user = User.objects.create_user(**validated_data)
#         return user
    
# class NotificationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Notification
#         fields = ['id', 'message', 'is_read', 'created_at', 'stock_item']
from rest_framework import serializers
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Company, CompanyMembership, PaymentRecord,
    DataEntry, Debt, Notification, StockItem, StockItem2,
    UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock,
)



# ---------------------------------------------------------------------------
# Company & Subscription Serializers
# ---------------------------------------------------------------------------

# class CompanyRegistrationSerializer(serializers.Serializer):
#     """Used by the public registration endpoint."""
#     company_name = serializers.CharField(max_length=200)
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(write_only=True, min_length=6)

#     def validate_company_name(self, value):
#         if Company.objects.filter(name__iexact=value).exists():
#             raise serializers.ValidationError("A company with this name already exists.")
#         return value

#     def validate_username(self, value):
#         if User.objects.filter(username=value).exists():
#             raise serializers.ValidationError("This username is already taken.")
#         return value

#     def create(self, validated_data):
#         # Create the owner user
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             password=validated_data['password'],
#             is_staff=True,   # company admin = staff within their scope
#         )
#         # Create the company
#         company = Company.objects.create(
#             name=validated_data['company_name'],
#             owner=user,
#             is_active=False,  # inactive until superadmin grants access
#         )
#         # Create membership for the owner
#         CompanyMembership.objects.create(
#             user=user,
#             company=company,
#             role='admin',
#         )
#         return company
class CompanyRegistrationSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=200)
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    business_location = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_company_name(self, value):
        if Company.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A company with this name already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            is_staff=True,
        )
        company = Company.objects.create(
            name=validated_data['company_name'],
            owner=user,
            is_active=False,
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            business_location=validated_data.get('business_location', ''),
        )
        CompanyMembership.objects.create(user=user, company=company, role='admin')
        return company

class AuthenticatedCompanyRegistrationSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=200)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    business_location = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_company_name(self, value):
        if Company.objects.filter(name__iexact=value).exists():
            raise serializers.ValidationError("A company with this name already exists.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        company = Company.objects.create(
            name=validated_data['company_name'],
            owner=user,
            is_active=False,
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
            business_location=validated_data.get('business_location', ''),
        )
        CompanyMembership.objects.create(user=user, company=company, role='admin')
        return company

class PaymentRecordSerializer(serializers.ModelSerializer):
    recorded_by_username = serializers.CharField(source='recorded_by.username', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = PaymentRecord
        fields = [
            'id', 'company', 'company_name', 'amount_paid', 'payment_method',
            'payment_date', 'months_granted', 'recorded_by', 'recorded_by_username',
            'reference', 'notes', 'created_at',
        ]
        read_only_fields = ['recorded_by', 'created_at']


class CompanyMembershipSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = CompanyMembership
        fields = ['id', 'user_id', 'username', 'company', 'company_name', 'role', 'created_at']
        read_only_fields = ['created_at']


class CompanySerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    is_access_valid = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    members_count = serializers.SerializerMethodField()
    payments = PaymentRecordSerializer(many=True, read_only=True)

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'owner', 'owner_username', 'is_active',
            'access_expires_at', 'registered_at', 'notes',
            'is_access_valid', 'days_until_expiry', 'members_count', 'payments',
        ]
        read_only_fields = ['registered_at', 'owner']

    def get_is_access_valid(self, obj):
        return obj.is_access_valid()

    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry()

    def get_members_count(self, obj):
        return obj.members.count()


class CompanyListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views."""
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    is_access_valid = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    last_payment = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id', 'name', 'owner_username', 'is_active',
            'access_expires_at', 'registered_at',
            'is_access_valid', 'days_until_expiry', 'last_payment',
        ]

    def get_is_access_valid(self, obj):
        return obj.is_access_valid()

    def get_days_until_expiry(self, obj):
        return obj.days_until_expiry()

    def get_last_payment(self, obj):
        last = obj.payments.order_by('-payment_date').first()
        if last:
            return {'amount': str(last.amount_paid), 'date': str(last.payment_date)}
        return None


# Superadmin action serializers
class GrantAccessSerializer(serializers.Serializer):
    months = serializers.IntegerField(min_value=1, max_value=24, default=1)


class CreateCompanyStaffSerializer(serializers.Serializer):
    """Company admin uses this to create staff users within their company."""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=['admin', 'staff'], default='staff')

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value


# ---------------------------------------------------------------------------
# Existing serializers (updated to include company scoping where needed)
# ---------------------------------------------------------------------------

class DataEntrySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = DataEntry
        fields = ['user', 'date', 'item_name', 'quantity', 'price', 'expense_name', 'expenses']


class StockItemSerializer(serializers.ModelSerializer):
    month          = serializers.SerializerMethodField()
    profit_per_unit = serializers.SerializerMethodField()
    margin_percent  = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = [
            'id', 'name', 'quantity', 'price_per_unit', 'added_date', 'month',
            'restock_quantity', 'last_restock_date',
            'buying_price', 'selling_price', 'profit_per_unit', 'margin_percent',
        ]

    def get_month(self, obj):
        return obj.get_month()

    def get_profit_per_unit(self, obj):
        p = obj.profit_per_unit()
        return float(p) if p is not None else None

    def get_margin_percent(self, obj):
        return obj.margin_percent()


class StockItemSerializer2(serializers.ModelSerializer):
    month          = serializers.SerializerMethodField()
    profit_per_sqm = serializers.SerializerMethodField()
    margin_percent  = serializers.SerializerMethodField()

    class Meta:
        model = StockItem2
        fields = [
            'id', 'stock_name', 'area_in_square_meters', 'price_per_square_meter',
            'added_date', 'month', 'restock_area_in_square_meters', 'last_restock_date',
            'buying_price', 'selling_price', 'profit_per_sqm', 'margin_percent',
        ]

    def get_month(self, obj):
        return obj.get_month()

    def get_profit_per_sqm(self, obj):
        p = obj.profit_per_sqm()
        return float(p) if p is not None else None

    def get_margin_percent(self, obj):
        return obj.margin_percent()


class UserEntrySerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserEntry
        fields = '__all__'


class UserEntrySerializer2(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserEntry2
        fields = '__all__'


class UserEntrySerializerExpense(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserEntryExpense
        fields = '__all__'


class UserEntrySerializerOutofstock(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserEntryOutofstock
        fields = '__all__'


class StockReportSerializer(serializers.ModelSerializer):
    remaining_stock = serializers.SerializerMethodField()
    total_value_used = serializers.SerializerMethodField()
    total_value_unused = serializers.SerializerMethodField()

    class Meta:
        model = StockItem
        fields = ['name', 'quantity_used', 'remaining_stock', 'total_value_used', 'total_value_unused']

    def get_remaining_stock(self, obj):
        return obj.remaining_stock()

    def get_total_value_used(self, obj):
        return obj.total_value_used()

    def get_total_value_unused(self, obj):
        return obj.total_value_unused()


class StockItemRestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = ['name', 'quantity']


class StockItem2RestockSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem2
        fields = ['stock_name', 'area_in_square_meters']


class DebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debt
        fields = ['id', 'stock_name', 'debtor_name', 'stock_dimensions', 'amount',
                  'date', 'status', 'user']
        read_only_fields = ['user']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at', 'stock_item']


# ---------------------------------------------------------------------------
# User Companies Serializer — used by the company switcher
# ---------------------------------------------------------------------------

class UserCompanySerializer(serializers.ModelSerializer):
    """
    Returns the company info for a single CompanyMembership row.
    Used by /company/my-companies/ so the frontend can populate the switcher.
    """
    company_id   = serializers.IntegerField(source='company.id',   read_only=True)
    company_name = serializers.CharField(source='company.name',   read_only=True)
    is_access_valid = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()

    class Meta:
        model = CompanyMembership
        fields = ['company_id', 'company_name', 'role', 'is_access_valid', 'days_until_expiry']

    def get_is_access_valid(self, obj):
        return obj.company.is_access_valid()

    def get_days_until_expiry(self, obj):
        return obj.company.days_until_expiry()
