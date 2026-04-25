# from django.contrib import admin
# from .models import DataEntry, Debt, StockItem, StockItem2, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock

# @admin.register(DataEntry)
# class DataEntryAdmin(admin.ModelAdmin):
#     list_display = ('user', 'date', 'item_name', 'quantity', 'price', 'expense_name', 'expenses')
#     search_fields = ('user__username', 'item_name')
#     list_filter = ('date', 'user')

# @admin.register(StockItem)
# class StockItemAdmin(admin.ModelAdmin):
#     list_display = ('name', 'quantity', 'price_per_unit','quantity_used', "restock_quantity" ,"last_restock_date")

# @admin.register(StockItem2)
# class StockItemAdmin2(admin.ModelAdmin):
#     list_display = ('stock_name', 'area_in_square_meters', 'area_used_in_square_meters','price_per_square_meter','restock_area_in_square_meters','last_restock_date' )    

# @admin.register(UserEntry)
# class UserEntryAdmin(admin.ModelAdmin):
#     list_display = ('user', 'date', 'item_name', 'quantity', 'total_price', 'discount_price')

# @admin.register(UserEntry2)
# class UserEntryAdmin2(admin.ModelAdmin):
#     list_display = ('user', 'date', 'item_name', 'area_in_square_meters', 'total_price','discount_price')

# @admin.register(UserEntryExpense)
# class UserEntryAdminExpense(admin.ModelAdmin):
#     list_display = ('user', 'date', 'expense_name', 'expenses')

# @admin.register(UserEntryOutofstock)
# class UserEntryAdminOutofstock(admin.ModelAdmin):
#     list_display = ('user', 'date', 'name', 'price')    

# # Make sure you only register each model once.
# @admin.register(Debt)
# class DebtAdmin(admin.ModelAdmin):
#     list_display = ('user', 'debtor_name', 'stock_dimensions', 'stock_name', 'amount', 'date', 'status')
#     list_filter = ('status', 'date', 'user')
#     search_fields = ('debtor_name', 'stock_name', 'user__username')
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import (
    Company, CompanyMembership, PaymentRecord,
    DataEntry, Debt, StockItem, StockItem2,
    UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock,
)


# ---------------------------------------------------------------------------
# Inline: show payments inside the Company admin page
# ---------------------------------------------------------------------------

class PaymentRecordInline(admin.TabularInline):
    model = PaymentRecord
    extra = 1
    fields = ('amount_paid', 'payment_method', 'payment_date', 'months_granted', 'reference', 'recorded_by')
    readonly_fields = ('recorded_by',)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


class CompanyMembershipInline(admin.TabularInline):
    model = CompanyMembership
    extra = 0
    fields = ('user', 'role', 'created_at')
    readonly_fields = ('created_at',)


