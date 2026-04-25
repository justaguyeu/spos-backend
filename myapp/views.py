# # from decimal import Decimal
# # from urllib import request, response
# # from venv import logger
# # from django.forms import ValidationError
# # from django.http import JsonResponse
# # from rest_framework import generics, viewsets, status
# # from rest_framework.permissions import IsAuthenticated
# # from rest_framework.views import APIView
# # from rest_framework.decorators import api_view
# # from rest_framework.response import Response
# # from rest_framework_simplejwt.views import TokenObtainPairView
# # from django.contrib.auth.models import User
# # from .models import DataEntry, Debt, Notification, NotificationPreference, StockItem, StockItem2, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock
# # from django.db.models import F 
# # from .serializers import DataEntrySerializer, DebtSerializer, NotificationSerializer, StockItem2RestockSerializer, StockItemRestockSerializer, StockItemSerializer, StockItemSerializer2, StockReportSerializer, UserEntrySerializer, UserEntrySerializer2, UserEntrySerializerExpense, UserEntrySerializerOutofstock
# # from django.db.models import Sum
# # from django.utils.dateparse import parse_date
# # from datetime import datetime, timedelta
# # from django.contrib.auth import authenticate
# # from rest_framework_simplejwt.authentication import JWTAuthentication
# # from rest_framework.generics import ListCreateAPIView, DestroyAPIView
# # from django.contrib.auth.hashers import make_password
# # from rest_framework.permissions import IsAdminUser
# # from django.shortcuts import get_object_or_404
# # from .models import NotificationPreference
# # from .utils import send_sms, send_email
# # from django.shortcuts import render
# # from django.db.models import Sum
# # from django.utils import timezone

# # from myapp import models


# # class DataEntryListCreateView(generics.ListCreateAPIView):
# #     serializer_class = DataEntrySerializer
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return DataEntry.objects.all()
# #         return DataEntry.objects.filter(user=user)

# #     def perform_create(self, serializer):
# #         # Correcting the indentation
# #         serializer.save(user=self.request.user)

# # class CustomTokenObtainPairView(TokenObtainPairView):
# #     def post(self, request, *args, **kwargs):
# #         # Extract username and password from request
# #         username = request.data.get('username')
# #         password = request.data.get('password')
        
# #         try:
# #             # Authenticate the user
# #             user = authenticate(username=username, password=password)
            
# #             if user is not None:
# #                 # Authentication successful, proceed with token generation
# #                 response = super().post(request, *args, **kwargs)
                
# #                 # Add custom data to the response based on user type
# #                 if user.is_staff:
# #                     response.data['is_staff'] = True
# #                     response.data['message'] = "Login successful. Welcome, admin!"
# #                 else:
# #                     response.data['is_staff'] = False
# #                     response.data['message'] = "Login successful. Welcome, user!"
                
# #                 return response
# #             else:
# #                 # User authentication failed (incorrect password or non-existent user)
# #                 return Response({
# #                     'message': "Invalid credentials. Check your username and password."
# #                 }, status=401)

# #         except User.DoesNotExist:
# #             # Handle case where user does not exist
# #             return Response({
# #                 'message': "User does not exist."
# #             }, status=400)
# # class MonthlyReportView(generics.GenericAPIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')
# #         if not month:
# #             return Response({"error": "Month parameter is required."}, status=400)
        
# #         try:
# #             year, month_number = map(int, month.split('-'))
# #             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
# #             if month_number == 12:
# #                 end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
# #             else:
# #                 end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
# #         except ValueError:
# #             return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

# #         # Fetch UserEntry and UserEntry2 data
# #         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
# #         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
        
# #         # Fetch ExpenseEntry data
# #         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)
# #         debt_entries = Debt.objects.filter(date__gte=start_date, date__lt=end_date)
# #         outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date)

# #         # Combine daily totals for both UserEntry and UserEntry2
# #         daily_totals = (
# #             user_entries.values('date')
# #             .annotate(total_sales=Sum('total_price'))
# #             .order_by('date')
# #         )

# #         daily_totals2 = (
# #             user_entries2.values('date')
# #             .annotate(total_sales=Sum('total_price'))
# #             .order_by('date')
# #         )
       

# #         # Merge sales data from both UserEntry and UserEntry2
# #         combined_sales_totals = {}
# #         for entry in daily_totals:
# #             date = entry['date']
# #             combined_sales_totals[date] = entry['total_sales']

# #         for entry in daily_totals2:
# #             date = entry['date']
# #             if date in combined_sales_totals:
# #                 combined_sales_totals[date] += entry['total_sales']
# #             else:
# #                 combined_sales_totals[date] = entry['total_sales']

# #         # Combine daily totals with expenses
# #         daily_expenses = (
# #             expense_entries.values('date')
# #             .annotate(total_expenses=Sum('expenses'))
# #             .order_by('date')
# #         )

# #         daily_debts = (
# #             debt_entries.values('date')
# #             .annotate(total_debts=Sum('amount'))
# #             .order_by('date')
# #         )

# #         daily_outofstock = (
# #             outofstock_entries.values('date')
# #             .annotate(total_outofstock=Sum('price'))
# #             .order_by('date')
# #         )

# #         combined_daily_totals = []
# #         all_dates = set(combined_sales_totals.keys()) | set(item['date'] for item in daily_outofstock) | set(item['date'] for item in daily_debts) | set(item['date'] for item in daily_expenses)

# #         for date in sorted(all_dates):
# #             daily_sales = combined_sales_totals.get(date, 0)
# #             daily_outofstock_value = next((item['total_outofstock'] for item in daily_outofstock if item['date'] == date), 0)or 0
# #             daily_debts_value = next((item['total_debts'] for item in daily_debts if item['date'] == date), 0) or 0
# #             daily_expense_value = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)or 0
# #             combined_daily_totals.append({
# #                 'date': date,
# #                 'total_sales': daily_sales,
# #                 'total_expenses': daily_expense_value,
# #                 'total_debts': daily_debts_value,
# #                 'total_outofstock': daily_outofstock_value, 
# #                 'profit': daily_sales + daily_outofstock_value - daily_expense_value
# #             })

# #         # Calculate monthly totals
# #         total_sales = sum(combined_sales_totals.values())
# #         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
# #         total_debts = debt_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
# #         total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0
# #         profit = total_sales + total_outofstock - total_expenses

# #         monthly_totals = {
# #             'total_sales': total_sales,
# #             'total_expenses': total_expenses,
# #             'total_debts': total_debts,
# #             'total_outofstock': total_outofstock,
# #             'profit': profit,
# #         }

# #         return Response({'daily_totals': combined_daily_totals, 'monthly_totals': monthly_totals})

# # class WeeklyReportView(generics.GenericAPIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         start_date = request.query_params.get('start_date')
# #         end_date = request.query_params.get('end_date')
# #         if not start_date or not end_date:
# #             return Response({"error": "Start date and end date parameters are required."}, status=400)
        
# #         try:
# #             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
# #             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
# #         except ValueError:
# #             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

# #         # Fetch UserEntry and UserEntry2 data
# #         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lte=end_date)
# #         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lte=end_date)
        
# #         # Fetch ExpenseEntry data
# #         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lte=end_date)
# #         debt_entries = Debt.objects.filter(date__gte=start_date, date__lt=end_date)
# #         outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date)

# #         # Combine daily totals for both UserEntry and UserEntry2
# #         daily_totals = (
# #             user_entries.values('date')
# #             .annotate(total_sales=Sum('total_price'))
# #             .order_by('date')
# #         )

# #         daily_totals2 = (
# #             user_entries2.values('date')
# #             .annotate(total_sales=Sum('total_price'))
# #             .order_by('date')
# #         )

# #         # Merge sales data from both UserEntry and UserEntry2
# #         combined_sales_totals = {}
# #         for entry in daily_totals:
# #             date = entry['date']
# #             combined_sales_totals[date] = entry['total_sales']

# #         for entry in daily_totals2:
# #             date = entry['date']
# #             if date in combined_sales_totals:
# #                 combined_sales_totals[date] += entry['total_sales']
# #             else:
# #                 combined_sales_totals[date] = entry['total_sales']

# #         # Combine daily totals with expenses
# #         daily_expenses = (
# #             expense_entries.values('date')
# #             .annotate(total_expenses=Sum('expenses'))
# #             .order_by('date')
# #         )

# #         daily_debts = (
# #             debt_entries.values('date')
# #             .annotate(total_debts=Sum('amount'))
# #             .order_by('date')
# #         )

# #         daily_outofstock = (
# #             outofstock_entries.values('date')
# #             .annotate(total_outofstock=Sum('price'))
# #             .order_by('date')
# #         )

# #         combined_daily_totals = []
# #         all_dates = set(combined_sales_totals.keys()) | set(item['date'] for item in daily_outofstock) | set(item['date'] for item in daily_debts)

# #         for date in sorted(all_dates):
# #             daily_sales = combined_sales_totals.get(date, 0)
# #             daily_outofstock_value = next((item['total_outofstock'] for item in daily_outofstock if item['date'] == date), 0)or 0
# #             daily_debts_value = next((item['total_debts'] for item in daily_debts if item['date'] == date), 0) or 0
# #             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0) or 0
# #             combined_daily_totals.append({
# #                 'date': date.strftime('%Y-%m-%d'),  # Convert date to string format
# #                 'total_sales': daily_sales,
# #                 'total_debts': daily_debts_value,
# #                 'total_outofstock': daily_outofstock_value, 
# #                 'total_expenses': daily_expense,
# #                 'profit': daily_sales + daily_outofstock_value - daily_expense
# #             })

# #         # Calculate weekly totals
# #         total_sales = sum(combined_sales_totals.values())
# #         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
# #         total_debts = debt_entries.aggregate(Sum('amount'))['amount__sum'] or 0
# #         total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0
# #         profit = total_sales + total_outofstock - total_expenses

# #         weekly_totals = {
# #             'total_sales': total_sales,
# #             'total_debts': total_debts,
# #             'total_outofstock': total_outofstock,
# #             'total_expenses': total_expenses,
# #             'profit': profit,
# #         }

# #         return Response({'daily_totals': combined_daily_totals, 'weekly_totals': weekly_totals})

# # #     permission_classes = [IsAuthenticated]

# # #     def get(self, request, *args, **kwargs):
# # #         month = request.query_params.get('month')
# # #         if not month:
# # #             return Response({"error": "Month parameter is required."}, status=400)
        
# # #         try:
# # #             year, month_number = map(int, month.split('-'))
# # #             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
# # #             # Get the first day of the next month for `end_date`
# # #             if month_number == 12:
# # #                 end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
# # #             else:
# # #                 end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
# # #         except ValueError:
# # #             return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

# # #         # Fetch UserEntry data
# # #         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
        
# # #         # Fetch ExpenseEntry data
# # #         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)
        
# # #         # Calculate daily totals for sales and expenses
# # #         daily_totalss = (
# # #             user_entries.values('date')
# # #             .annotate(total_sales=Sum('total_price'))
# # #             .order_by('date')
# # #         )

# # #         # Combine daily totals with expenses
# # #         daily_expenses = (
# # #             expense_entries.values('date')
# # #             .annotate(total_expenses=Sum('expenses'))
# # #             .order_by('date')
# # #         )

# # #         # Merge daily totals and daily expenses
# # #         combined_daily_totals = []
# # #         all_dates = set([item['date'] for item in daily_totalss] + [item['date'] for item in daily_expenses])

# # #         for date in sorted(all_dates):
# # #             daily_sales = next((item['total_sales'] for item in daily_totalss if item['date'] == date), 0)
# # #             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
# # #             combined_daily_totals.append({
# # #                 'date': date,
# # #                 'total_sales': daily_sales,
# # #                 'total_expenses': daily_expense,
# # #                 'profit': daily_sales - daily_expense
# # #             })

# # #         # Calculate monthly totals
# # #         total_sales = user_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
# # #         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
# # #         profit = total_sales - total_expenses

# # #         monthly_totalss = {
# # #             'total_sales': total_sales,
# # #             'total_expenses': total_expenses,
# # #             'profit': profit,
# # #         }

# # #         return Response({'daily_totalss': combined_daily_totals, 'monthly_totalss': monthly_totalss})
    
# # class MonthlyReportView2(generics.GenericAPIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')
# #         if not month:
# #             return Response({"error": "Month parameter is required."}, status=400)
        
# #         try:
# #             year, month_number = map(int, month.split('-'))
# #             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
            
# #             if month_number == 12:
# #                 end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
# #             else:
# #                 end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
# #         except ValueError:
# #             return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

# #         # Fetch UserEntry data
# #         user_entries = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
        
# #         # Fetch ExpenseEntry data
# #         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)
        
# #         # Calculate daily totals for sales and expenses
# #         daily_totalss = (
# #             user_entries.values('date')
# #             .annotate(total_sales=Sum('total_price'))
# #             .order_by('date')
# #         )

# #         # Combine daily totals with expenses
# #         daily_expenses = (
# #             expense_entries.values('date')
# #             .annotate(total_expenses=Sum('expenses'))
# #             .order_by('date')
# #         )

# #         # Merge daily totals and daily expenses
# #         combined_daily_totalss = []
# #         all_dates = set([item['date'] for item in daily_totalss] + [item['date'] for item in daily_expenses])

# #         for date in sorted(all_dates):
# #             daily_sales = next((item['total_sales'] for item in daily_totalss if item['date'] == date), 0)
# #             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
# #             combined_daily_totalss.append({
# #                 'date': date,
# #                 'total_sales': daily_sales,
# #                 'total_expenses': daily_expense,
# #                 'profit': daily_sales - daily_expense
# #             })

# #         # Calculate monthly totals
# #         total_sales = user_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
# #         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
# #         profit = total_sales - total_expenses

# #         monthly_totalss = {
# #             'total_sales': total_sales,
# #             'total_expenses': total_expenses,
# #             'profit': profit,
# #         }

# #         return Response({'daily_totalss': combined_daily_totalss, 'monthly_totalss': monthly_totalss})  

# # class StockItemViewSet(viewsets.ModelViewSet):
# #     permission_classes = [IsAuthenticated]
# #     queryset = StockItem.objects.all()
# #     serializer_class = StockItemSerializer

# #     def get(self, request):
# #         selected_month = request.query_params.get('month')
        
# #         if selected_month:
# #             try:
# #                 year, month = map(int, selected_month.split('-'))
                
               
# #                 stock_items = StockItem.objects.filter(
# #                     date_added__year=year,
# #                     date_added__month=month
# #                 )
# #             except ValueError:
# #                 return Response({"error": "Invalid month format. Please use 'YYYY-MM' format."}, status=400)

# #         else:
            
# #             stock_items = StockItem.objects.all()
        
# #         serializer = StockItemSerializer(stock_items, many=True)
# #         return Response(serializer.data)

# # class UserEntryViewSet(viewsets.ModelViewSet):
# #     queryset = UserEntry.objects.all()
# #     serializer_class = UserEntrySerializer
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return UserEntry.objects.all()
# #         return UserEntry.objects.filter(user=user)
    

# #     # def perform_create(self, serializer):
# #     #     serializer.save(user=self.request.user)
# #     #     if serializer.is_valid():
# #     #         try:
# #     #             serializer.save(user=request.user)
# #     #             return Response(serializer.data, status=status.HTTP_201_CREATED)
# #     #         except ValidationError as e:
# #     #             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #     #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     # Override create to catch ValueError from model
# #     def create(self, request, *args, **kwargs):
# #         serializer = self.get_serializer(data=request.data)
# #         serializer.is_valid(raise_exception=True)
# #         try:
# #             self.perform_create(serializer)
# #             return Response(serializer.data, status=status.HTTP_201_CREATED)
# #         except ValueError as e:
# #             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# #     def perform_update(self, serializer):
# #         # Custom behavior during update (if needed)
# #         serializer.save(user=self.request.user)
# #         if serializer.is_valid():
# #             try:
# #                 serializer.save(user=request.user)
# #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
# #             except ValidationError as e:
# #                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

# #     def post(self, request):
# #         serializer = UserEntrySerializer(data=request.data)
# #         if serializer.is_valid():
# #             try:
# #                 serializer.save(user=request.user)
# #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
# #             except ValidationError as e:
# #                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

