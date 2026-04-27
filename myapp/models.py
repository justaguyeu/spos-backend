
  

# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator
# from decimal import Decimal, InvalidOperation
# from django.db.models import F


# # ---------------------------------------------------------------------------
# # Helper — defined first so models below can call it
# # ---------------------------------------------------------------------------

# def send_stock_notification(stock_item, stock_name, remaining_stock, model_type='units'):
#     """
#     Create an in-app Notification for the superuser when stock is low.
#     Correctly sets stock_item OR stock_item2 FK depending on which model called us.
#     """
#     try:
#         admin_user = User.objects.filter(is_superuser=True).first()
#         if admin_user is None:
#             print('No superuser found — notification skipped.')
#             return
#     except Exception as e:
#         print(f'Error finding admin user: {e}')
#         return

#     message = f"Stock Alert: {stock_name} has only {remaining_stock} {model_type} left."

#     if isinstance(stock_item, StockItem):
#         Notification.objects.create(
#             user=admin_user,
#             message=message,
#             is_read=False,
#             stock_item=stock_item,
#             stock_item2=None,
#         )
#     else:
#         Notification.objects.create(
#             user=admin_user,
#             message=message,
#             is_read=False,
#             stock_item=None,
#             stock_item2=stock_item,
#         )

#     print(f"Notification sent: {message}")


# # ---------------------------------------------------------------------------
# # Models
# # ---------------------------------------------------------------------------

# class DataEntry(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     date = models.DateField()
#     item_name = models.CharField(max_length=100)
#     quantity = models.IntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     expense_name = models.CharField(max_length=100, blank=True, null=True)
#     expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.item_name}"


# class Notification(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     # FIX: Previously both FKs were named `stock_item` — the second silently
#     # overwrote the first.  Now they have distinct names and related_names.
#     stock_item = models.ForeignKey(
#         'StockItem', null=True, blank=True, on_delete=models.CASCADE,
#         related_name='notifications',
#     )
#     stock_item2 = models.ForeignKey(
#         'StockItem2', null=True, blank=True, on_delete=models.CASCADE,
#         related_name='notifications',
#     )

#     def __str__(self):
#         return f"Notification for {self.user.username} - {self.message}"


# class NotificationPreference(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     email = models.EmailField(null=True, blank=True)
#     phone_number = models.CharField(max_length=15, null=True, blank=True)
#     receive_email = models.BooleanField(default=False)
#     receive_sms = models.BooleanField(default=False)
#     receive_push = models.BooleanField(default=False)
#     receive_phone_call = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user}'s notification preferences"


# # ---------------------------------------------------------------------------
# # StockItem  (unit-based stock, e.g. VIKOMBE MAGIC / VIKOMBE WHITE)
# # Threshold : notify when remaining <= 5 units
# # Hidden    : when remaining == 0  (AvailableStockItemsView filters these out)
# # ---------------------------------------------------------------------------

# LOW_STOCK_THRESHOLD_UNITS = 5


# class StockItem(models.Model):
#     name = models.CharField(max_length=100)
#     quantity = models.PositiveIntegerField()
#     quantity_used = models.PositiveIntegerField(default=0)
#     price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     added_date = models.DateField()
#     restock_quantity = models.PositiveIntegerField(default=0)
#     last_restock_date = models.DateField(null=True, blank=True)

#     # def remaining_stock(self):
#     #     """How many units are still available (never negative)."""
#     #     return max(0, self.quantity - self.quantity_used)
#     def remaining_stock(self):
#         return max(0, int(self.quantity) - int(self.quantity_used))

#     def total_value_used(self):
#         return self.quantity_used * self.price_per_unit

#     def total_value_unused(self):
#         return self.remaining_stock() * self.price_per_unit

#     def total_value_stock(self):
#         return self.quantity * self.price_per_unit

#     def is_depleted(self):
#         """True when zero units remain — item must not be shown to users."""
#         return self.remaining_stock() == 0

#     def get_month(self):
#         return self.added_date.strftime('%Y-%m')

#     def save(self, *args, **kwargs):
#         # ------------------------------------------------------------------
#         # Only send a notification when the remaining count actually drops
#         # INTO the low-stock zone (or decreases further inside it).
#         # This prevents spamming on every restock / unrelated save.
#         # ------------------------------------------------------------------
#         should_notify = False
#         # new_remaining = max(0, self.quantity - self.quantity_used)
#         new_remaining = max(0, int(self.quantity) - int(self.quantity_used))

#         if self.pk:
#             try:
#                 old = StockItem.objects.get(pk=self.pk)
#                 old_remaining = old.remaining_stock()
#                 # Notify only when count just crossed the threshold downward,
#                 # OR is already below threshold and decreased further.
#                 if new_remaining <= LOW_STOCK_THRESHOLD_UNITS and new_remaining < old_remaining:
#                     should_notify = True
#             except StockItem.DoesNotExist:
#                 pass
#         else:
#             # Brand-new item created already below threshold
#             if new_remaining <= LOW_STOCK_THRESHOLD_UNITS:
#                 should_notify = True

#         super().save(*args, **kwargs)

#         if should_notify:
#             send_stock_notification(
#                 stock_item=self,
#                 stock_name=self.name,
#                 remaining_stock=new_remaining,
#                 model_type='units',
#             )

#     def __str__(self):
#         return self.name


# # ---------------------------------------------------------------------------
# # StockItem2  (area-based stock, e.g. BANNER / STICKER)
# # Threshold : notify when remaining <= 10 square metres
# # Hidden    : when remaining == 0  (AvailableStockItemsView2 filters these out)
# # ---------------------------------------------------------------------------

