from django.urls import path
from .views import AvailableStockItemsView, AvailableStockItemsView2, ChangePasswordView, DataEntryListCreateView, DebtEntryViewSet, MonthlyReportView, MonthlyReportView2, RestockView, StockItemListCreateView, StockItemDetailView, StockItemListCreateView2, StockItemListCreateView2a, StockItemListCreateViewa, StockReportView, StockReportView2, UserDeleteView, UserEntryViewSet, UserEntryViewSet2, UserEntryViewSet2a, UserEntryViewSetExpense, UserEntryViewSetExpensea, UserEntryViewSetOutofstock, UserEntryViewSeta, UserListCreateView, WeeklyReportView, YearlyReportView, get_notifications, update_preferences
from myapp import views

# urlpatterns = [
#     # path('data/', DataEntryListCreateView.as_view(), name='data-entry'),
#     path('data/monthly/', MonthlyReportView.as_view(), name='monthly-report'),
#     path('data/weekly/', WeeklyReportView.as_view(), name='monthly-report'),
#     path('data/monthly2/', MonthlyReportView2.as_view(), name='monthly-report'),
#     path('api/stock/report/', StockReportView.as_view(), name='stock-report'),
#     path('api/stock/report2/', StockReportView2.as_view(), name='stock-report'),
#     path('api/stock/', StockItemListCreateView.as_view(), name='stock-list-create'),
#     path('api/stock2/', StockItemListCreateView2.as_view(), name='stock-list-create'),

    


#     path('api/notifications/', views.fetch_notifications, name='fetch_notifications'),
#     path('api/notifications/read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
#     path('api/update-preferences/', update_preferences, name='update_preferences'),

#     path('data/yearly/', YearlyReportView.as_view(), name='monthly-report'),

    
#     path('debts/', DebtEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='debt-list-create'),
#     path('debts/<int:pk>/', DebtEntryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='debt-list-create'),    
#     path('api/stock/<int:pk>/', StockItemDetailView.as_view(), name='stock-detail'),
#     path('api/restock/', RestockView.as_view(), name='restock'),
#     path('data/', UserEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
      
#     path('data2/', UserEntryViewSet2.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
#     path('dataa/', UserEntryViewSeta.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
#     path('dataa/<int:pk>/', UserEntryViewSeta.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentrya-detail'),


#     path('data2a/', UserEntryViewSet2a.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
#     path('dataexpensea/', UserEntryViewSetExpensea.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
#     path('dataexpense/', UserEntryViewSetExpense.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
#     path('dataexpense/<int:pk>/', UserEntryViewSetExpense.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry-list-create'),
#     path('data/accidentalbanner', UserEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
#     path('available-stock/', AvailableStockItemsView.as_view(), name='available-stock'),
#     path('available-stock2/', AvailableStockItemsView2.as_view(), name='available-stock'),


#     path('dataoutofstock/', UserEntryViewSetOutofstock.as_view({'get': 'list', 'post': 'create'}), name='userentry-list-create'),
#     path('dataoutofstock/<int:pk>/', UserEntryViewSetOutofstock.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry-list-create'),

#     path('users/', UserListCreateView.as_view(), name='user-list-create'),
#     path('users/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),
#     path('change-password/', ChangePasswordView.as_view(), name='change-password'),
   
# ]
# myapp/urls.py

from django.urls import path
from myapp import views