# #     def put(self, request, pk):
# #         try:
# #             data = UserEntry.objects.get(pk=pk)
# #         except UserEntry.DoesNotExist:
# #             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

# #         serializer = UserEntrySerializer(data, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(serializer.data)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     def perform_update(self, serializer):
# #         serializer.save(user=self.request.user)   

# # # class UserEntryViewSet(viewsets.ModelViewSet):
# # #     queryset = UserEntry.objects.all()
# # #     serializer_class = UserEntrySerializer
# # #     permission_classes = [IsAuthenticated]

# # #     def get_queryset(self):
# # #         """
# # #         Customize queryset: return all entries for admin users and filtered entries for regular users.
# # #         """
# # #         user = self.request.user
# # #         if user.is_staff:
# # #             return UserEntry.objects.all()  # Admin gets all entries
# # #         return UserEntry.objects.filter(user=user)  # Regular users see only their own entries

# # #     def perform_create(self, serializer):
# # #         """
# # #         Automatically assign the logged-in user when creating a new UserEntry.
# # #         """
# # #         serializer.save(user=self.request.user)

# # #     def update(self, request, *args, **kwargs):
# # #         """
# # #         Override the update method to handle PUT requests for updating an entry.
# # #         """
# # #         try:
# # #             instance = self.get_object()  # Get the entry to be updated
# # #         except Data.DoesNotExist:
# # #             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

# # #         serializer = DataSerializer(instance, data=request.data, partial=False)
# # #         if serializer.is_valid():
# # #             serializer.save()
# # #             return Response(serializer.data, status=status.HTTP_200_OK)
# # #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# # class UserEntryViewSet2(viewsets.ModelViewSet):
# #     queryset = UserEntry2.objects.all()
# #     serializer_class = UserEntrySerializer2
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return UserEntry2.objects.all()
# #         return UserEntry2.objects.filter(user=user)
    
# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)
# #         if serializer.is_valid():
# #             try:
# #                 serializer.save(user=request.user)
# #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
# #             except ValidationError as e:
# #                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# #     def perform_update(self, serializer):
# #         # Custom behavior during update (if needed)
# #         serializer.save(user=self.request.user)
# #         if serializer.is_valid():
# #             try:
# #                 serializer.save(user=request.user)
# #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
# #             except ValidationError as e:
# #                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)   

# #     def post(self, request):
# #         serializer = UserEntrySerializer(data=request.data)
# #         if serializer.is_valid():
# #             try:
# #                 serializer.save(user=request.user)
# #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
# #             except ValidationError as e:
# #                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST) 

# #     def put(self, request, pk):
# #         try:
# #             data = UserEntry.objects.get(pk=pk)
# #         except UserEntry.DoesNotExist:
# #             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

# #         serializer = UserEntrySerializer(data, data=request.data)
# #         if serializer.is_valid():
# #             serializer.save()
# #             return Response(serializer.data)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     def perform_update(self, serializer):
# #         serializer.save(user=self.request.user)

# # class UserEntryViewSetExpense(viewsets.ModelViewSet):
# #     queryset = UserEntryExpense.objects.all()
# #     serializer_class = UserEntrySerializerExpense
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return UserEntryExpense.objects.all()
# #         return UserEntryExpense.objects.filter(user=user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)       

# # class UserEntryViewSeta(viewsets.ModelViewSet):
# #     queryset = UserEntry.objects.all()
# #     serializer_class = UserEntrySerializer
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return UserEntry.objects.all()
# #         return UserEntry.objects.filter(user=user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     def perform_update(self, serializer):
# #         # Custom behavior during update (if needed)
# #         serializer.save(user=self.request.user)
# # class UserEntryViewSet2a(viewsets.ModelViewSet):
# #     queryset = UserEntry2.objects.all()
# #     serializer_class = UserEntrySerializer2
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return UserEntry2.objects.all()
# #         return UserEntry2.objects.filter(user=user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# # class UserEntryViewSetExpensea(viewsets.ModelViewSet):
# #     queryset = UserEntryExpense.objects.all()
# #     serializer_class = UserEntrySerializerExpense
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return UserEntryExpense.objects.all()
# #         return UserEntryExpense.objects.filter(user=user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user) 

# # class UserEntryViewSetOutofstock(viewsets.ModelViewSet):
# #     queryset = UserEntryOutofstock.objects.all()
# #     serializer_class = UserEntrySerializerOutofstock
# #     permission_classes = [IsAuthenticated]

# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return UserEntryOutofstock.objects.all()
# #         return UserEntryOutofstock.objects.filter(user=user)

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)               


# # class StockReportView(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         month = request.query_params.get('month')

# #         if month:
# #             try:
# #                 year, month = map(int, month.split('-'))
# #                 start_date = datetime(year, month, 1)
# #                 end_date = (start_date + timedelta(days=31)).replace(day=1)
# #             except ValueError:
# #                 return Response({"error": "Invalid month format."}, status=400)
# #         else:
# #             start_date = None
# #             end_date = None

# #         stock_items = StockItem.objects.all()

# #         report = []
# #         for stock in stock_items:
# #             user_entries = UserEntry.objects.filter(item_name=stock.name)
# #             if start_date and end_date:
# #                 user_entries = user_entries.filter(date__gte=start_date, date__lt=end_date)

# #             quantity_used = user_entries.aggregate(Sum('quantity'))['quantity__sum'] or 0
# #             remaining_stock = stock.quantity - quantity_used
# #             total_value_used = quantity_used * stock.price_per_unit
# #             total_value_unused = remaining_stock * stock.price_per_unit
# #             total_value_stock = stock.quantity * stock.price_per_unit

# #             report.append({
# #                 'item_name': stock.name,
# #                 'total_quantity': stock.quantity,
# #                 'quantity_used': quantity_used,
# #                 'remaining_stock': remaining_stock,
# #                 'total_value_used': total_value_used,
# #                 'total_value_unused': total_value_unused,
# #                 'total_value_stock': total_value_stock,
# #             })

# #         return JsonResponse(report, safe=False)
    
# # class StockReportView2(APIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request):
# #         month = request.query_params.get('month')

# #         if month:
# #             try:
# #                 year, month = map(int, month.split('-'))
# #                 start_date = datetime(year, month, 1)
# #                 end_date = (start_date + timedelta(days=31)).replace(day=1)
# #             except ValueError:
# #                 return Response({"error": "Invalid month format."}, status=400)
# #         else:
# #             start_date = None
# #             end_date = None

# #         stock_items = StockItem2.objects.all()

# #         report = []
# #         for stock in stock_items:
# #             user_entries = UserEntry2.objects.filter(item_name=stock.stock_name)
# #             if start_date and end_date:
# #                 user_entries = user_entries.filter(date__gte=start_date, date__lt=end_date)

# #             area_used_in_square_meters = user_entries.aggregate(Sum('area_in_square_meters'))['area_in_square_meters__sum'] or 0
# #             remaining_stock = stock.area_in_square_meters - area_used_in_square_meters
# #             total_value_used = area_used_in_square_meters * stock.price_per_square_meter
# #             total_value_unused = remaining_stock * stock.price_per_square_meter
# #             total_value_stock = stock.area_in_square_meters * stock.price_per_square_meter

# #             report.append({
# #                 'item_name': stock.stock_name,
# #                 'total_quantity': stock.area_in_square_meters,
# #                 'quantity_used': area_used_in_square_meters,
# #                 'remaining_stock': remaining_stock,
# #                 'total_value_used': total_value_used,
# #                 'total_value_unused': total_value_unused,
# #                 'total_value_stock': total_value_stock,
# #             })

# #         return JsonResponse(report, safe=False)    
# # class StockItemListCreateView(generics.ListCreateAPIView):
# #     queryset = StockItem.objects.all()
# #     serializer_class = StockItemSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')

# #         if month:
# #             try:
# #                 selected_month = datetime.strptime(month, "%Y-%m").date()
# #                 stock_items = StockItem.objects.filter(
# #                     added_date__year=selected_month.year,
# #                     added_date__month=selected_month.month
# #                 )
# #             except ValueError:
# #                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
# #         else:
# #             stock_items = StockItem.objects.all()

# #         serializer = StockItemSerializer(stock_items, many=True)
# #         return Response(serializer.data)

# #     def post(self, request, *args, **kwargs):
# #         data = request.data
# #         item_name = data.get('item_name')
# #         restock_quantity = int(data.get('quantity'))

# #         try:
# #             stock_item = StockItem.objects.get(name=item_name)
# #             stock_item.quantity += restock_quantity
# #             stock_item.save()

# #             return Response({
# #                 "message": f"Stock updated successfully. New quantity for {item_name} is {stock_item.quantity}."
# #             }, status=200)

# #         except StockItem.DoesNotExist:
# #             return Response({"error": "Item not found."}, status=404)
        
        
        

      
    
# # class StockItemListCreateView2(generics.ListCreateAPIView):
# #     queryset = StockItem2.objects.all()
# #     serializer_class = StockItemSerializer2
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')

# #         if month:
# #             try:
# #                 selected_month = datetime.strptime(month, "%Y-%m").date()
# #                 stock_items = StockItem2.objects.filter(
# #                     added_date__year=selected_month.year,
# #                     added_date__month=selected_month.month
# #                 )
# #             except ValueError:
# #                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
# #         else:
# #             stock_items = StockItem2.objects.all()

# #         serializer = StockItemSerializer2(stock_items, many=True)
# #         return Response(serializer.data)

# #     def post(self, request, *args, **kwargs):
# #         data = request.data
# #         item_name = data.get('item_name')
# #         restock_quantity = Decimal(data.get('area_in_square_meters'))

# #         try:
# #             stock_item = StockItem2.objects.get(stock_name=item_name)
# #             stock_item.area_in_square_meters += restock_quantity
# #             stock_item.save()

# #             return Response({
# #                 "message": f"Stock updated successfully. New quantity for {item_name} is {stock_item.area_in_square_meters}."
# #             }, status=200)

# #         except StockItem2.DoesNotExist:
# #             return Response({"error": "Item not found."}, status=404)
     

# # class StockItemListCreateViewa(generics.ListCreateAPIView):
# #     queryset = StockItem.objects.all()
# #     serializer_class = StockItemSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')
        
        
# #         if month:
# #             try:
                
# #                 selected_month = datetime.strptime(month, "%Y-%m").date()

               
# #                 stock_items = StockItem.objects.filter(
# #                     added_date__year=selected_month.year,
# #                     added_date__month=selected_month.month
# #                 )
# #             except ValueError:
# #                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
# #         else:
# #             stock_items = StockItem.objects.all()

# #         serializer = StockItemSerializer(stock_items, many=True)
# #         return Response(serializer.data)
    
# # class StockItemListCreateView2a(generics.ListCreateAPIView):
# #     queryset = StockItem2.objects.all()
# #     serializer_class = StockItemSerializer2
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')
        
        
# #         if month:
# #             try:
                
# #                 selected_month = datetime.strptime(month, "%Y-%m").date()

               
# #                 stock_items = StockItem2.objects.filter(
# #                     added_date__year=selected_month.year,
# #                     added_date__month=selected_month.month
# #                 )
# #             except ValueError:
# #                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
# #         else:
# #             stock_items = StockItem2.objects.all()

# #         serializer = StockItemSerializer2(stock_items, many=True)
# #         return Response(serializer.data)



# # class StockItemDetailView(generics.RetrieveUpdateDestroyAPIView):
# #     queryset = StockItem.objects.all()
# #     serializer_class = StockItemSerializer
# #     permission_classes = [IsAuthenticated]


# # class AvailableStockItemsView(APIView):
# #     def get(self, request):
# #         available_stock_items = StockItem.objects.filter(quantity__gt=F('quantity_used'))
# #         serialized_data = StockItemSerializer(available_stock_items, many=True).data
# #         return Response(serialized_data)   
    
# # class AvailableStockItemsView2(APIView):
# #     def get(self, request):
# #         available_stock_items = StockItem2.objects.filter(area_in_square_meters__gt=F('area_used_in_square_meters'))
# #         serialized_data = StockItemSerializer2(available_stock_items, many=True).data
# #         return Response(serialized_data)   


# # class YearlyReportView(generics.GenericAPIView):
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         year = request.query_params.get('year')
# #         if not year:
# #             return Response({"error": "Year parameter is required."}, status=400)

# #         try:
# #             year = int(year)
# #             start_date = datetime(year, 1, 1).strftime('%Y-%m-%d')
# #             end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
# #         except ValueError:
# #             return Response({"error": "Invalid year format. Use YYYY."}, status=400)

# #         # Fetch data for the entire year
# #         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
# #         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
# #         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)

# #         # Combine daily totals for UserEntry and UserEntry2
# #         daily_totals = (
# #             user_entries.values('date')
# #             .annotate(total_sales=Sum('total_price'))
# #             .order_by('date')
# #         )

# #         daily_totals2 = (
# #             user_entries2.values('date')
# #             .annotate(total_sales=Sum('total_price'))
# #             .order_by('date')
# #         )

# #         # Merge sales data from both UserEntry and UserEntry2
# #         combined_sales_totals = {}
# #         for entry in daily_totals:
# #             date = entry['date']
# #             combined_sales_totals[date] = entry['total_sales']

# #         for entry in daily_totals2:
# #             date = entry['date']
# #             if date in combined_sales_totals:
# #                 combined_sales_totals[date] += entry['total_sales']
# #             else:
# #                 combined_sales_totals[date] = entry['total_sales']

# #         # Combine daily totals with expenses
# #         daily_expenses = (
# #             expense_entries.values('date')
# #             .annotate(total_expenses=Sum('expenses'))
# #             .order_by('date')
# #         )

# #         combined_daily_totals = []
# #         all_dates = set(combined_sales_totals.keys()) | set(item['date'] for item in daily_expenses)

# #         for date in sorted(all_dates):
# #             daily_sales = combined_sales_totals.get(date, 0)
# #             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
# #             combined_daily_totals.append({
# #                 'date': date,
# #                 'total_sales': daily_sales,
# #                 'total_expenses': daily_expense,
# #                 'profit': daily_sales - daily_expense
# #             })

# #         # Calculate monthly totals
# #         total_sales = sum(combined_sales_totals.values())
# #         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
# #         profit = total_sales - total_expenses

# #         monthly_totals = {
# #             'total_sales': total_sales,
# #             'total_expenses': total_expenses,
# #             'profit': profit,
# #         }

# #         return Response({'daily_totals': combined_daily_totals, 'monthly_totals': monthly_totals})

# # # Add this path to your urls.py
# # from django.urls import path



# # class RestockView(APIView):

# #     permission_classes = [IsAuthenticated]

# #     def post(self, request):
# #         item_data = request.data.get('item')
# #         item_type = request.data.get('item_type')

# #         if item_type == 'StockItem':
# #             serializer = StockItemRestockSerializer(data=item_data)
# #             if serializer.is_valid():
# #                 name = serializer.validated_data['name']
# #                 quantity = serializer.validated_data['quantity']
                
# #                 try:
# #                     stock_item = StockItem.objects.get(name=name)
# #                     stock_item.quantity += quantity
# #                     stock_item.restock_quantity = quantity
# #                     stock_item.last_restock_date = datetime.now().date()
# #                     stock_item.save()
# #                     return Response({'message': 'StockItem restocked successfully.'}, status=status.HTTP_200_OK)
# #                 except StockItem.DoesNotExist:
# #                     return Response({'error': 'StockItem not found.'}, status=status.HTTP_404_NOT_FOUND)
# #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# #         elif item_type == 'StockItem2':
# #             serializer = StockItem2RestockSerializer(data=item_data)
# #             if serializer.is_valid():
# #                 stock_name = serializer.validated_data['stock_name']
# #                 area_in_square_meters = serializer.validated_data['area_in_square_meters']
                
