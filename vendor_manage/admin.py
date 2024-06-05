from django.contrib import admin
from .models import (Vendor, PurchaseOrder, HistoricalPerformance)


class VendorAdmin(admin.ModelAdmin):
    list_display = (
        "name","contact_details","address","vendor_code",
        "on_time_delivery_rate","quality_rating_avg",
        "average_response_time","fulfillment_rate"
        )
admin.site.register(Vendor,VendorAdmin)

class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = (
        "po_number","vendor","order_date",
        "delivery_date","items","quantity",
        "status"
    )
admin.site.register(PurchaseOrder,PurchaseOrderAdmin)

class HistoricalPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "vendor","date","on_time_delivery_rate",
        "quality_rating_avg","average_response_time",
        "fulfillemnt_rate"
    )
admin.site.register(HistoricalPerformance,HistoricalPerformanceAdmin)