urlpatterns = [

    # -----------------------------------------------------------------------
    # COMPANY REGISTRATION
    # -----------------------------------------------------------------------
    path('company/register/', views.CompanyRegisterView.as_view(), name='company-register'),
    path('company/register-new/', views.AuthenticatedCompanyRegisterView.as_view(), name='company-register-new'),
    path('company/profile/', views.CompanyProfileView.as_view(), name='company-profile'),

    # -----------------------------------------------------------------------
    # SUPERADMIN — COMPANY MANAGEMENT
    # -----------------------------------------------------------------------
    path('admin/companies/',                             views.AdminCompanyListView.as_view(),     name='admin-company-list'),
    path('admin/companies/<int:pk>/',                    views.AdminCompanyDetailView.as_view(),   name='admin-company-detail'),
    path('admin/companies/<int:pk>/grant-access/',       views.AdminGrantAccessView.as_view(),     name='admin-grant-access'),
    path('admin/companies/<int:pk>/revoke-access/',      views.AdminRevokeAccessView.as_view(),    name='admin-revoke-access'),
    path('admin/companies/<int:pk>/payments/',           views.AdminPaymentListCreateView.as_view(), name='admin-company-payments'),
    path('admin/companies/<int:pk>/members/',            views.AdminCompanyMembersView.as_view(),  name='admin-company-members'),
    path('admin/payments/',                              views.AdminAllPaymentsView.as_view(),     name='admin-all-payments'),

    # -----------------------------------------------------------------------
    # COMPANY-ADMIN — STAFF MANAGEMENT
    # -----------------------------------------------------------------------
    path('company/staff/',              views.CompanyStaffListCreateView.as_view(), name='company-staff-list'),
    path('company/staff/<int:user_id>/', views.CompanyStaffDeleteView.as_view(),    name='company-staff-delete'),
    path('company/my-companies/',        views.UserCompaniesView.as_view(),          name='my-companies'),

    # -----------------------------------------------------------------------
    # DATA ENTRY (all scoped to the authenticated user's company)
    # -----------------------------------------------------------------------
    path('data/',            views.UserEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='userentry-list'),
    path('data/<int:pk>/',   views.UserEntryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry-detail'),

    path('data2/',           views.UserEntryViewSet2.as_view({'get': 'list', 'post': 'create'}), name='userentry2-list'),
    path('data2/<int:pk>/',  views.UserEntryViewSet2.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry2-detail'),

    path('dataa/',           views.UserEntryViewSeta.as_view({'get': 'list', 'post': 'create'}), name='userentrya-list'),
    path('dataa/<int:pk>/',  views.UserEntryViewSeta.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentrya-detail'),

    path('data2a/',          views.UserEntryViewSet2a.as_view({'get': 'list', 'post': 'create'}), name='userentry2a-list'),
    path('data2a/<int:pk>/', views.UserEntryViewSet2a.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='userentry2a-detail'),

    path('dataexpense/',           views.UserEntryViewSetExpense.as_view({'get': 'list', 'post': 'create'}), name='expense-list'),
    path('dataexpense/<int:pk>/',  views.UserEntryViewSetExpense.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='expense-detail'),

    path('dataexpensea/',          views.UserEntryViewSetExpensea.as_view({'get': 'list', 'post': 'create'}), name='expensea-list'),

    path('dataoutofstock/',           views.UserEntryViewSetOutofstock.as_view({'get': 'list', 'post': 'create'}), name='outofstock-list'),
    path('dataoutofstock/<int:pk>/',  views.UserEntryViewSetOutofstock.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='outofstock-detail'),

    # -----------------------------------------------------------------------
    # STOCK
    # -----------------------------------------------------------------------
    path('api/stock/',           views.StockItemListCreateView.as_view(),  name='stock-list'),
    path('api/stock/<int:pk>/',  views.StockItemDetailView.as_view(),      name='stock-detail'),
    path('api/stock2/',          views.StockItemListCreateView2.as_view(), name='stock2-list'),

    path('api/stocka/',          views.StockItemListCreateViewa.as_view(),  name='stocka-list'),
    path('api/stock2a/',         views.StockItemListCreateView2a.as_view(), name='stock2a-list'),

    path('available-stock/',  views.AvailableStockItemsView.as_view(),  name='available-stock'),
    path('available-stock2/', views.AvailableStockItemsView2.as_view(), name='available-stock2'),

    path('api/restock/', views.RestockView.as_view(), name='restock'),

    # -----------------------------------------------------------------------
    # REPORTS
    # -----------------------------------------------------------------------
    path('api/stock/report/',  views.StockReportView.as_view(),  name='stock-report'),
    path('api/stock/report2/', views.StockReportView2.as_view(), name='stock-report2'),

    path('data/monthly/',  views.MonthlyReportView.as_view(),  name='monthly-report'),
    path('data/monthly2/', views.MonthlyReportView2.as_view(), name='monthly-report2'),
    path('data/weekly/',   views.WeeklyReportView.as_view(),   name='weekly-report'),
    path('data/yearly/',   views.YearlyReportView.as_view(),   name='yearly-report'),

    # -----------------------------------------------------------------------
    # DEBTS
    # -----------------------------------------------------------------------
    path('debts/',           views.DebtEntryViewSet.as_view({'get': 'list', 'post': 'create'}), name='debt-list'),
    path('debts/<int:pk>/',  views.DebtEntryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='debt-detail'),

    # -----------------------------------------------------------------------
    # NOTIFICATIONS
    # -----------------------------------------------------------------------
    path('api/notifications/',                                    views.fetch_notifications,       name='fetch-notifications'),
    path('api/notifications/read/<int:notification_id>/',         views.mark_notification_as_read, name='mark-notification-read'),
    path('api/update-preferences/',                               views.update_preferences,        name='update-preferences'),

    # -----------------------------------------------------------------------
    # USER MANAGEMENT (superadmin)
    # -----------------------------------------------------------------------
    path('users/',           views.UserListCreateView.as_view(),  name='user-list'),
    path('users/<int:pk>/',  views.UserDeleteView.as_view(),      name='user-delete'),
    path('change-password/', views.ChangePasswordView.as_view(),  name='change-password'),
]
