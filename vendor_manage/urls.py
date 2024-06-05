from django.urls import path, include
from .views import VendorDetail, PurchaseOrderViewSet, VendorPerformanceView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'purchase_orders', PurchaseOrderViewSet)

urlpatterns = [
    path('vendors/', VendorDetail.as_view(), name="vendors"),
    path('vendors/<int:pk>/', VendorDetail.as_view(), name="vendor-detail"),
    path('vendors/<int:vendor_id>/performance/', VendorPerformanceView.as_view(), name="vendor-performance"),
    path('', include(router.urls)),
]