# LOW_STOCK_THRESHOLD_SQM = Decimal('10')


# class StockItem2(models.Model):
#     stock_name = models.CharField(max_length=100)
#     area_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2)
#     area_used_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     price_per_square_meter = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     added_date = models.DateField()
#     restock_area_in_square_meters = models.PositiveIntegerField(default=0)
#     last_restock_date = models.DateField(null=True, blank=True)

#     def remaining_area(self):
#         """How many m² are still available (never negative)."""
#         return max(Decimal('0'), self.area_in_square_meters - self.area_used_in_square_meters)

#     def total_value_used(self):
#         return self.area_used_in_square_meters * self.price_per_square_meter

#     def total_value_unused(self):
#         return self.remaining_area() * self.price_per_square_meter

#     def total_value_stock(self):
#         return self.area_in_square_meters * self.price_per_square_meter

#     def is_depleted(self):
#         """True when zero m² remain — item must not be shown to users."""
#         return self.remaining_area() == Decimal('0')

#     def get_month(self):
#         return self.added_date.strftime('%Y-%m')

#     def save(self, *args, **kwargs):
#         should_notify = False
#         # new_remaining = max(
#         #     Decimal('0'),
#         #     self.area_in_square_meters - self.area_used_in_square_meters,
#         # )
#         new_remaining = max(
#             Decimal('0'),
#             Decimal(str(self.area_in_square_meters)) - Decimal(str(self.area_used_in_square_meters)),
# )

#         if self.pk:
#             try:
#                 old = StockItem2.objects.get(pk=self.pk)
#                 old_remaining = old.remaining_area()
#                 if new_remaining <= LOW_STOCK_THRESHOLD_SQM and new_remaining < old_remaining:
#                     should_notify = True
#             except StockItem2.DoesNotExist:
#                 pass
#         else:
#             if new_remaining <= LOW_STOCK_THRESHOLD_SQM:
#                 should_notify = True

#         super().save(*args, **kwargs)

#         if should_notify:
#             send_stock_notification(
#                 stock_item=self,
#                 stock_name=self.stock_name,
#                 remaining_stock=new_remaining,
#                 model_type='square meters',
#             )

#     def __str__(self):
#         return self.stock_name


# # ---------------------------------------------------------------------------
# # UserEntry / UserEntry2
# # ---------------------------------------------------------------------------

# class UserEntry(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     item_name = models.CharField(max_length=100)
#     quantity = models.PositiveIntegerField()
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     # def save(self, *args, **kwargs):
#     #     try:
#     #         stock_item = StockItem.objects.get(name=self.item_name)
#     #         remaining_stock = stock_item.remaining_stock()
#     #         if self.quantity > remaining_stock:
#     #             raise ValueError("Not enough stock available.")

#     #         if self.discount_price:
#     #             self.total_price = (self.quantity * stock_item.price_per_unit) - self.discount_price
#     #         else:
#     #             self.total_price = self.quantity * stock_item.price_per_unit

#     #         stock_item.quantity_used += self.quantity
#     #         stock_item.save()

#     #     except StockItem.DoesNotExist:
#     #         self.total_price = 0

#     #     if self.total_price < 0:
#     #         self.total_price = 0

#     #     super().save(*args, **kwargs)
#     def save(self, *args, **kwargs):
#         try:
#             stock_item = StockItem.objects.get(name=self.item_name)

#             # ── Determine old quantity if this is an UPDATE (not a new record) ──
#             if self.pk:
#                 try:
#                     old_instance = UserEntry.objects.get(pk=self.pk)
#                     old_quantity = old_instance.quantity
#                     old_item_name = old_instance.item_name
#                 except UserEntry.DoesNotExist:
#                     old_quantity = 0
#                     old_item_name = None
#             else:
#                 old_quantity = 0
#                 old_item_name = None

#             # ── If item_name changed, restore stock to the OLD item first ──
#             if old_item_name and old_item_name != self.item_name:
#                 try:
#                     old_stock_item = StockItem.objects.get(name=old_item_name)
#                     old_stock_item.quantity_used -= old_quantity
#                     old_stock_item.save()
#                 except StockItem.DoesNotExist:
#                     pass
#                 # For the new item, no old quantity to restore
#                 old_quantity = 0

#             # ── Check remaining stock accounting for the old quantity being freed ──
#             # remaining_stock() returns total added - quantity_used
#             # Since we haven't saved yet, we must add back old_quantity manually
#             remaining_stock = stock_item.remaining_stock() + old_quantity

#             if self.quantity > remaining_stock:
#                 raise ValueError("Not enough stock available.")

#             # ── Recalculate price ──
#             if self.discount_price:
#                 self.total_price = (self.quantity * stock_item.price_per_unit) - self.discount_price
#             else:
#                 self.total_price = self.quantity * stock_item.price_per_unit

#             # ── Update quantity_used: remove old, add new ──
#             stock_item.quantity_used = stock_item.quantity_used - old_quantity + self.quantity
#             stock_item.save()

#         except StockItem.DoesNotExist:
#             self.total_price = 0

#         if self.total_price < 0:
#             self.total_price = 0

#         super().save(*args, **kwargs)
#     def __str__(self):
#         return f"{self.user.username} - {self.item_name} - {self.date}"


