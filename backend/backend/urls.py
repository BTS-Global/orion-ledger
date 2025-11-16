"""
URL configuration for accounting software backend.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from companies.views import CompanyViewSet, UserProfileViewSet, ChartOfAccountsViewSet
from documents.views import DocumentViewSet
from transactions.views import TransactionViewSet, JournalEntryViewSet
from reports.views import ReportViewSet
from irs_forms.views import IRSFormViewSet
from core.views import current_user, logout_view, auth_status, get_csrf_token, debug_session, test_login
from core.auth_views import register_user, login_user, logout_user

# Create router and register viewsets
router = DefaultRouter()
router.register(r'companies', CompanyViewSet, basename='company')
router.register(r'profiles', UserProfileViewSet, basename='userprofile')
router.register(r'accounts', ChartOfAccountsViewSet, basename='chartofaccounts')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'journal-entries', JournalEntryViewSet, basename='journalentry')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'irs-forms', IRSFormViewSet, basename='irsform')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Authentication API
    path('api/auth/user/', current_user, name='current-user'),
    path('api/auth/logout/', logout_view, name='logout'),
    path('api/auth/status/', auth_status, name='auth-status'),
    path('api/auth/csrf/', get_csrf_token, name='csrf-token'),
    
    # Debug endpoints
    path('api/debug/session/', debug_session, name='debug-session'),
    path('api/debug/test-login/', test_login, name='test-login'),
    # Local authentication
    path('api/auth/register/', register_user, name='register'),
    path('api/auth/login/', login_user, name='login'),
    path('api/auth/logout-local/', logout_user, name='logout-local'),
    
    # Social auth
    path('accounts/', include('allauth.urls')),
    path('api-auth/', include('rest_framework.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

