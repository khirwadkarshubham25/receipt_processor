from rest_framework import status

from receipts.services.get_points import GetPoints
from receipts.services.process_receipts import ProcessReceipts


class ViewsServices:
    def __init__(self, service_name=None):
        self.service_config = {
            "process_receipts": self.ProcessReceipts,
            "get_points": self.GetPoints
        }
        self.service_obj = self.service_config[service_name].get_instance()

    def execute_service(self, *args, **kwargs):
        self.service_obj.execute_service(*args, **kwargs)
        if self.service_obj.status_code is not None:
            status_code = self.service_obj.status_code
        else:
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR if self.service_obj.error else status.HTTP_200_OK
        data = self.service_obj.data

        return status_code, data

    class ProcessReceipts:
        @staticmethod
        def get_instance():
            return ProcessReceipts()

    class GetPoints:
        @staticmethod
        def get_instance():
            return GetPoints()