# class UserEntry2(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     item_name = models.CharField(max_length=100)
#     area_in_square_meters = models.DecimalField(
#         max_digits=10,
#         decimal_places=5,
#         validators=[MinValueValidator(0)],
#     )
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     # def save(self, *args, **kwargs):
#     #     try:
#     #         stock_item = StockItem2.objects.get(stock_name=self.item_name)
#     #         remaining_area = stock_item.remaining_area()
#     #         if self.area_in_square_meters > remaining_area:
#     #             raise ValueError("Not enough stock available.")

#     #         if self.discount_price:
#     #             self.total_price = (
#     #                 self.area_in_square_meters * stock_item.price_per_square_meter
#     #             ) - self.discount_price
#     #         else:
#     #             self.total_price = self.area_in_square_meters * stock_item.price_per_square_meter

#     #         stock_item.area_used_in_square_meters += self.area_in_square_meters
#     #         stock_item.save()

#     #     except StockItem2.DoesNotExist:
#     #         self.total_price = 0

#     #     if self.total_price < 0:
#     #         self.total_price = 0

#     #     super().save(*args, **kwargs)
#     def save(self, *args, **kwargs):
#         try:
#             stock_item = StockItem2.objects.get(stock_name=self.item_name)

#             # ── Determine old area if this is an UPDATE (not a new record) ──
#             if self.pk:
#                 try:
#                     old_instance = UserEntry2.objects.get(pk=self.pk)
#                     old_area = old_instance.area_in_square_meters
#                     old_item_name = old_instance.item_name
#                 except UserEntry2.DoesNotExist:
#                     old_area = 0
#                     old_item_name = None
#             else:
#                 old_area = 0
#                 old_item_name = None

#             # ── If item_name changed, restore area to the OLD item first ──
#             if old_item_name and old_item_name != self.item_name:
#                 try:
#                     old_stock_item = StockItem2.objects.get(stock_name=old_item_name)
#                     old_stock_item.area_used_in_square_meters -= old_area
#                     old_stock_item.save()
#                 except StockItem2.DoesNotExist:
#                     pass
#                 # For the new item, no old area to restore
#                 old_area = 0

#             # ── Check remaining area accounting for the old area being freed ──
#             remaining_area = stock_item.remaining_area() + old_area

#             if self.area_in_square_meters > remaining_area:
#                 raise ValueError("Not enough stock available.")

#             # ── Recalculate price ──
#             if self.discount_price:
#                 self.total_price = (
#                     self.area_in_square_meters * stock_item.price_per_square_meter
#                 ) - self.discount_price
#             else:
#                 self.total_price = self.area_in_square_meters * stock_item.price_per_square_meter

#             # ── Update area_used: remove old, add new ──
#             stock_item.area_used_in_square_meters = (
#                 stock_item.area_used_in_square_meters - old_area + self.area_in_square_meters
#             )
#             stock_item.save()

#         except StockItem2.DoesNotExist:
#             self.total_price = 0

#         if self.total_price < 0:
#             self.total_price = 0

#         super().save(*args, **kwargs)
#     def __str__(self):
#         return f"{self.user.username} - {self.item_name} - {self.date}"


# class UserEntryExpense(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     expense_name = models.CharField(max_length=100, blank=True, null=True)
#     expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.expense_name} - {self.date}"


# class UserEntryOutofstock(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     name = models.CharField(max_length=100, blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.name} - {self.date}"


# class StockRestock(models.Model):
#     stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='restocks')
#     quantity = models.PositiveIntegerField()
#     restock_date = models.DateField()

#     def __str__(self):
#         return f"{self.stock_item.name} - {self.quantity} units on {self.restock_date}"


# class Debt(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('paid', 'Paid'),
#     ]

#     stock_name = models.CharField(max_length=100)
#     debtor_name = models.CharField(max_length=100)
#     stock_dimensions = models.CharField(max_length=100, blank=True, null=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     total_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

#     def save(self, *args, **kwargs):
#         try:
#             amount = Decimal(str(self.amount))
#             try:
#                 stock_item = StockItem.objects.get(name=self.stock_name)
#                 self.total_price = amount * Decimal(str(stock_item.price_per_unit))
#             except StockItem.DoesNotExist:
#                 try:
#                     stock_item2 = StockItem2.objects.get(stock_name=self.stock_name)
#                     self.total_price = amount * Decimal(str(stock_item2.price_per_square_meter))
#                 except StockItem2.DoesNotExist:
#                     self.total_price = amount

#             if self.total_price < Decimal('0'):
#                 self.total_price = Decimal('0')
#             if self.total_price > Decimal('99999999.99'):
#                 self.total_price = Decimal('99999999.99')

#         except (InvalidOperation, TypeError, ValueError):
#             self.total_price = Decimal('0')

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f'{self.debtor_name} owes {self.total_price} on {self.date}'

# from django.db import models
# from django.contrib.auth.models import User
# from django.core.validators import MinValueValidator
# from django.utils import timezone
# from decimal import Decimal, InvalidOperation
# from datetime import timedelta
# from django.db.models import F, Sum


# # ---------------------------------------------------------------------------
# # Company & Subscription
# # ---------------------------------------------------------------------------

# class Company(models.Model):
#     """
#     Every registered business is a Company.
#     The 'owner' is the company-admin (is_staff=True within their company scope).
#     The superuser (you) manages all companies.
#     """
#     name = models.CharField(max_length=200, unique=True)
#     owner = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='owned_company',
#     )
#     is_active = models.BooleanField(
#         default=False,
#         help_text="Superadmin toggles this after confirming payment.",
#     )
#     access_expires_at = models.DateTimeField(
#         null=True, blank=True,
#         help_text="When access expires. Null = no expiry (manual toggle only).",
#     )
#     registered_at = models.DateTimeField(auto_now_add=True)
#     notes = models.TextField(blank=True, null=True)