# ---------------------------------------------------------------------------
# Company Admin  — the main control panel for subscriptions
# ---------------------------------------------------------------------------

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'owner', 'status_badge', 'access_expires_at',
        'days_left', 'registered_at', 'grant_1_month_button',
    )
    list_filter = ('is_active',)
    search_fields = ('name', 'owner__username')
    readonly_fields = ('registered_at',)
    inlines = [PaymentRecordInline, CompanyMembershipInline]
    actions = ['grant_1_month', 'grant_3_months', 'revoke_access']

    fieldsets = (
        ('Company Info', {
            'fields': ('name', 'owner', 'registered_at', 'notes'),
        }),
        ('Access Control', {
            'fields': ('is_active', 'access_expires_at'),
            'description': (
                'Toggle is_active to immediately allow/block access. '
                'Set access_expires_at to auto-expire on a date.'
            ),
        }),
    )

    def status_badge(self, obj):
        if obj.is_access_valid():
            return format_html('<span style="color:green;font-weight:bold;">✓ Active</span>')
        elif obj.is_active:
            return format_html('<span style="color:orange;font-weight:bold;">⚠ Expired</span>')
        else:
            return format_html('<span style="color:red;font-weight:bold;">✗ Suspended</span>')
    status_badge.short_description = 'Status'

    def days_left(self, obj):
        d = obj.days_until_expiry()
        if d is None:
            return '—'
        if d == 0:
            return format_html('<span style="color:red;">Expired</span>')
        if d <= 5:
            return format_html(f'<span style="color:orange;">{d} days</span>')
        return f'{d} days'
    days_left.short_description = 'Days Left'

    def grant_1_month_button(self, obj):
        return format_html(
            '<a class="button" href="{}grant-access/?months=1" '
            'style="background:#28a745;color:white;padding:3px 8px;border-radius:4px;">'
            '+ 1 Month</a>',
            f'/admin/myapp/company/{obj.pk}/change/',
        )
    grant_1_month_button.short_description = 'Quick Grant'

    # Bulk actions
    @admin.action(description='Grant 1 month of access')
    def grant_1_month(self, request, queryset):
        for company in queryset:
            company.grant_access(months=1)
        self.message_user(request, f"Granted 1 month to {queryset.count()} company(ies).")

    @admin.action(description='Grant 3 months of access')
    def grant_3_months(self, request, queryset):
        for company in queryset:
            company.grant_access(months=3)
        self.message_user(request, f"Granted 3 months to {queryset.count()} company(ies).")

    @admin.action(description='Revoke access immediately')
    def revoke_access(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"Revoked access for {queryset.count()} company(ies).")

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, PaymentRecord) and not instance.pk:
                instance.recorded_by = request.user
            instance.save()
        formset.save_m2m()


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ('company', 'amount_paid', 'payment_method', 'payment_date', 'months_granted', 'recorded_by', 'reference')
    list_filter = ('payment_method', 'payment_date', 'company')
    search_fields = ('company__name', 'reference', 'recorded_by__username')
    readonly_fields = ('recorded_by', 'created_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.recorded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(CompanyMembership)
class CompanyMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'role', 'created_at')
    list_filter = ('role', 'company')
    search_fields = ('user__username', 'company__name')


# ---------------------------------------------------------------------------
# Existing model admins (unchanged, just registered)
# ---------------------------------------------------------------------------

@admin.register(DataEntry)
class DataEntryAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'date', 'item_name', 'quantity', 'price')
    search_fields = ('user__username', 'item_name', 'company__name')
    list_filter = ('date', 'company')


@admin.register(StockItem)
class StockItemAdmin(admin.ModelAdmin):
    list_display = ('company', 'name', 'quantity', 'price_per_unit', 'quantity_used', 'restock_quantity', 'last_restock_date')
    list_filter = ('company',)


@admin.register(StockItem2)
class StockItemAdmin2(admin.ModelAdmin):
    list_display = ('company', 'stock_name', 'area_in_square_meters', 'area_used_in_square_meters', 'price_per_square_meter', 'last_restock_date')
    list_filter = ('company',)


@admin.register(UserEntry)
class UserEntryAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'date', 'item_name', 'quantity', 'total_price', 'discount_price')
    list_filter = ('company',)


@admin.register(UserEntry2)
class UserEntryAdmin2(admin.ModelAdmin):
    list_display = ('company', 'user', 'date', 'item_name', 'area_in_square_meters', 'total_price', 'discount_price')
    list_filter = ('company',)


@admin.register(UserEntryExpense)
class UserEntryAdminExpense(admin.ModelAdmin):
    list_display = ('company', 'user', 'date', 'expense_name', 'expenses')
    list_filter = ('company',)


@admin.register(UserEntryOutofstock)
class UserEntryAdminOutofstock(admin.ModelAdmin):
    list_display = ('company', 'user', 'date', 'name', 'price')
    list_filter = ('company',)


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('company', 'user', 'debtor_name', 'stock_name', 'amount', 'date', 'status')
    list_filter = ('status', 'date', 'company')
    search_fields = ('debtor_name', 'stock_name', 'company__name')