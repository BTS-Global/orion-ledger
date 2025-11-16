from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AnnualReturnViewSet,
    EconomicSubstanceReportViewSet,
    JurisdictionFeeViewSet,
    ExchangeRateViewSet,
    CorporateServiceClientViewSet,
)

router = DefaultRouter()
router.register(r'annual-returns', AnnualReturnViewSet, basename='annual-return')
router.register(r'es-reports', EconomicSubstanceReportViewSet, basename='es-report')
router.register(r'fees', JurisdictionFeeViewSet, basename='jurisdiction-fee')
router.register(r'exchange-rates', ExchangeRateViewSet, basename='exchange-rate')
router.register(r'clients', CorporateServiceClientViewSet, basename='corporate-client')

urlpatterns = [
    path('', include(router.urls)),
]