#     email = models.EmailField(blank=True, null=True)
#     phone_number = models.CharField(max_length=20, blank=True, null=True)
#     business_location = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#         verbose_name_plural = "Companies"

#     def is_access_valid(self):
#         """Returns True if company is active AND not past expiry (if set)."""
#         if not self.is_active:
#             return False
#         if self.access_expires_at and timezone.now() > self.access_expires_at:
#             return False
#         return True

#     def grant_access(self, months=1):
#         """Extend or set access by N months from now (or from current expiry)."""
#         now = timezone.now()
#         base = self.access_expires_at if (self.access_expires_at and self.access_expires_at > now) else now
#         self.access_expires_at = base + timedelta(days=30 * months)
#         self.is_active = True
#         self.save()

#     def revoke_access(self):
#         self.is_active = False
#         self.save()

#     def days_until_expiry(self):
#         if not self.access_expires_at:
#             return None
#         delta = self.access_expires_at - timezone.now()
#         return max(0, delta.days)

#     def __str__(self):
#         status = "✓" if self.is_access_valid() else "✗"
#         return f"[{status}] {self.name}"


# class PaymentRecord(models.Model):
#     """
#     Every time a company pays, superadmin logs it here and grants access.
#     """
#     PAYMENT_METHODS = [
#         ('cash', 'Cash'),
#         ('bank_transfer', 'Bank Transfer'),
#         ('mobile_money', 'Mobile Money'),
#         ('other', 'Other'),
#     ]

#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name='payments',
#     )
#     amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
#     payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='cash')
#     payment_date = models.DateField(default=timezone.now)
#     months_granted = models.PositiveIntegerField(
#         default=1,
#         help_text="How many months of access this payment grants.",
#     )
#     recorded_by = models.ForeignKey(
#         User,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='recorded_payments',
#     )
#     reference = models.CharField(max_length=200, blank=True, null=True)
#     notes = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.company.name} — {self.amount_paid} on {self.payment_date}"


# # ---------------------------------------------------------------------------
# # CompanyMembership: links regular users to a company
# # ---------------------------------------------------------------------------

# class CompanyMembership(models.Model):
#     ROLE_CHOICES = [
#         ('admin', 'Company Admin'),   # can create staff users within company
#         ('staff', 'Staff'),            # regular data-entry user
#     ]
#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='membership',
#     )
#     company = models.ForeignKey(
#         Company,
#         on_delete=models.CASCADE,
#         related_name='members',
#     )
#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} @ {self.company.name} ({self.role})"


# # ---------------------------------------------------------------------------
# # Helper
# # ---------------------------------------------------------------------------

# def send_stock_notification(stock_item, stock_name, remaining_stock, model_type='units'):
#     from .models import Notification  # avoid circular at module level
#     try:
#         # Notify the company owner, not the global superuser
#         if isinstance(stock_item, StockItem):
#             company = stock_item.company
#         else:
#             company = stock_item.company

#         admin_user = company.owner if company else User.objects.filter(is_superuser=True).first()
#         if admin_user is None:
#             return

#         message = f"Stock Alert: {stock_name} has only {remaining_stock} {model_type} left."

#         if isinstance(stock_item, StockItem):
#             Notification.objects.create(
#                 user=admin_user,
#                 message=message,
#                 is_read=False,
#                 stock_item=stock_item,
#                 stock_item2=None,
#                 company=company,
#             )
#         else:
#             Notification.objects.create(
#                 user=admin_user,
#                 message=message,
#                 is_read=False,
#                 stock_item=None,
#                 stock_item2=stock_item,
#                 company=company,
#             )

#         print(f"Notification sent: {message}")
#     except Exception as e:
#         print(f'Error sending notification: {e}')


# # ---------------------------------------------------------------------------
# # All data models are now scoped to a Company
# # ---------------------------------------------------------------------------

# class DataEntry(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='data_entries', null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     date = models.DateField()
#     item_name = models.CharField(max_length=100)
#     quantity = models.IntegerField()
#     price = models.DecimalField(max_digits=10, decimal_places=2)
#     expense_name = models.CharField(max_length=100, blank=True, null=True)
#     expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.item_name}"