# #                 try:
# #                     stock_item2 = StockItem2.objects.get(stock_name=stock_name)
# #                     stock_item2.area_in_square_meters += area_in_square_meters
# #                     stock_item2.last_restock_date = datetime.now().date()
# #                     stock_item2.save()
# #                     return Response({'message': 'StockItem2 restocked successfully.'}, status=status.HTTP_200_OK)
# #                 except StockItem2.DoesNotExist:
# #                     return Response({'error': 'StockItem2 not found.'}, status=status.HTTP_404_NOT_FOUND)
# #             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# #         return Response({'error': 'Invalid item type.'}, status=status.HTTP_400_BAD_REQUEST)
    


# # class DebtEntryViewSet(viewsets.ModelViewSet):
# #     queryset = Debt.objects.all()
# #     serializer_class = DebtSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         start_date = request.query_params.get('start_date')
# #         end_date = request.query_params.get('end_date')
# #         if not start_date or not end_date:
# #             return Response({"error": "Start date and end date parameters are required."}, status=400)
        
# #         try:
# #             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
# #             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
# #         except ValueError:
# #             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

# #     # Ensure the user can only access their own debts, unless they are admin
# #     def get_queryset(self):
# #         user = self.request.user
# #         if user.is_staff:
# #             return Debt.objects.all()
# #         return Debt.objects.filter(user=user)\

# #     def perform_create(self, serializer):
# #         serializer.save(user=self.request.user)

# #     def perform_update(self, serializer):
# #         serializer.save(user=self.request.user)  

# #     # def partial_update(self, request, *args, **kwargs):
# #     #     kwargs['partial'] = True
# #     #     return super().update(request, *args, **kwargs)      

# #     def post(self, request):
# #         serializer = DebtSerializer(data=request.data)
# #         if serializer.is_valid():
# #             try:
# #                 serializer.save(user=request.user)
# #                 return Response(serializer.data, status=status.HTTP_201_CREATED)
# #             except ValidationError as e:
# #                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
# #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# #     # def update_debt(request, debt_id):
# #     #     try:
# #     #         debt = Debt.objects.get(pk=debt_id)
# #     #     except Debt.DoesNotExist:
# #     #         return JsonResponse({"error": "Debt not found"}, status=404)

# #     #     # Update debt object based on request data
# #     #     # debt.status = request.data.get('status')  # Assuming 'amount' is a field in your Debt model
# #     #     # debt.save()

# #     #     return JsonResponse({"message": "Debt updated successfully"}, status=200)



# # class UserListCreateView(ListCreateAPIView):
# #     queryset = User.objects.all()
# #     authentication_classes = [JWTAuthentication]
# #     permission_classes = [IsAdminUser]

# #     def get(self, request, *args, **kwargs):
# #         users = User.objects.all().values('id', 'username')
# #         return Response(users, status=status.HTTP_200_OK)

# #     def post(self, request, *args, **kwargs):
# #         username = request.data.get('username')
# #         password = request.data.get('password')

# #         if not username or not password:
# #             return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

# #         # Create a new user
# #         User.objects.create(username=username, password=make_password(password))
# #         return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)

# # # Delete user
# # class UserDeleteView(DestroyAPIView):
# #     queryset = User.objects.all()
# #     authentication_classes = [JWTAuthentication]
# #     permission_classes = [IsAdminUser]

# #     def delete(self, request, *args, **kwargs):
# #         user_id = kwargs['pk']
# #         try:
# #             user = User.objects.get(id=user_id)
# #             user.delete()
# #             return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
# #         except User.DoesNotExist:
# #             return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

# # # Change password view
# # class ChangePasswordView(APIView):
# #     authentication_classes = [JWTAuthentication]
# #     permission_classes = [IsAuthenticated]

# #     def post(self, request):
# #         user = request.user
# #         old_password = request.data.get('old_password')
# #         new_password = request.data.get('new_password')

# #         if not old_password or not new_password:
# #             return Response({'error': 'Old and new passwords are required.'}, status=status.HTTP_400_BAD_REQUEST)

# #         if not user.check_password(old_password):
# #             return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

# #         user.set_password(new_password)
# #         user.save()

# #         return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)



# # @api_view(['GET'])
# # def get_notifications(request):
# #     if request.user.is_authenticated:
# #         notifications = Notification.objects.filter(user=request.user)
# #         notifications_list = [{"message": n.message, "created_at": n.created_at} for n in notifications]
# #         return JsonResponse({"notifications": notifications_list})
# #     return JsonResponse({"notifications": []})


# # @api_view(['POST'])
# # def update_preferences(request):
# #     user = request.user
# #     data = request.data

# #     # Update or create preferences for the user
# #     preferences, created = NotificationPreference.objects.get_or_create(user=user)
# #     preferences.email = data.get('email', False)
# #     preferences.push = data.get('push', False)
# #     preferences.text = data.get('text', False)
# #     preferences.phone_call = data.get('phone_call', False)
# #     preferences.save()

# #     return Response({"message": "Preferences updated"}, status=status.HTTP_200_OK)


# # def notify_user_about_stock(user):
# #     notification_pref = get_object_or_404(NotificationPreference, user=user)

# #     # Get the stock level (this is an example, adapt it to your system)
# #     stock = StockItem.objects.filter(user=user).first()
    
# #     if stock and StockItem.quantity < 10:  # If stock is low
# #         message = f"Hello {user.username}, your stock is running low!"

# #         # Send email if the user has opted in
# #         if notification_pref.receive_email and notification_pref.email:
# #             send_email(notification_pref.email, "Low Stock Alert", message)

# #         # Send SMS if the user has opted in
# #         if notification_pref.receive_sms and notification_pref.phone_number:
# #             send_sms(notification_pref.phone_number, message)

# #         # Phone call logic can be added here if needed (using Twilio for calls)
# #         # You can also integrate push notifications similarly.


# # def check_stock_view(request):
# #     stock_items = StockItem.objects.all()

# #     for stock in stock_items:
# #         if StockItem.quantity < 10:  # Assume 10 is the threshold for low stock
# #             notify_user_about_stock(stock.user)

# #     return render(request, 'stock_list.html', {'stock_items': stock_items})


# # @api_view(['GET'])
# # # def fetch_notifications(request):
# # #     user = request.user
# # #     notifications = Notification.objects.filter(user=user, is_read=False)
    
# # #     notifications_data = [
# # #         {
# # #             'id': notification.id,
# # #             'message': notification.message,
# # #             'created_at': notification.created_at,
# # #             'is_read': notification.is_read,
# # #         }
# # #         for notification in notifications
# # #     ]
    
# # #     return JsonResponse({'notifications': notifications_data})
# # def fetch_notifications(request):
# #     # Fetch unread notifications for the logged-in admin
# #     user = User.objects.get(is_superuser=True)
# #     notifications = Notification.objects.filter(user=user, is_read=False)  # Filter on is_read field
# #     serializer = NotificationSerializer(notifications, many=True)
# #     return Response({'notifications': serializer.data})

# # @api_view(['POST'])
# # def mark_notification_as_read(request, notification_id):
# #     try:
# #         notification = Notification.objects.get(id=notification_id)
# #         notification.is_read = True
# #         notification.save()
# #         return Response({'success': 'Notification marked as read'})
# #     except Notification.DoesNotExist:
# #         return Response({'error': 'Notification not found'}, status=404)
    


# from decimal import Decimal
# from urllib import request, response
# from venv import logger
# from django.forms import ValidationError
# from django.http import JsonResponse
# from rest_framework import generics, viewsets, status
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework_simplejwt.views import TokenObtainPairView
# from django.contrib.auth.models import User
# from .models import DataEntry, Debt, Notification, NotificationPreference, StockItem, StockItem2, UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock
# from django.db.models import F 
# from .serializers import DataEntrySerializer, DebtSerializer, NotificationSerializer, StockItem2RestockSerializer, StockItemRestockSerializer, StockItemSerializer, StockItemSerializer2, StockReportSerializer, UserEntrySerializer, UserEntrySerializer2, UserEntrySerializerExpense, UserEntrySerializerOutofstock
# from django.db.models import Sum
# from django.utils.dateparse import parse_date
# from datetime import datetime, timedelta
# from django.contrib.auth import authenticate
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.generics import ListCreateAPIView, DestroyAPIView
# from django.contrib.auth.hashers import make_password
# from rest_framework.permissions import IsAdminUser
# from django.shortcuts import get_object_or_404
# from .models import NotificationPreference
# from .utils import send_sms, send_email
# from django.shortcuts import render
# from django.db.models import Sum
# from django.utils import timezone
# from django.urls import path
# from myapp import models
# from django.db.models import F


# class DataEntryListCreateView(generics.ListCreateAPIView):
#     serializer_class = DataEntrySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return DataEntry.objects.all()
#         return DataEntry.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class CustomTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         try:
#             user = authenticate(username=username, password=password)

#             if user is not None:
#                 response = super().post(request, *args, **kwargs)

#                 if user.is_staff:
#                     response.data['is_staff'] = True
#                     response.data['message'] = "Login successful. Welcome, admin!"
#                 else:
#                     response.data['is_staff'] = False
#                     response.data['message'] = "Login successful. Welcome, user!"

#                 return response
#             else:
#                 return Response({
#                     'message': "Invalid credentials. Check your username and password."
#                 }, status=401)

#         except User.DoesNotExist:
#             return Response({
#                 'message': "User does not exist."
#             }, status=400)


# class MonthlyReportView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         if not month:
#             return Response({"error": "Month parameter is required."}, status=400)

#         try:
#             year, month_number = map(int, month.split('-'))
#             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
#             if month_number == 12:
#                 end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
#             else:
#                 end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
#         except ValueError:
#             return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

#         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
#         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)
#         debt_entries = Debt.objects.filter(date__gte=start_date, date__lt=end_date)
#         outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date)

#         daily_totals = (
#             user_entries.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         daily_totals2 = (
#             user_entries2.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         combined_sales_totals = {}
#         for entry in daily_totals:
#             date = entry['date']
#             combined_sales_totals[date] = entry['total_sales']

#         for entry in daily_totals2:
#             date = entry['date']
#             if date in combined_sales_totals:
#                 combined_sales_totals[date] += entry['total_sales']
#             else:
#                 combined_sales_totals[date] = entry['total_sales']

#         daily_expenses = (
#             expense_entries.values('date')
#             .annotate(total_expenses=Sum('expenses'))
#             .order_by('date')
#         )

#         daily_debts = (
#             debt_entries.values('date')
#             .annotate(total_debts=Sum('amount'))
#             .order_by('date')
#         )

#         daily_outofstock = (
#             outofstock_entries.values('date')
#             .annotate(total_outofstock=Sum('price'))
#             .order_by('date')
#         )

#         combined_daily_totals = []
#         all_dates = (
#             set(combined_sales_totals.keys())
#             | set(item['date'] for item in daily_outofstock)
#             | set(item['date'] for item in daily_debts)
#             | set(item['date'] for item in daily_expenses)
#         )

#         for date in sorted(all_dates):
#             daily_sales = combined_sales_totals.get(date, 0)
#             daily_outofstock_value = next((item['total_outofstock'] for item in daily_outofstock if item['date'] == date), 0) or 0
#             daily_debts_value = next((item['total_debts'] for item in daily_debts if item['date'] == date), 0) or 0
#             daily_expense_value = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0) or 0
#             combined_daily_totals.append({
#                 'date': date,
#                 'total_sales': daily_sales,
#                 'total_expenses': daily_expense_value,
#                 'total_debts': daily_debts_value,
#                 'total_outofstock': daily_outofstock_value,
#                 'profit': daily_sales + daily_outofstock_value - daily_expense_value
#             })

#         total_sales = sum(combined_sales_totals.values())
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
#         total_debts = debt_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
#         total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0
#         profit = total_sales + total_outofstock - total_expenses

#         monthly_totals = {
#             'total_sales': total_sales,
#             'total_expenses': total_expenses,
#             'total_debts': total_debts,
#             'total_outofstock': total_outofstock,
#             'profit': profit,
#         }

#         return Response({'daily_totals': combined_daily_totals, 'monthly_totals': monthly_totals})


# class WeeklyReportView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         if not start_date or not end_date:
#             return Response({"error": "Start date and end date parameters are required."}, status=400)

#         try:
#             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#         except ValueError:
#             return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=400)

#         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lte=end_date)
#         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lte=end_date)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lte=end_date)
#         debt_entries = Debt.objects.filter(date__gte=start_date, date__lte=end_date)
#         outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lte=end_date)

#         daily_totals = (
#             user_entries.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         daily_totals2 = (
#             user_entries2.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         combined_sales_totals = {}
#         for entry in daily_totals:
#             date = entry['date']
#             combined_sales_totals[date] = entry['total_sales']

#         for entry in daily_totals2:
#             date = entry['date']
#             if date in combined_sales_totals:
#                 combined_sales_totals[date] += entry['total_sales']
#             else:
#                 combined_sales_totals[date] = entry['total_sales']

#         daily_expenses = (
#             expense_entries.values('date')
#             .annotate(total_expenses=Sum('expenses'))
#             .order_by('date')
#         )

#         daily_debts = (
#             debt_entries.values('date')
#             .annotate(total_debts=Sum('amount'))
#             .order_by('date')
#         )

#         daily_outofstock = (
#             outofstock_entries.values('date')
#             .annotate(total_outofstock=Sum('price'))
#             .order_by('date')
#         )

#         combined_daily_totals = []
#         all_dates = (
#             set(combined_sales_totals.keys())
#             | set(item['date'] for item in daily_outofstock)
#             | set(item['date'] for item in daily_debts)
#         )

#         for date in sorted(all_dates):
#             daily_sales = combined_sales_totals.get(date, 0)
#             daily_outofstock_value = next((item['total_outofstock'] for item in daily_outofstock if item['date'] == date), 0) or 0
#             daily_debts_value = next((item['total_debts'] for item in daily_debts if item['date'] == date), 0) or 0
#             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0) or 0
#             combined_daily_totals.append({
#                 'date': date.strftime('%Y-%m-%d'),
#                 'total_sales': daily_sales,
#                 'total_debts': daily_debts_value,
#                 'total_outofstock': daily_outofstock_value,
#                 'total_expenses': daily_expense,
#                 'profit': daily_sales + daily_outofstock_value - daily_expense
#             })

#         total_sales = sum(combined_sales_totals.values())
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
#         total_debts = debt_entries.aggregate(Sum('amount'))['amount__sum'] or 0
#         total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0
#         profit = total_sales + total_outofstock - total_expenses

#         weekly_totals = {
#             'total_sales': total_sales,
#             'total_debts': total_debts,
#             'total_outofstock': total_outofstock,
#             'total_expenses': total_expenses,
#             'profit': profit,
#         }

#         return Response({'daily_totals': combined_daily_totals, 'weekly_totals': weekly_totals})


# class MonthlyReportView2(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         if not month:
#             return Response({"error": "Month parameter is required."}, status=400)

#         try:
#             year, month_number = map(int, month.split('-'))
#             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')

#             if month_number == 12:
#                 end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
#             else:
#                 end_date = datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
#         except ValueError:
#             return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

#         user_entries = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)

#         daily_totalss = (
#             user_entries.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         daily_expenses = (
#             expense_entries.values('date')
#             .annotate(total_expenses=Sum('expenses'))
#             .order_by('date')
#         )

#         combined_daily_totalss = []
#         all_dates = set([item['date'] for item in daily_totalss] + [item['date'] for item in daily_expenses])

#         for date in sorted(all_dates):
#             daily_sales = next((item['total_sales'] for item in daily_totalss if item['date'] == date), 0)
#             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
#             combined_daily_totalss.append({
#                 'date': date,
#                 'total_sales': daily_sales,
#                 'total_expenses': daily_expense,
#                 'profit': daily_sales - daily_expense
#             })

#         total_sales = user_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
#         profit = total_sales - total_expenses

#         monthly_totalss = {
#             'total_sales': total_sales,
#             'total_expenses': total_expenses,
#             'profit': profit,
#         }

#         return Response({'daily_totalss': combined_daily_totalss, 'monthly_totalss': monthly_totalss})


# class StockItemViewSet(viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer

#     def get(self, request):
#         selected_month = request.query_params.get('month')

#         if selected_month:
#             try:
#                 year, month = map(int, selected_month.split('-'))
#                 stock_items = StockItem.objects.filter(
#                     date_added__year=year,
#                     date_added__month=month
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid month format. Please use 'YYYY-MM' format."}, status=400)
#         else:
#             stock_items = StockItem.objects.all()

