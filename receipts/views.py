from django.http import JsonResponse
from rest_framework import generics
from rest_framework.views import APIView

from receipt_processor.services.view_services import ViewsServices


class ProcessReceipts(APIView):
    """
    API Process Receipts View
    """
    def post(self, request, *args, **kwargs) -> JsonResponse:
        """
        Post API to process receipts
        Request Example
        {
            "retailer": "Walgreens",
            "purchaseDate": "2022-01-02",
            "purchaseTime": "08:13",
            "total": "2.65",
            "items": [
                {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
                {"shortDescription": "Dasani", "price": "1.40"}
            ]
        }
        """
        kwargs.update({
            "request": request
        })
        service_obj = ViewsServices(service_name="process_receipts")
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)


class GetPoints(generics.ListAPIView):
    """
    API Request to get points calculated on receipts
    The id of receipt is taken from url.
    """
    def get(self, request, *args, **kwargs) -> JsonResponse:
        """
        Get API to get receipts points
        """
        kwargs.update({
            "request": request
        })
        service_obj = ViewsServices(service_name="get_points")
        status_code, data = service_obj.execute_service(*args, **kwargs)
        return JsonResponse(data, safe=False, status=status_code)