# class Notification(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     message = models.TextField()
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     stock_item = models.ForeignKey(
#         'StockItem', null=True, blank=True, on_delete=models.CASCADE,
#         related_name='notifications',
#     )
#     stock_item2 = models.ForeignKey(
#         'StockItem2', null=True, blank=True, on_delete=models.CASCADE,
#         related_name='notifications',
#     )

#     def __str__(self):
#         return f"Notification for {self.user.username} - {self.message}"


# class NotificationPreference(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#     email = models.EmailField(null=True, blank=True)
#     phone_number = models.CharField(max_length=15, null=True, blank=True)
#     receive_email = models.BooleanField(default=False)
#     receive_sms = models.BooleanField(default=False)
#     receive_push = models.BooleanField(default=False)
#     receive_phone_call = models.BooleanField(default=False)

#     def __str__(self):
#         return f"{self.user}'s notification preferences"


# LOW_STOCK_THRESHOLD_UNITS = 5


# class StockItem(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_items', null=True)
#     name = models.CharField(max_length=100)
#     quantity = models.PositiveIntegerField()
#     quantity_used = models.PositiveIntegerField(default=0)
#     price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     added_date = models.DateField()
#     restock_quantity = models.PositiveIntegerField(default=0)
#     last_restock_date = models.DateField(null=True, blank=True)

#     class Meta:
#         unique_together = ('company', 'name')  # same item name OK across companies

#     def remaining_stock(self):
#         return max(0, int(self.quantity) - int(self.quantity_used))

#     def total_value_used(self):
#         return self.quantity_used * self.price_per_unit

#     def total_value_unused(self):
#         return self.remaining_stock() * self.price_per_unit

#     def total_value_stock(self):
#         return self.quantity * self.price_per_unit

#     def is_depleted(self):
#         return self.remaining_stock() == 0

#     def get_month(self):
#         return self.added_date.strftime('%Y-%m')

#     def save(self, *args, **kwargs):
#         should_notify = False
#         new_remaining = max(0, int(self.quantity) - int(self.quantity_used))

#         if self.pk:
#             try:
#                 old = StockItem.objects.get(pk=self.pk)
#                 old_remaining = old.remaining_stock()
#                 if new_remaining <= LOW_STOCK_THRESHOLD_UNITS and new_remaining < old_remaining:
#                     should_notify = True
#             except StockItem.DoesNotExist:
#                 pass
#         else:
#             if new_remaining <= LOW_STOCK_THRESHOLD_UNITS:
#                 should_notify = True

#         super().save(*args, **kwargs)

#         if should_notify:
#             send_stock_notification(self, self.name, new_remaining, 'units')

#     def __str__(self):
#         return f"{self.name} ({self.company.name if self.company else 'N/A'})"


# LOW_STOCK_THRESHOLD_SQM = Decimal('10')


# class StockItem2(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_items2', null=True)
#     stock_name = models.CharField(max_length=100)
#     area_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2)
#     area_used_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     price_per_square_meter = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
#     added_date = models.DateField()
#     restock_area_in_square_meters = models.PositiveIntegerField(default=0)
#     last_restock_date = models.DateField(null=True, blank=True)

#     class Meta:
#         unique_together = ('company', 'stock_name')

#     def remaining_area(self):
#         return max(Decimal('0'), self.area_in_square_meters - self.area_used_in_square_meters)

#     def total_value_used(self):
#         return self.area_used_in_square_meters * self.price_per_square_meter

#     def total_value_unused(self):
#         return self.remaining_area() * self.price_per_square_meter

#     def total_value_stock(self):
#         return self.area_in_square_meters * self.price_per_square_meter

#     def is_depleted(self):
#         return self.remaining_area() == Decimal('0')

#     def get_month(self):
#         return self.added_date.strftime('%Y-%m')

#     def save(self, *args, **kwargs):
#         should_notify = False
#         new_remaining = max(
#             Decimal('0'),
#             Decimal(str(self.area_in_square_meters)) - Decimal(str(self.area_used_in_square_meters)),
#         )

#         if self.pk:
#             try:
#                 old = StockItem2.objects.get(pk=self.pk)
#                 old_remaining = old.remaining_area()
#                 if new_remaining <= LOW_STOCK_THRESHOLD_SQM and new_remaining < old_remaining:
#                     should_notify = True
#             except StockItem2.DoesNotExist:
#                 pass
#         else:
#             if new_remaining <= LOW_STOCK_THRESHOLD_SQM:
#                 should_notify = True

#         super().save(*args, **kwargs)

#         if should_notify:
#             send_stock_notification(self, self.stock_name, new_remaining, 'square meters')

#     def __str__(self):
#         return f"{self.stock_name} ({self.company.name if self.company else 'N/A'})"


# class UserEntry(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_entries', null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     item_name = models.CharField(max_length=100)
#     quantity = models.PositiveIntegerField()
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def save(self, *args, **kwargs):
#         try:
#             # Scope stock lookup to the same company
#             stock_item = StockItem.objects.get(name=self.item_name, company=self.company)

#             if self.pk:
#                 try:
#                     old_instance = UserEntry.objects.get(pk=self.pk)
#                     old_quantity = old_instance.quantity
#                     old_item_name = old_instance.item_name
#                 except UserEntry.DoesNotExist:
#                     old_quantity = 0
#                     old_item_name = None
#             else:
#                 old_quantity = 0
#                 old_item_name = None

#             if old_item_name and old_item_name != self.item_name:
#                 try:
#                     old_stock_item = StockItem.objects.get(name=old_item_name, company=self.company)
#                     old_stock_item.quantity_used -= old_quantity
#                     old_stock_item.save()
#                 except StockItem.DoesNotExist:
#                     pass
#                 old_quantity = 0

#             remaining_stock = stock_item.remaining_stock() + old_quantity

#             if self.quantity > remaining_stock:
#                 raise ValueError("Not enough stock available.")

#             if self.discount_price:
#                 self.total_price = (self.quantity * stock_item.price_per_unit) - self.discount_price
#             else:
#                 self.total_price = self.quantity * stock_item.price_per_unit

#             stock_item.quantity_used = stock_item.quantity_used - old_quantity + self.quantity
#             stock_item.save()

#         except StockItem.DoesNotExist:
#             self.total_price = 0

#         if self.total_price < 0:
#             self.total_price = 0

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user.username} - {self.item_name} - {self.date}"


# class UserEntry2(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_entries2', null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     item_name = models.CharField(max_length=100)
#     area_in_square_meters = models.DecimalField(
#         max_digits=10,
#         decimal_places=5,
#         validators=[MinValueValidator(0)],
#     )
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def save(self, *args, **kwargs):
#         try:
#             stock_item = StockItem2.objects.get(stock_name=self.item_name, company=self.company)