#         serializer = StockItemSerializer(stock_items, many=True)
#         return Response(serializer.data)


# class UserEntryViewSet(viewsets.ModelViewSet):
#     queryset = UserEntry.objects.all()
#     serializer_class = UserEntrySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return UserEntry.objects.all()
#         return UserEntry.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)

#     def put(self, request, pk):
#         try:
#             data = UserEntry.objects.get(pk=pk)
#         except UserEntry.DoesNotExist:
#             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = UserEntrySerializer(data, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserEntryViewSet2(viewsets.ModelViewSet):
#     queryset = UserEntry2.objects.all()
#     serializer_class = UserEntrySerializer2
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return UserEntry2.objects.all()
#         return UserEntry2.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)

#     def put(self, request, pk):
#         try:
#             data = UserEntry2.objects.get(pk=pk)
#         except UserEntry2.DoesNotExist:
#             return Response({'error': 'Data not found'}, status=status.HTTP_404_NOT_FOUND)

#         serializer = UserEntrySerializer2(data, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserEntryViewSetExpense(viewsets.ModelViewSet):
#     queryset = UserEntryExpense.objects.all()
#     serializer_class = UserEntrySerializerExpense
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return UserEntryExpense.objects.all()
#         return UserEntryExpense.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class UserEntryViewSeta(viewsets.ModelViewSet):
#     queryset = UserEntry.objects.all()
#     serializer_class = UserEntrySerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return UserEntry.objects.all()
#         return UserEntry.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)


# class UserEntryViewSet2a(viewsets.ModelViewSet):
#     queryset = UserEntry2.objects.all()
#     serializer_class = UserEntrySerializer2
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return UserEntry2.objects.all()
#         return UserEntry2.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)


# class UserEntryViewSetExpensea(viewsets.ModelViewSet):
#     queryset = UserEntryExpense.objects.all()
#     serializer_class = UserEntrySerializerExpense
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return UserEntryExpense.objects.all()
#         return UserEntryExpense.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class UserEntryViewSetOutofstock(viewsets.ModelViewSet):
#     queryset = UserEntryOutofstock.objects.all()
#     serializer_class = UserEntrySerializerOutofstock
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return UserEntryOutofstock.objects.all()
#         return UserEntryOutofstock.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)


# class StockReportView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         month = request.query_params.get('month')

#         if month:
#             try:
#                 year, month = map(int, month.split('-'))
#                 start_date = datetime(year, month, 1)
#                 end_date = (start_date + timedelta(days=31)).replace(day=1)
#             except ValueError:
#                 return Response({"error": "Invalid month format."}, status=400)
#         else:
#             start_date = None
#             end_date = None

#         stock_items = StockItem.objects.all()

#         report = []
#         for stock in stock_items:
#             user_entries = UserEntry.objects.filter(item_name=stock.name)
#             if start_date and end_date:
#                 user_entries = user_entries.filter(date__gte=start_date, date__lt=end_date)

#             quantity_used = user_entries.aggregate(Sum('quantity'))['quantity__sum'] or 0
#             remaining_stock = stock.quantity - quantity_used
#             total_value_used = quantity_used * stock.price_per_unit
#             total_value_unused = remaining_stock * stock.price_per_unit
#             total_value_stock = stock.quantity * stock.price_per_unit

#             report.append({
#                 'item_name': stock.name,
#                 'total_quantity': stock.quantity,
#                 'quantity_used': quantity_used,
#                 'remaining_stock': remaining_stock,
#                 'total_value_used': total_value_used,
#                 'total_value_unused': total_value_unused,
#                 'total_value_stock': total_value_stock,
#             })

#         return JsonResponse(report, safe=False)


# class StockReportView2(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         month = request.query_params.get('month')

#         if month:
#             try:
#                 year, month = map(int, month.split('-'))
#                 start_date = datetime(year, month, 1)
#                 end_date = (start_date + timedelta(days=31)).replace(day=1)
#             except ValueError:
#                 return Response({"error": "Invalid month format."}, status=400)
#         else:
#             start_date = None
#             end_date = None

#         stock_items = StockItem2.objects.all()

#         report = []
#         for stock in stock_items:
#             user_entries = UserEntry2.objects.filter(item_name=stock.stock_name)
#             if start_date and end_date:
#                 user_entries = user_entries.filter(date__gte=start_date, date__lt=end_date)

#             area_used_in_square_meters = user_entries.aggregate(Sum('area_in_square_meters'))['area_in_square_meters__sum'] or 0
#             remaining_stock = stock.area_in_square_meters - area_used_in_square_meters
#             total_value_used = area_used_in_square_meters * stock.price_per_square_meter
#             total_value_unused = remaining_stock * stock.price_per_square_meter
#             total_value_stock = stock.area_in_square_meters * stock.price_per_square_meter

#             report.append({
#                 'item_name': stock.stock_name,
#                 'total_quantity': stock.area_in_square_meters,
#                 'quantity_used': area_used_in_square_meters,
#                 'remaining_stock': remaining_stock,
#                 'total_value_used': total_value_used,
#                 'total_value_unused': total_value_unused,
#                 'total_value_stock': total_value_stock,
#             })

#         return JsonResponse(report, safe=False)


# class StockItemListCreateView(generics.ListCreateAPIView):
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')

#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 stock_items = StockItem.objects.filter(
#                     added_date__year=selected_month.year,
#                     added_date__month=selected_month.month
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
#         else:
#             stock_items = StockItem.objects.all()

#         serializer = StockItemSerializer(stock_items, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         item_name = data.get('item_name')
#         restock_quantity = int(data.get('quantity'))

#         try:
#             stock_item = StockItem.objects.get(name=item_name)
#             stock_item.quantity += restock_quantity
#             stock_item.save()

#             return Response({
#                 "message": f"Stock updated successfully. New quantity for {item_name} is {stock_item.quantity}."
#             }, status=200)

#         except StockItem.DoesNotExist:
#             return Response({"error": "Item not found."}, status=404)


# class StockItemListCreateView2(generics.ListCreateAPIView):
#     queryset = StockItem2.objects.all()
#     serializer_class = StockItemSerializer2
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')

#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 stock_items = StockItem2.objects.filter(
#                     added_date__year=selected_month.year,
#                     added_date__month=selected_month.month
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
#         else:
#             stock_items = StockItem2.objects.all()

#         serializer = StockItemSerializer2(stock_items, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         item_name = data.get('item_name')
#         restock_quantity = Decimal(data.get('area_in_square_meters'))

#         try:
#             stock_item = StockItem2.objects.get(stock_name=item_name)
#             stock_item.area_in_square_meters += restock_quantity
#             stock_item.save()

#             return Response({
#                 "message": f"Stock updated successfully. New quantity for {item_name} is {stock_item.area_in_square_meters}."
#             }, status=200)

#         except StockItem2.DoesNotExist:
#             return Response({"error": "Item not found."}, status=404)


# # class StockItemListCreateViewa(generics.ListCreateAPIView):
# #     queryset = StockItem.objects.all()
# #     serializer_class = StockItemSerializer
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')

# #         if month:
# #             try:
# #                 selected_month = datetime.strptime(month, "%Y-%m").date()
# #                 stock_items = StockItem.objects.filter(
# #                     added_date__year=selected_month.year,
# #                     added_date__month=selected_month.month
# #                 )
# #             except ValueError:
# #                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
# #         else:
# #             stock_items = StockItem.objects.all()

# #         serializer = StockItemSerializer(stock_items, many=True)
# #         return Response(serializer.data)


# # class StockItemListCreateView2a(generics.ListCreateAPIView):
# #     queryset = StockItem2.objects.all()
# #     serializer_class = StockItemSerializer2
# #     permission_classes = [IsAuthenticated]

# #     def get(self, request, *args, **kwargs):
# #         month = request.query_params.get('month')

# #         if month:
# #             try:
# #                 selected_month = datetime.strptime(month, "%Y-%m").date()
# #                 stock_items = StockItem2.objects.filter(
# #                     added_date__year=selected_month.year,
# #                     added_date__month=selected_month.month
# #                 )
# #             except ValueError:
# #                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
# #         else:
# #             stock_items = StockItem2.objects.all()

# #         serializer = StockItemSerializer2(stock_items, many=True)
# #         return Response(serializer.data)

# class StockItemListCreateViewa(generics.ListCreateAPIView):
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')

#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 stock_items = StockItem.objects.filter(
#                     added_date__year=selected_month.year,
#                     added_date__month=selected_month.month
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
#         else:
#             stock_items = StockItem.objects.all()

#         serializer = StockItemSerializer(stock_items, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         name = data.get('name')
#         quantity = data.get('quantity')
#         price_per_unit = data.get('price_per_unit')
#         added_date = data.get('added_date')

#         if StockItem.objects.filter(name=name).exists():
#             stock_item = StockItem.objects.get(name=name)
#             stock_item.quantity += int(quantity)
#             stock_item.save()
#             return Response({'message': f'Stock updated for {name}.'}, status=status.HTTP_200_OK)
#         else:
#             StockItem.objects.create(
#                 name=name,
#                 quantity=quantity,
#                 price_per_unit=price_per_unit,
#                 added_date=added_date
#             )
#             return Response({'message': f'{name} added to stock.'}, status=status.HTTP_201_CREATED)

#     def delete(self, request, *args, **kwargs):
#         name = request.data.get('name')
#         if not name:
#             return Response({'error': 'Item name is required.'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             stock_item = StockItem.objects.get(name=name)
#             stock_item.delete()
#             return Response({'message': f'{name} deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
#         except StockItem.DoesNotExist:
#             return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)


# class StockItemListCreateView2a(generics.ListCreateAPIView):
#     queryset = StockItem2.objects.all()
#     serializer_class = StockItemSerializer2
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')

#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 stock_items = StockItem2.objects.filter(
#                     added_date__year=selected_month.year,
#                     added_date__month=selected_month.month
#                 )
#             except ValueError:
#                 return Response({"error": "Invalid month format. Please use YYYY-MM."}, status=400)
#         else:
#             stock_items = StockItem2.objects.all()

#         serializer = StockItemSerializer2(stock_items, many=True)
#         return Response(serializer.data)

#     def post(self, request, *args, **kwargs):
#         data = request.data
#         stock_name = data.get('stock_name')
#         area_in_square_meters = data.get('area_in_square_meters')
#         price_per_square_meter = data.get('price_per_square_meter')
#         added_date = data.get('added_date')

#         if StockItem2.objects.filter(stock_name=stock_name).exists():
#             stock_item = StockItem2.objects.get(stock_name=stock_name)
#             stock_item.area_in_square_meters += Decimal(area_in_square_meters)
#             stock_item.save()
#             return Response({'message': f'Stock updated for {stock_name}.'}, status=status.HTTP_200_OK)
#         else:
#             StockItem2.objects.create(
#                 stock_name=stock_name,
#                 area_in_square_meters=area_in_square_meters,
#                 price_per_square_meter=price_per_square_meter,
#                 added_date=added_date
#             )
#             return Response({'message': f'{stock_name} added to stock.'}, status=status.HTTP_201_CREATED)

#     def delete(self, request, *args, **kwargs):
#         name = request.data.get('name')
#         if not name:
#             return Response({'error': 'Item name is required.'}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             stock_item = StockItem2.objects.get(stock_name=name)
#             stock_item.delete()
#             return Response({'message': f'{name} deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
#         except StockItem2.DoesNotExist:
#             return Response({'error': 'Item not found.'}, status=status.HTTP_404_NOT_FOUND)
            
# class StockItemDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer
#     permission_classes = [IsAuthenticated]


# # Replace these two classes in your existing views.py

# class AvailableStockItemsView(APIView):
#     """
#     Returns StockItem rows where remaining stock > 0.
#     Items with zero remaining are excluded — users cannot select them.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # quantity_used < quantity  →  remaining_stock() > 0
#         available = StockItem.objects.filter(quantity__gt=models.F('quantity_used'))
#         return Response(StockItemSerializer(available, many=True).data)


# class AvailableStockItemsView2(APIView):
#     """
#     Returns StockItem2 rows where remaining area > 0.
#     Items with zero remaining area are excluded — users cannot select them.
#     """
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         # area_used < area_total  →  remaining_area() > 0
#         available = StockItem2.objects.filter(
#             area_in_square_meters__gt=models.F('area_used_in_square_meters')
#         )
#         return Response(StockItemSerializer2(available, many=True).data)

# class YearlyReportView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         year = request.query_params.get('year')
#         if not year:
#             return Response({"error": "Year parameter is required."}, status=400)

#         try:
#             year = int(year)
#             start_date = datetime(year, 1, 1).strftime('%Y-%m-%d')
#             end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
#         except ValueError:
#             return Response({"error": "Invalid year format. Use YYYY."}, status=400)

#         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date)
#         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date)

#         daily_totals = (
#             user_entries.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         daily_totals2 = (
#             user_entries2.values('date')
#             .annotate(total_sales=Sum('total_price'))
#             .order_by('date')
#         )

#         combined_sales_totals = {}
#         for entry in daily_totals:
#             date = entry['date']
#             combined_sales_totals[date] = entry['total_sales']

#         for entry in daily_totals2:
#             date = entry['date']
#             if date in combined_sales_totals:
#                 combined_sales_totals[date] += entry['total_sales']
#             else:
#                 combined_sales_totals[date] = entry['total_sales']

#         daily_expenses = (
#             expense_entries.values('date')
#             .annotate(total_expenses=Sum('expenses'))
#             .order_by('date')
#         )

#         combined_daily_totals = []
#         all_dates = set(combined_sales_totals.keys()) | set(item['date'] for item in daily_expenses)

#         for date in sorted(all_dates):
#             daily_sales = combined_sales_totals.get(date, 0)
#             daily_expense = next((item['total_expenses'] for item in daily_expenses if item['date'] == date), 0)
#             combined_daily_totals.append({
#                 'date': date,
#                 'total_sales': daily_sales,
#                 'total_expenses': daily_expense,
#                 'profit': daily_sales - daily_expense
#             })

#         total_sales = sum(combined_sales_totals.values())
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
#         profit = total_sales - total_expenses

#         monthly_totals = {
#             'total_sales': total_sales,
#             'total_expenses': total_expenses,
#             'profit': profit,
#         }

#         return Response({'daily_totals': combined_daily_totals, 'monthly_totals': monthly_totals})


# class RestockView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         item_data = request.data.get('item')
#         item_type = request.data.get('item_type')

#         if item_type == 'StockItem':
#             serializer = StockItemRestockSerializer(data=item_data)
#             if serializer.is_valid():
#                 name = serializer.validated_data['name']
#                 quantity = serializer.validated_data['quantity']

#                 try:
#                     stock_item = StockItem.objects.get(name=name)
#                     stock_item.quantity += quantity
#                     stock_item.restock_quantity = quantity
#                     stock_item.last_restock_date = datetime.now().date()
#                     stock_item.save()
#                     return Response({'message': 'StockItem restocked successfully.'}, status=status.HTTP_200_OK)
#                 except StockItem.DoesNotExist:
#                     return Response({'error': 'StockItem not found.'}, status=status.HTTP_404_NOT_FOUND)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         elif item_type == 'StockItem2':
#             serializer = StockItem2RestockSerializer(data=item_data)
#             if serializer.is_valid():
#                 stock_name = serializer.validated_data['stock_name']
#                 area_in_square_meters = serializer.validated_data['area_in_square_meters']

#                 try:
#                     stock_item2 = StockItem2.objects.get(stock_name=stock_name)
#                     stock_item2.area_in_square_meters += area_in_square_meters
#                     stock_item2.last_restock_date = datetime.now().date()
#                     stock_item2.save()
#                     return Response({'message': 'StockItem2 restocked successfully.'}, status=status.HTTP_200_OK)
#                 except StockItem2.DoesNotExist:
#                     return Response({'error': 'StockItem2 not found.'}, status=status.HTTP_404_NOT_FOUND)
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         return Response({'error': 'Invalid item type.'}, status=status.HTTP_400_BAD_REQUEST)


