from rest_framework import status

from receipt_processor.commons.generic_constants import GenericConstants
from receipts.models import Receipt
from receipts.services.service_helper.receipts_service_helper import ReceiptsServiceHelper


class GetPoints(ReceiptsServiceHelper):
    def __init__(self):
        super().__init__()
        self.error_message = None

    def get_request_params(self, *args, **kwargs) -> dict:
        """
        This function will extract the request parameters from the request object

        @params: *args
        @params: **kwargs
        """
        return {
            "id": kwargs.get("id")
        }

    def get_data(self, *args, **kwargs) -> dict:
        """
        This function is the entry point of the service.

        @params: *args
        @params: **kwargs

        @return: Dictionary API response
        """
        params = self.get_request_params(*args, **kwargs)
        self.validate_id(params.get("id"))
        if self.status_code is not None:
            return {"message": self.error_message}
        return self.get_points(params)

    def validate_id(self, receipts_id) -> None:
        """
        This functions validate if id is provided in the url.

        @params: String receipts_id - Receipt Id
        """
        if receipts_id is None:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.INVALID_URL.format(receipts_id)
            return
        return

    def get_points(self, params) -> dict:
        """
        This function gets the points from the database.

        @params: Dictionary params - Request Params

        @return: Dictionary API response
        """
        data = Receipt.objects.filter(id=params["id"]).values("points")
        print(len(data))
        if len(data) == 0:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.INVALID_ID.format(params["id"])
            return {"message": self.error_message}
        return {"points": data[0].get("points")}