#             if self.pk:
#                 try:
#                     old_instance = UserEntry2.objects.get(pk=self.pk)
#                     old_area = old_instance.area_in_square_meters
#                     old_item_name = old_instance.item_name
#                 except UserEntry2.DoesNotExist:
#                     old_area = 0
#                     old_item_name = None
#             else:
#                 old_area = 0
#                 old_item_name = None

#             if old_item_name and old_item_name != self.item_name:
#                 try:
#                     old_stock_item = StockItem2.objects.get(stock_name=old_item_name, company=self.company)
#                     old_stock_item.area_used_in_square_meters -= old_area
#                     old_stock_item.save()
#                 except StockItem2.DoesNotExist:
#                     pass
#                 old_area = 0

#             remaining_area = stock_item.remaining_area() + old_area

#             if self.area_in_square_meters > remaining_area:
#                 raise ValueError("Not enough stock available.")

#             if self.discount_price:
#                 self.total_price = (
#                     self.area_in_square_meters * stock_item.price_per_square_meter
#                 ) - self.discount_price
#             else:
#                 self.total_price = self.area_in_square_meters * stock_item.price_per_square_meter

#             stock_item.area_used_in_square_meters = (
#                 stock_item.area_used_in_square_meters - old_area + self.area_in_square_meters
#             )
#             stock_item.save()

#         except StockItem2.DoesNotExist:
#             self.total_price = 0

#         if self.total_price < 0:
#             self.total_price = 0

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f"{self.user.username} - {self.item_name} - {self.date}"


# class UserEntryExpense(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses', null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     expense_name = models.CharField(max_length=100, blank=True, null=True)
#     expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.expense_name} - {self.date}"


# class UserEntryOutofstock(models.Model):
#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='outofstock_entries', null=True)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     date = models.DateField()
#     name = models.CharField(max_length=100, blank=True, null=True)
#     price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.name} - {self.date}"


# class StockRestock(models.Model):
#     stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='restocks')
#     quantity = models.PositiveIntegerField()
#     restock_date = models.DateField()

#     def __str__(self):
#         return f"{self.stock_item.name} - {self.quantity} units on {self.restock_date}"


# class Debt(models.Model):
#     STATUS_CHOICES = [
#         ('pending', 'Pending'),
#         ('paid', 'Paid'),
#     ]

#     company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='debts', null=True)
#     stock_name = models.CharField(max_length=100)
#     debtor_name = models.CharField(max_length=100)
#     stock_dimensions = models.CharField(max_length=100, blank=True, null=True)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     date = models.DateField()
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     total_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

#     def save(self, *args, **kwargs):
#         try:
#             amount = Decimal(str(self.amount))
#             try:
#                 stock_item = StockItem.objects.get(name=self.stock_name, company=self.company)
#                 self.total_price = amount * Decimal(str(stock_item.price_per_unit))
#             except StockItem.DoesNotExist:
#                 try:
#                     stock_item2 = StockItem2.objects.get(stock_name=self.stock_name, company=self.company)
#                     self.total_price = amount * Decimal(str(stock_item2.price_per_square_meter))
#                 except StockItem2.DoesNotExist:
#                     self.total_price = amount

#             if self.total_price < Decimal('0'):
#                 self.total_price = Decimal('0')
#             if self.total_price > Decimal('99999999.99'):
#                 self.total_price = Decimal('99999999.99')

#         except (InvalidOperation, TypeError, ValueError):
#             self.total_price = Decimal('0')

#         super().save(*args, **kwargs)

#     def __str__(self):
#         return f'{self.debtor_name} owes {self.total_price} on {self.date}'
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from datetime import timedelta
from django.db.models import F, Sum


# ---------------------------------------------------------------------------
# Company & Subscription
# ---------------------------------------------------------------------------

class Company(models.Model):
    name = models.CharField(max_length=200, unique=True)
    owner = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='owned_company',
    )
    is_active = models.BooleanField(
        default=False,
        help_text="Superadmin toggles this after confirming payment.",
    )
    access_expires_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When access expires. Null = no expiry (manual toggle only).",
    )
    registered_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    business_location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-registered_at']

    def is_access_valid(self):
        if not self.is_active:
            return False
        if self.access_expires_at and timezone.now() > self.access_expires_at:
            return False
        return True

    def grant_access(self, months=1):
        now = timezone.now()
        base = self.access_expires_at if (self.access_expires_at and self.access_expires_at > now) else now
        self.access_expires_at = base + timedelta(days=30 * months)
        self.is_active = True
        self.save()

    def revoke_access(self):
        self.is_active = False
        self.save()

    def days_until_expiry(self):
        if not self.access_expires_at:
            return None
        delta = self.access_expires_at - timezone.now()
        return max(0, delta.days)

    def __str__(self):
        status = "✓" if self.is_access_valid() else "✗"
        return f"[{status}] {self.name}"


class PaymentRecord(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('other', 'Other'),
    ]

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='payments',
    )
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PAYMENT_METHODS, default='cash')
    payment_date = models.DateField(default=timezone.now)
    months_granted = models.PositiveIntegerField(
        default=1,
        help_text="How many months of access this payment grants.",
    )
    recorded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='recorded_payments',
    )
    reference = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-payment_date', '-created_at']

    def __str__(self):
        return f"{self.company.name} — {self.amount_paid} on {self.payment_date}"