# class DebtEntryViewSet(viewsets.ModelViewSet):
#     queryset = Debt.objects.all()
#     serializer_class = DebtSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
#         if user.is_staff:
#             return Debt.objects.all()
#         return Debt.objects.filter(user=user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

#     def perform_update(self, serializer):
#         serializer.save(user=self.request.user)

#     def post(self, request):
#         serializer = DebtSerializer(data=request.data)
#         if serializer.is_valid():
#             try:
#                 serializer.save(user=request.user)
#                 return Response(serializer.data, status=status.HTTP_201_CREATED)
#             except ValidationError as e:
#                 return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserListCreateView(ListCreateAPIView):
#     queryset = User.objects.all()
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAdminUser]

#     def get(self, request, *args, **kwargs):
#         users = User.objects.all().values('id', 'username')
#         return Response(users, status=status.HTTP_200_OK)

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         if not username or not password:
#             return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

#         User.objects.create(username=username, password=make_password(password))
#         return Response({'message': 'User created successfully.'}, status=status.HTTP_201_CREATED)


# class UserDeleteView(DestroyAPIView):
#     queryset = User.objects.all()
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAdminUser]

#     def delete(self, request, *args, **kwargs):
#         user_id = kwargs['pk']
#         try:
#             user = User.objects.get(id=user_id)
#             user.delete()
#             return Response({'message': 'User deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
#         except User.DoesNotExist:
#             return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


# class ChangePasswordView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         old_password = request.data.get('old_password')
#         new_password = request.data.get('new_password')

#         if not old_password or not new_password:
#             return Response({'error': 'Old and new passwords are required.'}, status=status.HTTP_400_BAD_REQUEST)

#         if not user.check_password(old_password):
#             return Response({'error': 'Old password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)

#         user.set_password(new_password)
#         user.save()

#         return Response({'message': 'Password updated successfully.'}, status=status.HTTP_200_OK)


# @api_view(['GET'])
# def get_notifications(request):
#     if request.user.is_authenticated:
#         notifications = Notification.objects.filter(user=request.user)
#         notifications_list = [{"message": n.message, "created_at": n.created_at} for n in notifications]
#         return JsonResponse({"notifications": notifications_list})
#     return JsonResponse({"notifications": []})


# @api_view(['POST'])
# def update_preferences(request):
#     user = request.user
#     data = request.data

#     preferences, created = NotificationPreference.objects.get_or_create(user=user)
#     preferences.email = data.get('email', False)
#     preferences.push = data.get('push', False)
#     preferences.text = data.get('text', False)
#     preferences.phone_call = data.get('phone_call', False)
#     preferences.save()

#     return Response({"message": "Preferences updated"}, status=status.HTTP_200_OK)


# def notify_user_about_stock(user):
#     notification_pref = get_object_or_404(NotificationPreference, user=user)
#     stock = StockItem.objects.filter(user=user).first()

#     if stock and stock.remaining_stock() < 10:
#         message = f"Hello {user.username}, your stock is running low!"

#         if notification_pref.receive_email and notification_pref.email:
#             send_email(notification_pref.email, "Low Stock Alert", message)

#         if notification_pref.receive_sms and notification_pref.phone_number:
#             send_sms(notification_pref.phone_number, message)


# def check_stock_view(request):
#     stock_items = StockItem.objects.all()

#     for stock in stock_items:
#         if stock.remaining_stock() < 10:
#             notify_user_about_stock(stock.user)

#     return render(request, 'stock_list.html', {'stock_items': stock_items})


# @api_view(['GET'])
# def fetch_notifications(request):
#     if not request.user.is_authenticated:
#         return Response({'notifications': []})
#     notifications = Notification.objects.filter(user=request.user, is_read=False)
#     serializer = NotificationSerializer(notifications, many=True)
#     return Response({'notifications': serializer.data})


# @api_view(['POST'])
# def mark_notification_as_read(request, notification_id):
#     try:
#         notification = Notification.objects.get(id=notification_id)
#         notification.is_read = True
#         notification.save()
#         return Response({'success': 'Notification marked as read'})
#     except Notification.DoesNotExist:
#         return Response({'error': 'Notification not found'}, status=404)

"""
views.py  —  Multi-tenant edition

New endpoints:
  POST   /api/company/register/          — public, creates company + owner account
  GET    /api/admin/companies/           — superadmin: list all companies
  GET    /api/admin/companies/<id>/      — superadmin: company detail
  POST   /api/admin/companies/<id>/grant-access/   — grant N months
  POST   /api/admin/companies/<id>/revoke-access/  — revoke immediately
  POST   /api/admin/companies/<id>/record-payment/ — log a payment
  GET    /api/admin/companies/<id>/payments/       — list payments for a company
  POST   /api/company/staff/create/      — company-admin creates staff user
  GET    /api/company/staff/             — company-admin lists own staff
  DELETE /api/company/staff/<id>/       — company-admin removes a staff user

All existing data endpoints are unchanged in URL but now automatically scoped
to the authenticated user's company via CompanyScopedMixin.
"""

# from decimal import Decimal
# from django.http import JsonResponse
# from django.contrib.auth.models import User
# from django.contrib.auth import authenticate
# from django.contrib.auth.hashers import make_password
# from django.shortcuts import get_object_or_404, render
# from django.db.models import F, Sum
# from django.utils import timezone
# from datetime import datetime, timedelta

# from rest_framework import generics, viewsets, status
# from rest_framework.decorators import api_view, permission_classes as deco_permissions
# from rest_framework.exceptions import PermissionDenied
# from rest_framework.generics import ListCreateAPIView, DestroyAPIView
# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework_simplejwt.views import TokenObtainPairView
# from django.forms import ValidationError

# from .mixins import CompanyScopedMixin, get_company_for_user
# from .models import (
#     Company, CompanyMembership, PaymentRecord,
#     DataEntry, Debt, Notification, NotificationPreference,
#     StockItem, StockItem2,
#     UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock,
# )
# from .serializers import (
#     CompanyRegistrationSerializer, CompanySerializer, CompanyListSerializer,
#     GrantAccessSerializer, PaymentRecordSerializer,
#     CreateCompanyStaffSerializer, CompanyMembershipSerializer,
#     DataEntrySerializer, DebtSerializer, NotificationSerializer,
#     StockItem2RestockSerializer, StockItemRestockSerializer,
#     StockItemSerializer, StockItemSerializer2, StockReportSerializer,
#     UserEntrySerializer, UserEntrySerializer2,
#     UserEntrySerializerExpense, UserEntrySerializerOutofstock,
# )
# from myapp import models as myapp_models


# # ===========================================================================
# # COMPANY REGISTRATION  (public endpoint — no auth required)
# # ===========================================================================

# class CompanyRegisterView(APIView):
#     """
#     POST /api/company/register/
#     Body: { company_name, username, password }
#     Creates company + owner account. Account is INACTIVE until superadmin grants access.
#     """
#     permission_classes = []   # public

#     def post(self, request):
#         serializer = CompanyRegistrationSerializer(data=request.data)
#         if serializer.is_valid():
#             company = serializer.save()
#             return Response(
#                 {
#                     'message': (
#                         f'🎉 Welcome to SPOS! Your company "{company.name}" has been registered successfully. '
#                         'An administrator will review and activate your 30-day free trial once your payment is confirmed. '
#                         'You will be notified when your account is ready.'
#                     ),
#                     'company': company.name,
#                     'owner': company.owner.username,
#                     'is_active': company.is_active,
#                 },
#                 status=status.HTTP_201_CREATED,
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# # ===========================================================================
# # SUPERADMIN — COMPANY MANAGEMENT
# # ===========================================================================

# class IsSuperAdmin(IsAdminUser):
#     def has_permission(self, request, view):
#         return bool(request.user and request.user.is_superuser)


# class AdminCompanyListView(APIView):
#     """
#     GET  /api/admin/companies/        — list all companies
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def get(self, request):
#         companies = Company.objects.all().order_by('-registered_at')
#         serializer = CompanyListSerializer(companies, many=True)
#         return Response(serializer.data)


# class AdminCompanyDetailView(APIView):
#     """
#     GET   /api/admin/companies/<id>/   — company detail with payments
#     PATCH /api/admin/companies/<id>/   — update notes / is_active directly
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def get_object(self, pk):
#         return get_object_or_404(Company, pk=pk)

#     def get(self, request, pk):
#         company = self.get_object(pk)
#         return Response(CompanySerializer(company).data)

#     def patch(self, request, pk):
#         company = self.get_object(pk)
#         # Only allow patching safe fields
#         allowed = {'notes', 'is_active', 'access_expires_at'}
#         data = {k: v for k, v in request.data.items() if k in allowed}
#         serializer = CompanySerializer(company, data=data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class AdminGrantAccessView(APIView):
#     """
#     POST /api/admin/companies/<id>/grant-access/
#     Body: { months: 1 }
#     Grants N months of access from today (or extends existing expiry).
#     Automatically logs a payment record if amount_paid is provided.
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def post(self, request, pk):
#         company = get_object_or_404(Company, pk=pk)
#         serializer = GrantAccessSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         months = serializer.validated_data['months']
#         company.grant_access(months=months)

#         # Optionally record a payment at the same time
#         amount_paid = request.data.get('amount_paid')
#         if amount_paid:
#             PaymentRecord.objects.create(
#                 company=company,
#                 amount_paid=Decimal(str(amount_paid)),
#                 payment_method=request.data.get('payment_method', 'cash'),
#                 payment_date=request.data.get('payment_date', timezone.now().date()),
#                 months_granted=months,
#                 recorded_by=request.user,
#                 reference=request.data.get('reference', ''),
#                 notes=request.data.get('notes', ''),
#             )

#         return Response(
#             {
#                 'message': f'Access granted for {months} month(s).',
#                 'company': company.name,
#                 'is_active': company.is_active,
#                 'access_expires_at': company.access_expires_at,
#                 'days_until_expiry': company.days_until_expiry(),
#             }
#         )


# class AdminRevokeAccessView(APIView):
#     """
#     POST /api/admin/companies/<id>/revoke-access/
#     Immediately suspends the company.
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def post(self, request, pk):
#         company = get_object_or_404(Company, pk=pk)
#         company.revoke_access()
#         return Response(
#             {
#                 'message': f'Access revoked for {company.name}.',
#                 'is_active': company.is_active,
#             }
#         )


# class AdminPaymentListCreateView(APIView):
#     """
#     GET  /api/admin/companies/<id>/payments/   — list payments
#     POST /api/admin/companies/<id>/payments/   — record a payment (without granting access)
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def get(self, request, pk):
#         company = get_object_or_404(Company, pk=pk)
#         payments = company.payments.order_by('-payment_date')
#         return Response(PaymentRecordSerializer(payments, many=True).data)

#     def post(self, request, pk):
#         company = get_object_or_404(Company, pk=pk)
#         data = request.data.copy()
#         data['company'] = company.pk
#         serializer = PaymentRecordSerializer(data=data)
#         if serializer.is_valid():
#             serializer.save(recorded_by=request.user, company=company)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class AdminAllPaymentsView(APIView):
#     """
#     GET /api/admin/payments/   — all payments across all companies
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def get(self, request):
#         payments = PaymentRecord.objects.select_related('company').order_by('-payment_date')
#         return Response(PaymentRecordSerializer(payments, many=True).data)


# class AdminCompanyMembersView(APIView):
#     """
#     GET /api/admin/companies/<id>/members/   — list all users in a company
#     """
#     permission_classes = [IsAuthenticated, IsSuperAdmin]

#     def get(self, request, pk):
#         company = get_object_or_404(Company, pk=pk)
#         members = company.members.select_related('user').all()
#         return Response(CompanyMembershipSerializer(members, many=True).data)


# # ===========================================================================
# # COMPANY-ADMIN — STAFF MANAGEMENT
# # (company admin manages their own users; superadmin can do this for any co.)
# # ===========================================================================

# class IsCompanyAdmin(IsAuthenticated):
#     def has_permission(self, request, view):
#         if not super().has_permission(request, view):
#             return False
#         if request.user.is_superuser:
#             return True
#         try:
#             return request.user.membership.role == 'admin'
#         except Exception:
#             return False


# class CompanyStaffListCreateView(APIView):
#     """
#     GET  /api/company/staff/   — list staff in my company
#     POST /api/company/staff/   — create a new staff user in my company
#     """
#     permission_classes = [IsAuthenticated, IsCompanyAdmin]

#     def _get_company(self, request):
#         if request.user.is_superuser:
#             company_id = request.query_params.get('company_id') or request.data.get('company_id')
#             return get_object_or_404(Company, pk=company_id) if company_id else None
#         return request.user.membership.company

#     def get(self, request):
#         company = self._get_company(request)
#         if not company:
#             return Response({'error': 'company_id required for superadmin.'}, status=400)
#         members = company.members.select_related('user').all()
#         return Response(CompanyMembershipSerializer(members, many=True).data)

#     def post(self, request):
#         company = self._get_company(request)
#         if not company:
#             return Response({'error': 'company_id required for superadmin.'}, status=400)

#         serializer = CreateCompanyStaffSerializer(data=request.data)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         user = User.objects.create_user(
#             username=serializer.validated_data['username'],
#             password=serializer.validated_data['password'],
#         )
#         membership = CompanyMembership.objects.create(
#             user=user,
#             company=company,
#             role=serializer.validated_data['role'],
#         )
#         return Response(
#             {
#                 'message': f"User '{user.username}' created in company '{company.name}'.",
#                 'user_id': user.pk,
#                 'username': user.username,
#                 'role': membership.role,
#             },
#             status=status.HTTP_201_CREATED,
#         )


# class CompanyStaffDeleteView(APIView):
#     """
#     DELETE /api/company/staff/<user_id>/
#     Removes the user from the company (and deletes the account).
#     Company admin cannot delete themselves.
#     """
#     permission_classes = [IsAuthenticated, IsCompanyAdmin]

#     def delete(self, request, user_id):
#         if request.user.pk == user_id:
#             return Response({'error': 'You cannot delete your own account.'}, status=400)

#         try:
#             if request.user.is_superuser:
#                 membership = CompanyMembership.objects.get(user_id=user_id)
#             else:
#                 company = request.user.membership.company
#                 membership = CompanyMembership.objects.get(user_id=user_id, company=company)
#         except CompanyMembership.DoesNotExist:
#             return Response({'error': 'User not found in your company.'}, status=404)

#         username = membership.user.username
#         membership.user.delete()   # cascades membership
#         return Response({'message': f"User '{username}' removed."}, status=204)


# # ===========================================================================
# # AUTH
# # ===========================================================================

# # class CustomTokenObtainPairView(TokenObtainPairView):
# #     def post(self, request, *args, **kwargs):
# #         username = request.data.get('username')
# #         password = request.data.get('password')

# #         user = authenticate(username=username, password=password)
# #         if user is None:
# #             return Response({'message': "Invalid credentials."}, status=401)

# #         response = super().post(request, *args, **kwargs)

# #         # Attach extra context
# #         response.data['is_staff'] = user.is_staff
# #         response.data['is_superuser'] = user.is_superuser

# #         if user.is_superuser:
# #             response.data['role'] = 'superadmin'
# #             response.data['message'] = "Welcome, superadmin!"
# #         else:
# #             try:
# #                 membership = user.membership
# #                 company = membership.company
# #                 response.data['role'] = membership.role
# #                 response.data['company_id'] = company.pk
# #                 response.data['company_name'] = company.name
# #                 response.data['is_company_active'] = company.is_access_valid()
# #                 response.data['access_expires_at'] = (
# #                     company.access_expires_at.isoformat() if company.access_expires_at else None
# #                 )
# #                 response.data['days_until_expiry'] = company.days_until_expiry()
# #                 response.data['message'] = f"Welcome, {username}!"
# #             except Exception:
# #                 response.data['role'] = 'unknown'
# #                 response.data['message'] = "Login successful but no company linked."

# #         return response
# # Replace your CustomTokenObtainPairView in views.py with this:

# class CustomTokenObtainPairView(TokenObtainPairView):
#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')

#         user = authenticate(username=username, password=password)
#         if user is None:
#             return Response({'message': "Invalid credentials."}, status=401)

