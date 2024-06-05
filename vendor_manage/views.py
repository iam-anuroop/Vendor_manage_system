from django.shortcuts import render
from .serializers import VendorSerializer, PurchaseOrderSerializer, HistoricalPerformanceSerializer
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import status
from django.db.models import Avg, F, Count, ExpressionWrapper, fields



class VendorDetail(APIView):

    def update_performance(self, vendor):
        orders = PurchaseOrder.objects.filter(vendor=vendor)
        
        completed_orders = orders.filter(status='completed')
        total_orders = orders.count()
        completed_count = completed_orders.count()

        if completed_count == 0:
            return 0

        on_time_delivery_rate = completed_orders.filter(delivery_date__lte=F('delivery_date')).count() / completed_count * 100
        quality_rating_avg = completed_orders.aggregate(Avg('quality_rating'))['quality_rating__avg'] or 0

        response_times = completed_orders.annotate(
            response_time=ExpressionWrapper(F('acknowledgment_date') - F('issue_date'), output_field=fields.DurationField())
        ).aggregate(Avg('response_time'))['response_time__avg']
        
        average_response_time = response_times.total_seconds() / 3600 if response_times else 0
        fulfillment_rate = completed_count / total_orders * 100

        vendor.on_time_delivery_rate = on_time_delivery_rate
        vendor.quality_rating_avg = quality_rating_avg
        vendor.average_response_time = average_response_time
        vendor.fulfillment_rate = fulfillment_rate
        vendor.save()

        historical_performance, created = HistoricalPerformance.objects.get_or_create(
        vendor=vendor
        )

        update_fields = {}
        if vendor.on_time_delivery_rate > historical_performance.on_time_delivery_rate:
            update_fields['on_time_delivery_rate'] = vendor.on_time_delivery_rate
        if vendor.quality_rating_avg > historical_performance.quality_rating_avg:
            update_fields['quality_rating_avg'] = vendor.quality_rating_avg
        if vendor.average_response_time < historical_performance.average_response_time or historical_performance.average_response_time == 0:
            update_fields['average_response_time'] = vendor.average_response_time
        if vendor.fulfillment_rate > historical_performance.fulfillment_rate:
            update_fields['fulfillment_rate'] = vendor.fulfillment_rate

        if update_fields:
            for key, value in update_fields.items():
                setattr(historical_performance, key, value)
            historical_performance.save()

            return "done"


    def post(self, request):
        serializer = VendorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, pk=None):
        try:
            if pk is not None:
                vendor = Vendor.objects.get(pk=pk)
            else:
                vendor = Vendor.objects.all()
        except:
            return Response({"msg":"No user Available"},status=status.HTTP_400_BAD_REQUEST)
        serializer = VendorSerializer(vendor)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self, request, pk):
        try:
            vendor = Vendor.objects.get(pk=pk)
        except:
            return Response({"msg":"No user Available"},status=status.HTTP_400_BAD_REQUEST)
        serializer = VendorSerializer(vendor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            self.update_performance(vendor)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            vendor = Vendor.objects.get(pk=pk)
        except:
            return Response({"msg":"No user Available"},status=status.HTTP_400_BAD_REQUEST)
        vendor.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class VendorPerformanceView(APIView):
    def get(elf, request, vendor_id):
        try:
            vendor = Vendor.objects.get(pk=vendor_id)
        except:
            return Response({"msg":"No user Available"},status=status.HTTP_400_BAD_REQUEST) 
        
        historical_performance = HistoricalPerformance.objects.get(vendor=vendor)
        serializer = HistoricalPerformanceSerializer(historical_performance)
        
        return Response(serializer.data, status=status.HTTP_200_OK)