# ---------------------------------------------------------------------------
# CompanyMembership
# ---------------------------------------------------------------------------

class CompanyMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Company Admin'),
        ('staff', 'Staff'),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='membership',
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='members',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['company', 'role']

    def __str__(self):
        return f"{self.user.username} @ {self.company.name} ({self.role})"


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def send_stock_notification(stock_item, stock_name, remaining_stock, model_type='units'):
    from .models import Notification
    try:
        if isinstance(stock_item, StockItem):
            company = stock_item.company
        else:
            company = stock_item.company

        admin_user = company.owner if company else User.objects.filter(is_superuser=True).first()
        if admin_user is None:
            return

        message = f"Stock Alert: {stock_name} has only {remaining_stock} {model_type} left."

        if isinstance(stock_item, StockItem):
            Notification.objects.create(
                user=admin_user,
                message=message,
                is_read=False,
                stock_item=stock_item,
                stock_item2=None,
                company=company,
            )
        else:
            Notification.objects.create(
                user=admin_user,
                message=message,
                is_read=False,
                stock_item=None,
                stock_item2=stock_item,
                company=company,
            )

        print(f"Notification sent: {message}")
    except Exception as e:
        print(f'Error sending notification: {e}')


# ---------------------------------------------------------------------------
# Data models — all scoped to a Company
# ---------------------------------------------------------------------------

class DataEntry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='data_entries', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    item_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    expense_name = models.CharField(max_length=100, blank=True, null=True)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']

    def __str__(self):
        return f"{self.user.username} - {self.item_name}"