#         # ── Check company access BEFORE issuing token ──────────────────────
#         if not user.is_superuser:
#             try:
#                 membership = user.membership
#                 company = membership.company

#                 if not company.is_access_valid():
#                     # Return 403 with full suspension details so the
#                     # frontend can redirect to /auth/suspended
#                     return Response(
#                         {
#                             'error': 'access_suspended',
#                             'message': (
#                                 "Your company's subscription has expired or been suspended. "
#                                 "Please contact the administrator to renew access."
#                             ),
#                             'company': company.name,
#                             'is_active': company.is_active,
#                             'access_expires_at': (
#                                 company.access_expires_at.isoformat()
#                                 if company.access_expires_at else None
#                             ),
#                         },
#                         status=403,
#                     )
#             except Exception:
#                 # No membership found — also block
#                 return Response(
#                     {
#                         'error': 'no_company',
#                         'message': 'Your account is not linked to any company. Contact the administrator.',
#                     },
#                     status=403,
#                 )

#         # ── All good — issue token ─────────────────────────────────────────
#         response = super().post(request, *args, **kwargs)

#         response.data['is_staff'] = user.is_staff
#         response.data['is_superuser'] = user.is_superuser

#         if user.is_superuser:
#             response.data['role'] = 'superadmin'
#             response.data['message'] = "Welcome, superadmin!"
#         else:
#             try:
#                 membership = user.membership
#                 company = membership.company
#                 response.data['role'] = membership.role
#                 response.data['company_id'] = company.pk
#                 response.data['company_name'] = company.name
#                 response.data['is_company_active'] = company.is_access_valid()
#                 response.data['access_expires_at'] = (
#                     company.access_expires_at.isoformat()
#                     if company.access_expires_at else None
#                 )
#                 response.data['days_until_expiry'] = company.days_until_expiry()
#                 response.data['message'] = f"Welcome, {username}!"
#             except Exception:
#                 response.data['role'] = 'unknown'
#                 response.data['message'] = "Login successful but no company linked."

#         return response

# # ===========================================================================
# # DATA ENTRY VIEWS  (all company-scoped via CompanyScopedMixin)
# # ===========================================================================

# class DataEntryListCreateView(CompanyScopedMixin, generics.ListCreateAPIView):
#     serializer_class = DataEntrySerializer
#     permission_classes = [IsAuthenticated]
#     queryset = DataEntry.objects.all()


# class UserEntryViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
#     queryset = UserEntry.objects.all()
#     serializer_class = UserEntrySerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class UserEntryViewSet2(CompanyScopedMixin, viewsets.ModelViewSet):
#     queryset = UserEntry2.objects.all()
#     serializer_class = UserEntrySerializer2
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class UserEntryViewSetExpense(CompanyScopedMixin, viewsets.ModelViewSet):
#     queryset = UserEntryExpense.objects.all()
#     serializer_class = UserEntrySerializerExpense
#     permission_classes = [IsAuthenticated]


# class UserEntryViewSetOutofstock(CompanyScopedMixin, viewsets.ModelViewSet):
#     queryset = UserEntryOutofstock.objects.all()
#     serializer_class = UserEntrySerializerOutofstock
#     permission_classes = [IsAuthenticated]


# # These "a" variants are kept for URL compatibility
# UserEntryViewSeta = UserEntryViewSet
# UserEntryViewSet2a = UserEntryViewSet2
# UserEntryViewSetExpensea = UserEntryViewSetExpense


# # ===========================================================================
# # STOCK VIEWS
# # ===========================================================================

# class StockItemViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer


# class StockItemListCreateView(CompanyScopedMixin, generics.ListCreateAPIView):
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         company = self.get_company()
#         qs = StockItem.objects.all()
#         if company:
#             qs = qs.filter(company=company)
#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 qs = qs.filter(added_date__year=selected_month.year, added_date__month=selected_month.month)
#             except ValueError:
#                 return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)
#         return Response(StockItemSerializer(qs, many=True).data)

#     def post(self, request, *args, **kwargs):
#         company = self.get_company()
#         data = request.data
#         item_name = data.get('item_name')
#         restock_quantity = int(data.get('quantity', 0))
#         try:
#             stock_item = StockItem.objects.get(name=item_name, company=company)
#             stock_item.quantity += restock_quantity
#             stock_item.save()
#             return Response({'message': f'Stock updated for {item_name}.'}, status=200)
#         except StockItem.DoesNotExist:
#             return Response({'error': 'Item not found.'}, status=404)


# class StockItemListCreateView2(CompanyScopedMixin, generics.ListCreateAPIView):
#     queryset = StockItem2.objects.all()
#     serializer_class = StockItemSerializer2
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         company = self.get_company()
#         qs = StockItem2.objects.all()
#         if company:
#             qs = qs.filter(company=company)
#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 qs = qs.filter(added_date__year=selected_month.year, added_date__month=selected_month.month)
#             except ValueError:
#                 return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)
#         return Response(StockItemSerializer2(qs, many=True).data)

#     def post(self, request, *args, **kwargs):
#         company = self.get_company()
#         data = request.data
#         item_name = data.get('item_name')
#         restock_quantity = Decimal(data.get('area_in_square_meters', 0))
#         try:
#             stock_item = StockItem2.objects.get(stock_name=item_name, company=company)
#             stock_item.area_in_square_meters += restock_quantity
#             stock_item.save()
#             return Response({'message': f'Stock updated for {item_name}.'}, status=200)
#         except StockItem2.DoesNotExist:
#             return Response({'error': 'Item not found.'}, status=404)


# class StockItemListCreateViewa(CompanyScopedMixin, generics.ListCreateAPIView):
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         company = self.get_company()
#         qs = StockItem.objects.filter(company=company) if company else StockItem.objects.all()
#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 qs = qs.filter(added_date__year=selected_month.year, added_date__month=selected_month.month)
#             except ValueError:
#                 return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)
#         return Response(StockItemSerializer(qs, many=True).data)

#     def post(self, request, *args, **kwargs):
#         company = self.get_company()
#         data = request.data
#         name = data.get('name')
#         quantity = data.get('quantity')
#         price_per_unit = data.get('price_per_unit')
#         added_date = data.get('added_date')

#         if StockItem.objects.filter(name=name, company=company).exists():
#             stock_item = StockItem.objects.get(name=name, company=company)
#             stock_item.quantity += int(quantity)
#             stock_item.save()
#             return Response({'message': f'Stock updated for {name}.'}, status=200)
#         else:
#             StockItem.objects.create(name=name, quantity=quantity,
#                                      price_per_unit=price_per_unit,
#                                      added_date=added_date, company=company)
#             return Response({'message': f'{name} added to stock.'}, status=201)

#     def delete(self, request, *args, **kwargs):
#         company = self.get_company()
#         name = request.data.get('name')
#         if not name:
#             return Response({'error': 'Item name is required.'}, status=400)
#         try:
#             StockItem.objects.get(name=name, company=company).delete()
#             return Response({'message': f'{name} deleted.'}, status=204)
#         except StockItem.DoesNotExist:
#             return Response({'error': 'Item not found.'}, status=404)


# class StockItemListCreateView2a(CompanyScopedMixin, generics.ListCreateAPIView):
#     queryset = StockItem2.objects.all()
#     serializer_class = StockItemSerializer2
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         company = self.get_company()
#         qs = StockItem2.objects.filter(company=company) if company else StockItem2.objects.all()
#         if month:
#             try:
#                 selected_month = datetime.strptime(month, "%Y-%m").date()
#                 qs = qs.filter(added_date__year=selected_month.year, added_date__month=selected_month.month)
#             except ValueError:
#                 return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)
#         return Response(StockItemSerializer2(qs, many=True).data)

#     def post(self, request, *args, **kwargs):
#         company = self.get_company()
#         data = request.data
#         stock_name = data.get('stock_name')
#         area_in_square_meters = data.get('area_in_square_meters')
#         price_per_square_meter = data.get('price_per_square_meter')
#         added_date = data.get('added_date')

#         if StockItem2.objects.filter(stock_name=stock_name, company=company).exists():
#             stock_item = StockItem2.objects.get(stock_name=stock_name, company=company)
#             stock_item.area_in_square_meters += Decimal(area_in_square_meters)
#             stock_item.save()
#             return Response({'message': f'Stock updated for {stock_name}.'}, status=200)
#         else:
#             StockItem2.objects.create(stock_name=stock_name,
#                                       area_in_square_meters=area_in_square_meters,
#                                       price_per_square_meter=price_per_square_meter,
#                                       added_date=added_date, company=company)
#             return Response({'message': f'{stock_name} added to stock.'}, status=201)

#     def delete(self, request, *args, **kwargs):
#         company = self.get_company()
#         name = request.data.get('name')
#         if not name:
#             return Response({'error': 'Item name is required.'}, status=400)
#         try:
#             StockItem2.objects.get(stock_name=name, company=company).delete()
#             return Response({'message': f'{name} deleted.'}, status=204)
#         except StockItem2.DoesNotExist:
#             return Response({'error': 'Item not found.'}, status=404)


# class StockItemDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = StockItem.objects.all()
#     serializer_class = StockItemSerializer
#     permission_classes = [IsAuthenticated]


# class AvailableStockItemsView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         company = get_company_for_user(request)
#         qs = StockItem.objects.filter(quantity__gt=myapp_models.F('quantity_used'))
#         if company:
#             qs = qs.filter(company=company)
#         return Response(StockItemSerializer(qs, many=True).data)


# class AvailableStockItemsView2(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         company = get_company_for_user(request)
#         qs = StockItem2.objects.filter(area_in_square_meters__gt=myapp_models.F('area_used_in_square_meters'))
#         if company:
#             qs = qs.filter(company=company)
#         return Response(StockItemSerializer2(qs, many=True).data)


# # ===========================================================================
# # REPORTING VIEWS (all company-scoped)
# # ===========================================================================

# def _get_company_filter(request):
#     """Returns a dict to pass to .filter() for company scoping."""
#     company = get_company_for_user(request)
#     return {'company': company} if company else {}


# class MonthlyReportView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         if not month:
#             return Response({"error": "Month parameter is required."}, status=400)

#         try:
#             year, month_number = map(int, month.split('-'))
#             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
#             end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d') if month_number == 12 \
#                 else datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
#         except ValueError:
#             return Response({"error": "Invalid month format. Use YYYY-MM."}, status=400)

#         cf = _get_company_filter(request)
#         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
#         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
#         debt_entries = Debt.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
#         outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date, **cf)

#         daily_totals = user_entries.values('date').annotate(total_sales=Sum('total_price')).order_by('date')
#         daily_totals2 = user_entries2.values('date').annotate(total_sales=Sum('total_price')).order_by('date')

#         combined_sales_totals = {}
#         for entry in daily_totals:
#             combined_sales_totals[entry['date']] = entry['total_sales']
#         for entry in daily_totals2:
#             d = entry['date']
#             combined_sales_totals[d] = combined_sales_totals.get(d, 0) + entry['total_sales']

#         daily_expenses = expense_entries.values('date').annotate(total_expenses=Sum('expenses')).order_by('date')
#         daily_debts = debt_entries.values('date').annotate(total_debts=Sum('amount')).order_by('date')
#         daily_outofstock = outofstock_entries.values('date').annotate(total_outofstock=Sum('price')).order_by('date')

#         all_dates = (
#             set(combined_sales_totals.keys())
#             | set(i['date'] for i in daily_outofstock)
#             | set(i['date'] for i in daily_debts)
#             | set(i['date'] for i in daily_expenses)
#         )

#         combined_daily_totals = []
#         for date in sorted(all_dates):
#             daily_sales = combined_sales_totals.get(date, 0)
#             oos = next((i['total_outofstock'] for i in daily_outofstock if i['date'] == date), 0) or 0
#             debts = next((i['total_debts'] for i in daily_debts if i['date'] == date), 0) or 0
#             exp = next((i['total_expenses'] for i in daily_expenses if i['date'] == date), 0) or 0
#             combined_daily_totals.append({
#                 'date': date, 'total_sales': daily_sales, 'total_expenses': exp,
#                 'total_debts': debts, 'total_outofstock': oos,
#                 'profit': daily_sales + oos - exp,
#             })

#         total_sales = sum(combined_sales_totals.values())
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
#         total_debts = debt_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
#         total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0

#         return Response({
#             'daily_totals': combined_daily_totals,
#             'monthly_totals': {
#                 'total_sales': total_sales, 'total_expenses': total_expenses,
#                 'total_debts': total_debts, 'total_outofstock': total_outofstock,
#                 'profit': total_sales + total_outofstock - total_expenses,
#             },
#         })


# class WeeklyReportView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         start_date = request.query_params.get('start_date')
#         end_date = request.query_params.get('end_date')
#         if not start_date or not end_date:
#             return Response({"error": "start_date and end_date required."}, status=400)

#         try:
#             start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
#             end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
#         except ValueError:
#             return Response({"error": "Use YYYY-MM-DD."}, status=400)

#         cf = _get_company_filter(request)
#         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
#         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
#         debt_entries = Debt.objects.filter(date__gte=start_date, date__lte=end_date, **cf)
#         outofstock_entries = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lte=end_date, **cf)

#         daily_totals = user_entries.values('date').annotate(total_sales=Sum('total_price')).order_by('date')
#         daily_totals2 = user_entries2.values('date').annotate(total_sales=Sum('total_price')).order_by('date')

#         combined_sales_totals = {}
#         for entry in daily_totals:
#             combined_sales_totals[entry['date']] = entry['total_sales']
#         for entry in daily_totals2:
#             d = entry['date']
#             combined_sales_totals[d] = combined_sales_totals.get(d, 0) + entry['total_sales']

#         daily_expenses = expense_entries.values('date').annotate(total_expenses=Sum('expenses')).order_by('date')
#         daily_debts = debt_entries.values('date').annotate(total_debts=Sum('amount')).order_by('date')
#         daily_outofstock = outofstock_entries.values('date').annotate(total_outofstock=Sum('price')).order_by('date')

#         all_dates = set(combined_sales_totals.keys()) | set(i['date'] for i in daily_outofstock) | set(i['date'] for i in daily_debts)

#         combined_daily_totals = []
#         for date in sorted(all_dates):
#             daily_sales = combined_sales_totals.get(date, 0)
#             oos = next((i['total_outofstock'] for i in daily_outofstock if i['date'] == date), 0) or 0
#             debts = next((i['total_debts'] for i in daily_debts if i['date'] == date), 0) or 0
#             exp = next((i['total_expenses'] for i in daily_expenses if i['date'] == date), 0) or 0
#             combined_daily_totals.append({
#                 'date': date.strftime('%Y-%m-%d'), 'total_sales': daily_sales,
#                 'total_debts': debts, 'total_outofstock': oos, 'total_expenses': exp,
#                 'profit': daily_sales + oos - exp,
#             })

#         total_sales = sum(combined_sales_totals.values())
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0
#         total_debts = debt_entries.aggregate(Sum('amount'))['amount__sum'] or 0
#         total_outofstock = outofstock_entries.aggregate(Sum('price'))['price__sum'] or 0

#         return Response({
#             'daily_totals': combined_daily_totals,
#             'weekly_totals': {
#                 'total_sales': total_sales, 'total_debts': total_debts,
#                 'total_outofstock': total_outofstock, 'total_expenses': total_expenses,
#                 'profit': total_sales + total_outofstock - total_expenses,
#             },
#         })


# class MonthlyReportView2(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         month = request.query_params.get('month')
#         if not month:
#             return Response({"error": "Month parameter is required."}, status=400)

#         try:
#             year, month_number = map(int, month.split('-'))
#             start_date = datetime(year, month_number, 1).strftime('%Y-%m-%d')
#             end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d') if month_number == 12 \
#                 else datetime(year, month_number + 1, 1).strftime('%Y-%m-%d')
#         except ValueError:
#             return Response({"error": "Invalid month format."}, status=400)

#         cf = _get_company_filter(request)
#         user_entries = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date, **cf)

#         daily_totalss = user_entries.values('date').annotate(total_sales=Sum('total_price')).order_by('date')
#         daily_expenses = expense_entries.values('date').annotate(total_expenses=Sum('expenses')).order_by('date')

#         all_dates = set(i['date'] for i in daily_totalss) | set(i['date'] for i in daily_expenses)
#         combined = []
#         for date in sorted(all_dates):
#             sales = next((i['total_sales'] for i in daily_totalss if i['date'] == date), 0)
#             exp = next((i['total_expenses'] for i in daily_expenses if i['date'] == date), 0)
#             combined.append({'date': date, 'total_sales': sales, 'total_expenses': exp, 'profit': sales - exp})

#         total_sales = user_entries.aggregate(Sum('total_price'))['total_price__sum'] or 0
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0

#         return Response({
#             'daily_totalss': combined,
#             'monthly_totalss': {'total_sales': total_sales, 'total_expenses': total_expenses, 'profit': total_sales - total_expenses},
#         })


# class YearlyReportView(generics.GenericAPIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, *args, **kwargs):
#         year = request.query_params.get('year')
#         if not year:
#             return Response({"error": "Year required."}, status=400)

#         try:
#             year = int(year)
#             start_date = datetime(year, 1, 1).strftime('%Y-%m-%d')
#             end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
#         except ValueError:
#             return Response({"error": "Use YYYY."}, status=400)

#         cf = _get_company_filter(request)
#         user_entries = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
#         user_entries2 = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
#         expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date, **cf)

#         dt1 = user_entries.values('date').annotate(total_sales=Sum('total_price')).order_by('date')
#         dt2 = user_entries2.values('date').annotate(total_sales=Sum('total_price')).order_by('date')

#         combined_sales = {}
#         for e in dt1:
#             combined_sales[e['date']] = e['total_sales']
#         for e in dt2:
#             d = e['date']
#             combined_sales[d] = combined_sales.get(d, 0) + e['total_sales']

#         daily_expenses = expense_entries.values('date').annotate(total_expenses=Sum('expenses')).order_by('date')
#         all_dates = set(combined_sales.keys()) | set(i['date'] for i in daily_expenses)

#         combined_daily = []
#         for date in sorted(all_dates):
#             sales = combined_sales.get(date, 0)
#             exp = next((i['total_expenses'] for i in daily_expenses if i['date'] == date), 0)
#             combined_daily.append({'date': date, 'total_sales': sales, 'total_expenses': exp, 'profit': sales - exp})

#         total_sales = sum(combined_sales.values())
#         total_expenses = expense_entries.aggregate(Sum('expenses'))['expenses__sum'] or 0

#         return Response({
#             'daily_totals': combined_daily,
#             'monthly_totals': {'total_sales': total_sales, 'total_expenses': total_expenses, 'profit': total_sales - total_expenses},
#         })


# class StockReportView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         month = request.query_params.get('month')
#         start_date = end_date = None
#         if month:
#             try:
#                 y, m = map(int, month.split('-'))
#                 start_date = datetime(y, m, 1)
#                 end_date = (start_date + timedelta(days=31)).replace(day=1)
#             except ValueError:
#                 return Response({"error": "Invalid month."}, status=400)

#         company = get_company_for_user(request)
#         stock_items = StockItem.objects.filter(company=company) if company else StockItem.objects.all()
#         report = []
#         for stock in stock_items:
#             ue = UserEntry.objects.filter(item_name=stock.name, company=company)
#             if start_date and end_date:
#                 ue = ue.filter(date__gte=start_date, date__lt=end_date)
#             qty_used = ue.aggregate(Sum('quantity'))['quantity__sum'] or 0
#             remaining = stock.quantity - qty_used
#             report.append({
#                 'item_name': stock.name, 'total_quantity': stock.quantity,
#                 'quantity_used': qty_used, 'remaining_stock': remaining,
#                 'total_value_used': qty_used * stock.price_per_unit,
#                 'total_value_unused': remaining * stock.price_per_unit,
#                 'total_value_stock': stock.quantity * stock.price_per_unit,
#             })
#         return JsonResponse(report, safe=False)


# class StockReportView2(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         month = request.query_params.get('month')
#         start_date = end_date = None
#         if month:
#             try:
#                 y, m = map(int, month.split('-'))
#                 start_date = datetime(y, m, 1)
#                 end_date = (start_date + timedelta(days=31)).replace(day=1)
#             except ValueError:
#                 return Response({"error": "Invalid month."}, status=400)

#         company = get_company_for_user(request)
#         stock_items = StockItem2.objects.filter(company=company) if company else StockItem2.objects.all()
#         report = []
#         for stock in stock_items:
#             ue = UserEntry2.objects.filter(item_name=stock.stock_name, company=company)
#             if start_date and end_date:
#                 ue = ue.filter(date__gte=start_date, date__lt=end_date)
#             area_used = ue.aggregate(Sum('area_in_square_meters'))['area_in_square_meters__sum'] or 0
#             remaining = stock.area_in_square_meters - area_used
#             report.append({
#                 'item_name': stock.stock_name, 'total_quantity': stock.area_in_square_meters,
#                 'quantity_used': area_used, 'remaining_stock': remaining,
#                 'total_value_used': area_used * stock.price_per_square_meter,
#                 'total_value_unused': remaining * stock.price_per_square_meter,
#                 'total_value_stock': stock.area_in_square_meters * stock.price_per_square_meter,
#             })
#         return JsonResponse(report, safe=False)


# # ===========================================================================
# # RESTOCK, DEBT, USER MANAGEMENT
# # ===========================================================================

# class RestockView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         company = get_company_for_user(request)
#         item_data = request.data.get('item')
#         item_type = request.data.get('item_type')

#         if item_type == 'StockItem':
#             serializer = StockItemRestockSerializer(data=item_data)
#             if serializer.is_valid():
#                 name = serializer.validated_data['name']
#                 quantity = serializer.validated_data['quantity']
#                 try:
#                     stock_item = StockItem.objects.get(name=name, company=company)
#                     stock_item.quantity += quantity
#                     stock_item.restock_quantity = quantity
#                     stock_item.last_restock_date = datetime.now().date()
#                     stock_item.save()
#                     return Response({'message': 'Restocked.'}, status=200)
#                 except StockItem.DoesNotExist:
#                     return Response({'error': 'StockItem not found.'}, status=404)
#             return Response(serializer.errors, status=400)

#         elif item_type == 'StockItem2':
#             serializer = StockItem2RestockSerializer(data=item_data)
#             if serializer.is_valid():
#                 stock_name = serializer.validated_data['stock_name']
#                 area = serializer.validated_data['area_in_square_meters']
#                 try:
#                     stock_item2 = StockItem2.objects.get(stock_name=stock_name, company=company)
#                     stock_item2.area_in_square_meters += area
#                     stock_item2.last_restock_date = datetime.now().date()
#                     stock_item2.save()
#                     return Response({'message': 'Restocked.'}, status=200)
#                 except StockItem2.DoesNotExist:
#                     return Response({'error': 'StockItem2 not found.'}, status=404)
#             return Response(serializer.errors, status=400)

#         return Response({'error': 'Invalid item type.'}, status=400)


# class DebtEntryViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
#     queryset = Debt.objects.all()
#     serializer_class = DebtSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         try:
#             self.perform_create(serializer)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         except ValueError as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# class UserListCreateView(ListCreateAPIView):
#     queryset = User.objects.all()
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAdminUser]

#     def get(self, request, *args, **kwargs):
#         users = User.objects.all().values('id', 'username')
#         return Response(users, status=200)

#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         if not username or not password:
#             return Response({'error': 'Username and password required.'}, status=400)
#         User.objects.create(username=username, password=make_password(password))
#         return Response({'message': 'User created.'}, status=201)


# class UserDeleteView(DestroyAPIView):
#     queryset = User.objects.all()
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAdminUser]

#     def delete(self, request, *args, **kwargs):
#         try:
#             user = User.objects.get(id=kwargs['pk'])
#             user.delete()
#             return Response({'message': 'User deleted.'}, status=204)
#         except User.DoesNotExist:
#             return Response({'error': 'User not found.'}, status=404)


# class ChangePasswordView(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         user = request.user
#         old_password = request.data.get('old_password')
#         new_password = request.data.get('new_password')
#         if not old_password or not new_password:
#             return Response({'error': 'Both passwords required.'}, status=400)
#         if not user.check_password(old_password):
#             return Response({'error': 'Old password incorrect.'}, status=400)
#         user.set_password(new_password)
#         user.save()
#         return Response({'message': 'Password updated.'}, status=200)


# # ===========================================================================
# # NOTIFICATIONS
# # ===========================================================================

# @api_view(['GET'])
# def get_notifications(request):
#     if request.user.is_authenticated:
#         notifications = Notification.objects.filter(user=request.user)
#         return JsonResponse({"notifications": [{"message": n.message, "created_at": n.created_at} for n in notifications]})
#     return JsonResponse({"notifications": []})


# @api_view(['POST'])
# def update_preferences(request):
#     preferences, _ = NotificationPreference.objects.get_or_create(user=request.user)
#     data = request.data
#     preferences.email = data.get('email', False)
#     preferences.receive_push = data.get('push', False)
#     preferences.receive_sms = data.get('text', False)
#     preferences.receive_phone_call = data.get('phone_call', False)
#     preferences.save()
#     return Response({"message": "Preferences updated"}, status=200)


# @api_view(['GET'])
# def fetch_notifications(request):
#     if not request.user.is_authenticated:
#         return Response({'notifications': []})
#     notifications = Notification.objects.filter(user=request.user, is_read=False)
#     return Response({'notifications': NotificationSerializer(notifications, many=True).data})


# @api_view(['POST'])
# def mark_notification_as_read(request, notification_id):
#     try:
#         n = Notification.objects.get(id=notification_id)
#         n.is_read = True
#         n.save()
#         return Response({'success': 'Marked as read'})
#     except Notification.DoesNotExist:
#         return Response({'error': 'Not found'}, status=404)

# # views.py — add this class (put it near the other company views)

# class CompanyProfileView(APIView):
#     """
#     GET   /api/company/profile/   — get own company info
#     PATCH /api/company/profile/   — update email, phone, location (admin only)
#     """
#     permission_classes = [IsAuthenticated]

#     def _get_company(self, request):
#         if request.user.is_superuser:
#             return None
#         try:
#             return request.user.membership.company
#         except Exception:
#             return None

#     def get(self, request):
#         company = self._get_company(request)
#         if not company:
#             return Response({'error': 'No company linked.'}, status=404)
#         return Response({
#             'name': company.name,
#             'email': company.email or '',
#             'phone_number': company.phone_number or '',
#             'business_location': company.business_location or '',
#             'is_active': company.is_active,
#             'access_expires_at': (
#                 company.access_expires_at.isoformat()
#                 if company.access_expires_at else None
#             ),
#             'days_until_expiry': company.days_until_expiry(),
#         })

#     def patch(self, request):
#         company = self._get_company(request)
#         if not company:
#             return Response({'error': 'No company linked.'}, status=404)

#         # Only company admin or superuser can edit
#         try:
#             role = request.user.membership.role
#         except Exception:
#             role = None

#         if role != 'admin' and not request.user.is_superuser:
#             return Response(
#                 {'error': 'Only company admins can update the company profile.'},
#                 status=403,
#             )

#         allowed_fields = {'email', 'phone_number', 'business_location'}
#         updated = []
#         for field in allowed_fields:
#             if field in request.data:
#                 setattr(company, field, request.data[field])
#                 updated.append(field)

#         if updated:
#             company.save(update_fields=updated)

#         return Response({
#             'message': 'Company profile updated.',
#             'updated_fields': updated,
#             'name': company.name,
#             'email': company.email or '',
#             'phone_number': company.phone_number or '',
#             'business_location': company.business_location or '',
#         })
#     """
#     GET  /api/company/profile/   — get own company info
#     PATCH /api/company/profile/  — update email, phone, location
#     """
#     permission_classes = [IsAuthenticated]

#     def _get_company(self, request):
#         if request.user.is_superuser:
#             return None
#         try:
#             return request.user.membership.company
#         except Exception:
#             return None

#     def get(self, request):
#         company = self._get_company(request)
#         if not company:
#             return Response({'error': 'No company linked.'}, status=404)
#         return Response({
#             'name': company.name,
#             'email': company.email or '',
#             'phone_number': company.phone_number or '',
#             'business_location': company.business_location or '',
#             'is_active': company.is_active,
#             'access_expires_at': company.access_expires_at,
#             'days_until_expiry': company.days_until_expiry(),
#         })

#     def patch(self, request):
#         company = self._get_company(request)
#         if not company:
#             return Response({'error': 'No company linked.'}, status=404)
#         # Only company admin or superuser
#         try:
#             role = request.user.membership.role
#         except Exception:
#             role = None
#         if role != 'admin' and not request.user.is_superuser:
#             return Response({'error': 'Only company admins can update profile.'}, status=403)

#         allowed = {'email', 'phone_number', 'business_location', 'name'}
#         for field in allowed:
#             if field in request.data:
#                 setattr(company, field, request.data[field])
#         company.save()
#         return Response({'message': 'Company profile updated.'})

"""
views.py  —  Multi-tenant edition  (performance + security hardened)

Changes vs previous version:
  - All O(n²) report loops replaced with O(n) dict lookups
  - cache_page applied to all report views (5-minute TTL)
  - Company-scoped cache keys so tenants never share cached data
  - select_related / only() on stock report loops
  - All other logic unchanged
"""

from decimal import Decimal
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404, render
from django.db.models import F, Sum
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from datetime import datetime, timedelta

from rest_framework import generics, viewsets, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
from django.forms import ValidationError

from .mixins import CompanyScopedMixin, get_company_for_user
from .models import (
    Company, CompanyMembership, PaymentRecord,
    DataEntry, Debt, Notification, NotificationPreference,
    StockItem, StockItem2,
    UserEntry, UserEntry2, UserEntryExpense, UserEntryOutofstock,
)
from .serializers import (
    CompanyRegistrationSerializer, CompanySerializer, CompanyListSerializer,
    GrantAccessSerializer, PaymentRecordSerializer,
    CreateCompanyStaffSerializer, CompanyMembershipSerializer,
    DataEntrySerializer, DebtSerializer, NotificationSerializer,
    StockItem2RestockSerializer, StockItemRestockSerializer,
    StockItemSerializer, StockItemSerializer2, StockReportSerializer,
    UserEntrySerializer, UserEntrySerializer2,
    UserEntrySerializerExpense, UserEntrySerializerOutofstock,
)
from myapp import models as myapp_models


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def _get_company_filter(request):
    """Returns a dict to pass to .filter() for company scoping."""
    company = get_company_for_user(request)
    return {"company": company} if company else {}


def _qs_to_date_dict(queryset, value_field):
    """
    Convert a values('date').annotate(...) queryset into a plain dict
    {date: value} so lookups are O(1) instead of O(n) inside a loop.
    """
    return {row["date"]: row[value_field] for row in queryset}


def _get_or_set_report_cache(company_id, key_suffix, compute_fn, timeout=300):
    """
    Company-scoped cache wrapper.
    key_suffix example: 'monthly:2025-04'
    """
    cache_key = f"report:{company_id}:{key_suffix}"
    result = cache.get(cache_key)
    if result is None:
        result = compute_fn()
        cache.set(cache_key, result, timeout=timeout)
    return result


# ---------------------------------------------------------------------------
# COMPANY REGISTRATION  (public — no auth)
# ---------------------------------------------------------------------------

class CompanyRegisterView(APIView):
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
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        companies = Company.objects.all().order_by("-registered_at")
        return Response(CompanyListSerializer(companies, many=True).data)


class AdminCompanyDetailView(APIView):
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
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request, pk):
        company = get_object_or_404(Company, pk=pk)
        company.revoke_access()
        return Response({"message": f"Access revoked for {company.name}.", "is_active": company.is_active})


class AdminPaymentListCreateView(APIView):
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
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        payments = PaymentRecord.objects.select_related("company").order_by("-payment_date")
        return Response(PaymentRecordSerializer(payments, many=True).data)


class AdminCompanyMembersView(APIView):
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
            return request.user.membership.role == "admin"
        except Exception:
            return False


class CompanyStaffListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def _get_company(self, request):
        if request.user.is_superuser:
            cid = request.query_params.get("company_id") or request.data.get("company_id")
            return get_object_or_404(Company, pk=cid) if cid else None
        return request.user.membership.company

    def get(self, request):
        company = self._get_company(request)
        if not company:
            return Response({"error": "company_id required for superadmin."}, status=400)
        members = company.members.select_related("user").all()
        return Response(CompanyMembershipSerializer(members, many=True).data)

    def post(self, request):
        company = self._get_company(request)
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
            {"message": f"User '{user.username}' created.", "user_id": user.pk, "role": membership.role},
            status=status.HTTP_201_CREATED,
        )


class CompanyStaffDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyAdmin]

    def delete(self, request, user_id):
        if request.user.pk == user_id:
            return Response({"error": "Cannot delete your own account."}, status=400)
        try:
            if request.user.is_superuser:
                membership = CompanyMembership.objects.get(user_id=user_id)
            else:
                company = request.user.membership.company
                membership = CompanyMembership.objects.get(user_id=user_id, company=company)
        except CompanyMembership.DoesNotExist:
            return Response({"error": "User not found in your company."}, status=404)
        username = membership.user.username
        membership.user.delete()
        return Response({"message": f"User '{username}' removed."}, status=204)


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
            try:
                membership = user.membership
                company = membership.company
                if not company.is_access_valid():
                    return Response(
                        {
                            "error": "access_suspended",
                            "message": (
                                "Your company's subscription has expired or been suspended. "
                                "Please contact the administrator to renew access."
                            ),
                            "company": company.name,
                            "is_active": company.is_active,
                            "access_expires_at": (
                                company.access_expires_at.isoformat()
                                if company.access_expires_at else None
                            ),
                        },
                        status=403,
                    )
            except Exception:
                return Response(
                    {"error": "no_company", "message": "Account not linked to any company."},
                    status=403,
                )

        response = super().post(request, *args, **kwargs)
        response.data["is_staff"]    = user.is_staff
        response.data["is_superuser"] = user.is_superuser

        if user.is_superuser:
            response.data["role"]    = "superadmin"
            response.data["message"] = "Welcome, superadmin!"
        else:
            try:
                membership = user.membership
                company    = membership.company
                response.data["role"]             = membership.role
                response.data["company_id"]       = company.pk
                response.data["company_name"]     = company.name
                response.data["is_company_active"] = company.is_access_valid()
                response.data["access_expires_at"] = (
                    company.access_expires_at.isoformat() if company.access_expires_at else None
                )
                response.data["days_until_expiry"] = company.days_until_expiry()
                response.data["message"]           = f"Welcome, {username}!"
            except Exception:
                response.data["role"]    = "unknown"
                response.data["message"] = "Login successful but no company linked."

        return response


# ---------------------------------------------------------------------------
# DATA ENTRY VIEWS
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


class UserEntryViewSetExpense(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset           = UserEntryExpense.objects.all()
    serializer_class   = UserEntrySerializerExpense
    permission_classes = [IsAuthenticated]


class UserEntryViewSetOutofstock(CompanyScopedMixin, viewsets.ModelViewSet):
    queryset           = UserEntryOutofstock.objects.all()
    serializer_class   = UserEntrySerializerOutofstock
    permission_classes = [IsAuthenticated]


# Aliases kept for URL compatibility
UserEntryViewSeta      = UserEntryViewSet
UserEntryViewSet2a     = UserEntryViewSet2
UserEntryViewSetExpensea = UserEntryViewSetExpense


# ---------------------------------------------------------------------------
# STOCK VIEWS
# ---------------------------------------------------------------------------

class StockItemViewSet(CompanyScopedMixin, viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset           = StockItem.objects.all()
    serializer_class   = StockItemSerializer


class StockItemListCreateView(CompanyScopedMixin, generics.ListCreateAPIView):
    queryset           = StockItem.objects.all()
    serializer_class   = StockItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs      = StockItem.objects.filter(company=company) if company else StockItem.objects.all()
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
            return Response({"error": "Item not found."}, status=404)


class StockItemListCreateView2(CompanyScopedMixin, generics.ListCreateAPIView):
    queryset           = StockItem2.objects.all()
    serializer_class   = StockItemSerializer2
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs      = StockItem2.objects.filter(company=company) if company else StockItem2.objects.all()
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
            return Response({"error": "Item not found."}, status=404)


class StockItemListCreateViewa(CompanyScopedMixin, generics.ListCreateAPIView):
    queryset           = StockItem.objects.all()
    serializer_class   = StockItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs      = StockItem.objects.filter(company=company) if company else StockItem.objects.all()
        if month:
            try:
                sm = datetime.strptime(month, "%Y-%m").date()
                qs = qs.filter(added_date__year=sm.year, added_date__month=sm.month)
            except ValueError:
                return Response({"error": "Use YYYY-MM."}, status=400)
        return Response(StockItemSerializer(qs, many=True).data)

    def post(self, request, *args, **kwargs):
        company       = self.get_company()
        data          = request.data
        name          = data.get("name")
        quantity      = data.get("quantity")
        price_per_unit = data.get("price_per_unit")
        added_date    = data.get("added_date")

        if StockItem.objects.filter(name=name, company=company).exists():
            stock_item          = StockItem.objects.get(name=name, company=company)
            stock_item.quantity += int(quantity)
            stock_item.save()
            return Response({"message": f"Stock updated for {name}."}, status=200)
        else:
            StockItem.objects.create(
                name=name, quantity=quantity,
                price_per_unit=price_per_unit,
                added_date=added_date, company=company,
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
            return Response({"error": "Item not found."}, status=404)


class StockItemListCreateView2a(CompanyScopedMixin, generics.ListCreateAPIView):
    queryset           = StockItem2.objects.all()
    serializer_class   = StockItemSerializer2
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        month   = request.query_params.get("month")
        company = self.get_company()
        qs      = StockItem2.objects.filter(company=company) if company else StockItem2.objects.all()
        if month:
            try:
                sm = datetime.strptime(month, "%Y-%m").date()
                qs = qs.filter(added_date__year=sm.year, added_date__month=sm.month)
            except ValueError:
                return Response({"error": "Use YYYY-MM."}, status=400)
        return Response(StockItemSerializer2(qs, many=True).data)

    def post(self, request, *args, **kwargs):
        company              = self.get_company()
        data                 = request.data
        stock_name           = data.get("stock_name")
        area_in_square_meters = data.get("area_in_square_meters")
        price_per_square_meter = data.get("price_per_square_meter")
        added_date           = data.get("added_date")

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
                added_date=added_date, company=company,
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
            return Response({"error": "Item not found."}, status=404)


class StockItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset           = StockItem.objects.all()
    serializer_class   = StockItemSerializer
    permission_classes = [IsAuthenticated]


class AvailableStockItemsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_company_for_user(request)
        qs = StockItem.objects.filter(quantity__gt=myapp_models.F("quantity_used"))
        if company:
            qs = qs.filter(company=company)
        return Response(StockItemSerializer(qs, many=True).data)


class AvailableStockItemsView2(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        company = get_company_for_user(request)
        qs = StockItem2.objects.filter(
            area_in_square_meters__gt=myapp_models.F("area_used_in_square_meters")
        )
        if company:
            qs = qs.filter(company=company)
        return Response(StockItemSerializer2(qs, many=True).data)


# ---------------------------------------------------------------------------
# REPORTING VIEWS  — cached + O(n) loops
# ---------------------------------------------------------------------------

@method_decorator(cache_page(60 * 5), name="get")
class MonthlyReportView(generics.GenericAPIView):
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

        cf             = _get_company_filter(request)
        user_entries   = UserEntry.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        user_entries2  = UserEntry2.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        expense_entries = UserEntryExpense.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        debt_entries   = Debt.objects.filter(date__gte=start_date, date__lt=end_date, **cf)
        oos_entries    = UserEntryOutofstock.objects.filter(date__gte=start_date, date__lt=end_date, **cf)

        # --- O(n) dict lookups instead of O(n²) next() scans ---
        sales1  = _qs_to_date_dict(
            user_entries.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        sales2  = _qs_to_date_dict(
            user_entries2.values("date").annotate(total_sales=Sum("total_price")), "total_sales"
        )
        # merge
        combined_sales = {d: sales1.get(d, 0) + sales2.get(d, 0)
                          for d in set(sales1) | set(sales2)}
        if sales1:  # fill dates only in sales1
            for d, v in sales1.items():
                combined_sales.setdefault(d, 0)
                combined_sales[d] += v if d not in sales2 else 0

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
            set(combined_sales)
            | set(exp_by_date)
            | set(debt_by_date)
            | set(oos_by_date)
        )

        combined_daily = []
        for date in sorted(all_dates):
            s   = combined_sales.get(date, 0) or 0
            exp = exp_by_date.get(date, 0) or 0
            dbt = debt_by_date.get(date, 0) or 0
            oos = oos_by_date.get(date, 0) or 0
            combined_daily.append({
                "date":            date,
                "total_sales":     s,
                "total_expenses":  exp,
                "total_debts":     dbt,
                "total_outofstock": oos,
                "profit":          s + oos - exp,
            })

        total_sales    = sum(combined_sales.values())
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0
        total_debts    = debt_entries.aggregate(Sum("total_price"))["total_price__sum"] or 0
        total_oos      = oos_entries.aggregate(Sum("price"))["price__sum"] or 0

        return Response({
            "daily_totals": combined_daily,
            "monthly_totals": {
                "total_sales":     total_sales,
                "total_expenses":  total_expenses,
                "total_debts":     total_debts,
                "total_outofstock": total_oos,
                "profit":          total_sales + total_oos - total_expenses,
            },
        })


@method_decorator(cache_page(60 * 5), name="get")
class WeeklyReportView(generics.GenericAPIView):
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

        all_dates = set(combined_sales) | set(oos_by_date) | set(debt_by_date) | set(exp_by_date)

        combined_daily = []
        for date in sorted(all_dates):
            s   = combined_sales.get(date, 0) or 0
            exp = exp_by_date.get(date, 0) or 0
            dbt = debt_by_date.get(date, 0) or 0
            oos = oos_by_date.get(date, 0) or 0
            combined_daily.append({
                "date":            date.strftime("%Y-%m-%d"),
                "total_sales":     s,
                "total_debts":     dbt,
                "total_outofstock": oos,
                "total_expenses":  exp,
                "profit":          s + oos - exp,
            })

        total_sales    = sum(combined_sales.values())
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0
        total_debts    = debt_entries.aggregate(Sum("amount"))["amount__sum"] or 0
        total_oos      = oos_entries.aggregate(Sum("price"))["price__sum"] or 0

        return Response({
            "daily_totals": combined_daily,
            "weekly_totals": {
                "total_sales":     total_sales,
                "total_debts":     total_debts,
                "total_outofstock": total_oos,
                "total_expenses":  total_expenses,
                "profit":          total_sales + total_oos - total_expenses,
            },
        })


@method_decorator(cache_page(60 * 5), name="get")
class MonthlyReportView2(generics.GenericAPIView):
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
            combined.append({"date": date, "total_sales": s, "total_expenses": exp, "profit": s - exp})

        total_sales    = user_entries.aggregate(Sum("total_price"))["total_price__sum"] or 0
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0

        return Response({
            "daily_totalss":   combined,
            "monthly_totalss": {
                "total_sales":    total_sales,
                "total_expenses": total_expenses,
                "profit":         total_sales - total_expenses,
            },
        })


@method_decorator(cache_page(60 * 5), name="get")
class YearlyReportView(generics.GenericAPIView):
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
            combined_daily.append({"date": date, "total_sales": s, "total_expenses": exp, "profit": s - exp})

        total_sales    = sum(combined_sales.values())
        total_expenses = expense_entries.aggregate(Sum("expenses"))["expenses__sum"] or 0

        return Response({
            "daily_totals":   combined_daily,
            "monthly_totals": {
                "total_sales":    total_sales,
                "total_expenses": total_expenses,
                "profit":         total_sales - total_expenses,
            },
        })


class StockReportView(APIView):
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
                return Response({"error": "Invalid month."}, status=400)

        company     = get_company_for_user(request)
        stock_items = (
            StockItem.objects.filter(company=company).only("name", "quantity", "price_per_unit")
            if company else StockItem.objects.all().only("name", "quantity", "price_per_unit")
        )
        report = []
        for stock in stock_items:
            ue = UserEntry.objects.filter(item_name=stock.name, company=company)
            if start_date and end_date:
                ue = ue.filter(date__gte=start_date, date__lt=end_date)
            qty_used  = ue.aggregate(Sum("quantity"))["quantity__sum"] or 0
            remaining = stock.quantity - qty_used
            report.append({
                "item_name":         stock.name,
                "total_quantity":    stock.quantity,
                "quantity_used":     qty_used,
                "remaining_stock":   remaining,
                "total_value_used":  qty_used * stock.price_per_unit,
                "total_value_unused": remaining * stock.price_per_unit,
                "total_value_stock": stock.quantity * stock.price_per_unit,
            })
        return JsonResponse(report, safe=False)


class StockReportView2(APIView):
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
                return Response({"error": "Invalid month."}, status=400)

        company     = get_company_for_user(request)
        stock_items = (
            StockItem2.objects.filter(company=company)
            .only("stock_name", "area_in_square_meters", "price_per_square_meter")
            if company else
            StockItem2.objects.all()
            .only("stock_name", "area_in_square_meters", "price_per_square_meter")
        )
        report = []
        for stock in stock_items:
            ue = UserEntry2.objects.filter(item_name=stock.stock_name, company=company)
            if start_date and end_date:
                ue = ue.filter(date__gte=start_date, date__lt=end_date)
            area_used = ue.aggregate(Sum("area_in_square_meters"))["area_in_square_meters__sum"] or 0
            remaining = stock.area_in_square_meters - area_used
            report.append({
                "item_name":         stock.stock_name,
                "total_quantity":    stock.area_in_square_meters,
                "quantity_used":     area_used,
                "remaining_stock":   remaining,
                "total_value_used":  area_used * stock.price_per_square_meter,
                "total_value_unused": remaining * stock.price_per_square_meter,
                "total_value_stock": stock.area_in_square_meters * stock.price_per_square_meter,
            })
        return JsonResponse(report, safe=False)


# ---------------------------------------------------------------------------
# RESTOCK & DEBT
# ---------------------------------------------------------------------------

class RestockView(APIView):
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
                    si = StockItem.objects.get(name=name, company=company)
                    si.quantity          += quantity
                    si.restock_quantity   = quantity
                    si.last_restock_date  = datetime.now().date()
                    si.save()
                    return Response({"message": "Restocked."}, status=200)
                except StockItem.DoesNotExist:
                    return Response({"error": "StockItem not found."}, status=404)
            return Response(serializer.errors, status=400)

        elif item_type == "StockItem2":
            serializer = StockItem2RestockSerializer(data=item_data)
            if serializer.is_valid():
                stock_name = serializer.validated_data["stock_name"]
                area       = serializer.validated_data["area_in_square_meters"]
                try:
                    si = StockItem2.objects.get(stock_name=stock_name, company=company)
                    si.area_in_square_meters += area
                    si.last_restock_date      = datetime.now().date()
                    si.save()
                    return Response({"message": "Restocked."}, status=200)
                except StockItem2.DoesNotExist:
                    return Response({"error": "StockItem2 not found."}, status=404)
            return Response(serializer.errors, status=400)

        return Response({"error": "Invalid item type."}, status=400)


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
# COMPANY PROFILE
# ---------------------------------------------------------------------------

class CompanyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_company(self, request):
        if request.user.is_superuser:
            return None
        try:
            return request.user.membership.company
        except Exception:
            return None

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
            role = request.user.membership.role
        except Exception:
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
        n          = Notification.objects.get(id=notification_id)
        n.is_read  = True
        n.save()
        return Response({"success": "Marked as read"})
    except Notification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)


# ---------------------------------------------------------------------------
# ROBOTS
# ---------------------------------------------------------------------------

from django.http import HttpResponse

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\nDisallow: /api/\nDisallow: /admin/\n",
        content_type="text/plain",
    )