class Notification(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    stock_item = models.ForeignKey(
        'StockItem', null=True, blank=True, on_delete=models.CASCADE,
        related_name='notifications',
    )
    stock_item2 = models.ForeignKey(
        'StockItem2', null=True, blank=True, on_delete=models.CASCADE,
        related_name='notifications',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.username} - {self.message}"


class NotificationPreference(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    receive_email = models.BooleanField(default=False)
    receive_sms = models.BooleanField(default=False)
    receive_push = models.BooleanField(default=False)
    receive_phone_call = models.BooleanField(default=False)

    class Meta:
        ordering = ['user']

    def __str__(self):
        return f"{self.user}'s notification preferences"


LOW_STOCK_THRESHOLD_UNITS = 5


class StockItem(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_items', null=True)
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    quantity_used = models.PositiveIntegerField(default=0)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    added_date = models.DateField()
    restock_quantity = models.PositiveIntegerField(default=0)
    last_restock_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('company', 'name')
        ordering = ['name']

    def remaining_stock(self):
        return max(0, int(self.quantity) - int(self.quantity_used))

    def total_value_used(self):
        return self.quantity_used * self.price_per_unit

    def total_value_unused(self):
        return self.remaining_stock() * self.price_per_unit

    def total_value_stock(self):
        return self.quantity * self.price_per_unit

    def is_depleted(self):
        return self.remaining_stock() == 0

    def get_month(self):
        return self.added_date.strftime('%Y-%m')

    def save(self, *args, **kwargs):
        should_notify = False
        new_remaining = max(0, int(self.quantity) - int(self.quantity_used))

        if self.pk:
            try:
                old = StockItem.objects.get(pk=self.pk)
                old_remaining = old.remaining_stock()
                if new_remaining <= LOW_STOCK_THRESHOLD_UNITS and new_remaining < old_remaining:
                    should_notify = True
            except StockItem.DoesNotExist:
                pass
        else:
            if new_remaining <= LOW_STOCK_THRESHOLD_UNITS:
                should_notify = True

        super().save(*args, **kwargs)

        if should_notify:
            send_stock_notification(self, self.name, new_remaining, 'units')

    def __str__(self):
        return f"{self.name} ({self.company.name if self.company else 'N/A'})"


LOW_STOCK_THRESHOLD_SQM = Decimal('10')


class StockItem2(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='stock_items2', null=True)
    stock_name = models.CharField(max_length=100)
    area_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2)
    area_used_in_square_meters = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_per_square_meter = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    added_date = models.DateField()
    restock_area_in_square_meters = models.PositiveIntegerField(default=0)
    last_restock_date = models.DateField(null=True, blank=True)

    class Meta:
        unique_together = ('company', 'stock_name')
        ordering = ['stock_name']

    def remaining_area(self):
        return max(Decimal('0'), self.area_in_square_meters - self.area_used_in_square_meters)

    def total_value_used(self):
        return self.area_used_in_square_meters * self.price_per_square_meter

    def total_value_unused(self):
        return self.remaining_area() * self.price_per_square_meter

    def total_value_stock(self):
        return self.area_in_square_meters * self.price_per_square_meter

    def is_depleted(self):
        return self.remaining_area() == Decimal('0')

    def get_month(self):
        return self.added_date.strftime('%Y-%m')

    def save(self, *args, **kwargs):
        should_notify = False
        new_remaining = max(
            Decimal('0'),
            Decimal(str(self.area_in_square_meters)) - Decimal(str(self.area_used_in_square_meters)),
        )

        if self.pk:
            try:
                old = StockItem2.objects.get(pk=self.pk)
                old_remaining = old.remaining_area()
                if new_remaining <= LOW_STOCK_THRESHOLD_SQM and new_remaining < old_remaining:
                    should_notify = True
            except StockItem2.DoesNotExist:
                pass
        else:
            if new_remaining <= LOW_STOCK_THRESHOLD_SQM:
                should_notify = True

        super().save(*args, **kwargs)

        if should_notify:
            send_stock_notification(self, self.stock_name, new_remaining, 'square meters')

    def __str__(self):
        return f"{self.stock_name} ({self.company.name if self.company else 'N/A'})"


class UserEntry(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_entries', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    item_name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']   # ← fixes the UnorderedObjectListWarning

    def save(self, *args, **kwargs):
        try:
            stock_item = StockItem.objects.get(name=self.item_name, company=self.company)

            if self.pk:
                try:
                    old_instance = UserEntry.objects.get(pk=self.pk)
                    old_quantity = old_instance.quantity
                    old_item_name = old_instance.item_name
                except UserEntry.DoesNotExist:
                    old_quantity = 0
                    old_item_name = None
            else:
                old_quantity = 0
                old_item_name = None

            if old_item_name and old_item_name != self.item_name:
                try:
                    old_stock_item = StockItem.objects.get(name=old_item_name, company=self.company)
                    old_stock_item.quantity_used -= old_quantity
                    old_stock_item.save()
                except StockItem.DoesNotExist:
                    pass
                old_quantity = 0

            remaining_stock = stock_item.remaining_stock() + old_quantity

            if self.quantity > remaining_stock:
                raise ValueError("Not enough stock available.")

            if self.discount_price:
                self.total_price = (self.quantity * stock_item.price_per_unit) - self.discount_price
            else:
                self.total_price = self.quantity * stock_item.price_per_unit

            stock_item.quantity_used = stock_item.quantity_used - old_quantity + self.quantity
            stock_item.save()

        except StockItem.DoesNotExist:
            self.total_price = 0

        if self.total_price < 0:
            self.total_price = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.item_name} - {self.date}"


class UserEntry2(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='user_entries2', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    item_name = models.CharField(max_length=100)
    area_in_square_meters = models.DecimalField(
        max_digits=10,
        decimal_places=5,
        validators=[MinValueValidator(0)],
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']   # ← fixes the UnorderedObjectListWarning

    def save(self, *args, **kwargs):
        try:
            stock_item = StockItem2.objects.get(stock_name=self.item_name, company=self.company)

            if self.pk:
                try:
                    old_instance = UserEntry2.objects.get(pk=self.pk)
                    old_area = old_instance.area_in_square_meters
                    old_item_name = old_instance.item_name
                except UserEntry2.DoesNotExist:
                    old_area = 0
                    old_item_name = None
            else:
                old_area = 0
                old_item_name = None

            if old_item_name and old_item_name != self.item_name:
                try:
                    old_stock_item = StockItem2.objects.get(stock_name=old_item_name, company=self.company)
                    old_stock_item.area_used_in_square_meters -= old_area
                    old_stock_item.save()
                except StockItem2.DoesNotExist:
                    pass
                old_area = 0

            remaining_area = stock_item.remaining_area() + old_area

            if self.area_in_square_meters > remaining_area:
                raise ValueError("Not enough stock available.")

            if self.discount_price:
                self.total_price = (
                    self.area_in_square_meters * stock_item.price_per_square_meter
                ) - self.discount_price
            else:
                self.total_price = self.area_in_square_meters * stock_item.price_per_square_meter

            stock_item.area_used_in_square_meters = (
                stock_item.area_used_in_square_meters - old_area + self.area_in_square_meters
            )
            stock_item.save()

        except StockItem2.DoesNotExist:
            self.total_price = 0

        if self.total_price < 0:
            self.total_price = 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.item_name} - {self.date}"


class UserEntryExpense(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='expenses', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    expense_name = models.CharField(max_length=100, blank=True, null=True)
    expenses = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']   # ← fixes the UnorderedObjectListWarning

    def __str__(self):
        return f"{self.user.username} - {self.expense_name} - {self.date}"


class UserEntryOutofstock(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='outofstock_entries', null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    name = models.CharField(max_length=100, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']   # ← fixes the UnorderedObjectListWarning

    def __str__(self):
        return f"{self.user.username} - {self.name} - {self.date}"


class StockRestock(models.Model):
    stock_item = models.ForeignKey(StockItem, on_delete=models.CASCADE, related_name='restocks')
    quantity = models.PositiveIntegerField()
    restock_date = models.DateField()

    class Meta:
        ordering = ['-restock_date']

    def __str__(self):
        return f"{self.stock_item.name} - {self.quantity} units on {self.restock_date}"


class Debt(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='debts', null=True)
    stock_name = models.CharField(max_length=100)
    debtor_name = models.CharField(max_length=100)
    stock_dimensions = models.CharField(max_length=100, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)

    class Meta:
        ordering = ['-date', '-id']   # ← fixes the UnorderedObjectListWarning

    def save(self, *args, **kwargs):
        try:
            amount = Decimal(str(self.amount))
            try:
                stock_item = StockItem.objects.get(name=self.stock_name, company=self.company)
                self.total_price = amount * Decimal(str(stock_item.price_per_unit))
            except StockItem.DoesNotExist:
                try:
                    stock_item2 = StockItem2.objects.get(stock_name=self.stock_name, company=self.company)
                    self.total_price = amount * Decimal(str(stock_item2.price_per_square_meter))
                except StockItem2.DoesNotExist:
                    self.total_price = amount

            if self.total_price < Decimal('0'):
                self.total_price = Decimal('0')
            if self.total_price > Decimal('99999999.99'):
                self.total_price = Decimal('99999999.99')

        except (InvalidOperation, TypeError, ValueError):
            self.total_price = Decimal('0')

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.debtor_name} owes {self.total_price} on {self.date}'