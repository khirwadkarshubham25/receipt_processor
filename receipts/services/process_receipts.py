import math
import re
from datetime import datetime

from rest_framework import status

from receipt_processor.commons.generic_constants import GenericConstants
from receipts.models import Receipt, Items
from receipts.services.service_helper.receipts_service_helper import ReceiptsServiceHelper


class ProcessReceipts(ReceiptsServiceHelper):

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
            "retailer": kwargs.get("request").data.get("retailer"),
            "purchase_date": kwargs.get("request").data.get("purchaseDate"),
            "purchase_time": kwargs.get("request").data.get("purchaseTime"),
            "items": kwargs.get("request").data.get("items"),
            "total": kwargs.get("request").data.get("total")
        }

    def get_data(self, *args, **kwargs) -> dict:
        """
        This function is the entry point of the service.

        @params: *args
        @params: **kwargs

        @return: Dictionary API response
        """
        params = self.get_request_params(*args, **kwargs)
        self.validate_params(params)
        if self.status_code is not None:
            return {"message": self.error_message}
        self.validate_receipt(params)
        if self.status_code is not None:
            return self.error_message
        return self.process_receipts(params)

    def validate_params(self, params) -> None:
        """
        This function validates all the request parameters

        @params: Dictionary params - API request parameters
        """
        return (
                self.validate_retailer(params.get("retailer")) or
                self.validate_purchase_date(params.get("purchase_date")) or
                self.validate_purchase_time(params.get("purchase_time")) or
                self.validate_items(params.get("items")) or
                self.validate_total(params.get("total"), params.get("items"))
        )

    def validate_retailer(self, retailer) -> None:
        """
        This function validates if the name of the retailer on receipt it provided or not

        @params: String retailer - Name of the retailer on receipt
        """
        if retailer is None:  # Check if the retailer name is provided or not
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.MANDATORY_MESSAGE.format("retailer")
            return
        return

    def validate_purchase_date(self, purchase_date) -> None:
        """
        This function validates the date of purchase on the receipt

        @params: String purchase_date - Date of purchase on receipt
        """
        if purchase_date is None:  # Check if the purchase date is provided or not
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error = GenericConstants.MANDATORY_MESSAGE.format("purchase date")
            return
        try:
            date = datetime.strptime(purchase_date, "%Y-%m-%d")
        except ValueError:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.INVALID_DATE
        return

    def validate_purchase_time(self, purchase_time) -> None:
        """
        This function validates the time of purchase on the receipt

        @params: String purchase_time - Time of purchase on receipt
        """
        if purchase_time is None:  # Check if the purchase time is provided or not
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.MANDATORY_MESSAGE.format("purchase time")
            return

        try:
            date = datetime.strptime(purchase_time, "%H:%M")
        except ValueError:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.INVALID_TIME

    def validate_items(self, items) -> None:
        """
        This function validates the items provided on receipts

        @params: List items - List of items purchased
        """
        if items is None or len(items) == 0:  # Check if items are provided or not
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.MANDATORY_MESSAGE.format("items")
            return

        for item in items:  # Check it the item details are provided or not
            if item.get("shortDescription") is None:
                self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
                self.error_message = GenericConstants.MANDATORY_MESSAGE.format("short description")
                return

            if item.get("price") is None:
                self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
                self.error_message = GenericConstants.MANDATORY_MESSAGE.format("price")
                return
        return

    def validate_total(self, total_amount, items) -> None:
        """
        This function validated the total amount on the receipt

        @params: Float total_amount - Total amount on the receipt
        @params: List items - List of items purchased
        """
        if total_amount is None:  # Check if total amount is provided or not
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.MANDATORY_MESSAGE.format("total")
            return
        amount = 0
        for item in items:
            amount += float(item.get("price", 0))

        # Check if the total amount is same as the sum of prices of all the items
        if format(amount, ".2f") != total_amount:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.INVALID_VALUE.format("total")
            return
        return

    def validate_receipt(self, params) -> None:
        """
        This function validates if this receipt is already used or not.

        @params: Dictionary params - API request parameters
        """
        receipts = Receipt.objects.filter(
            retailer=params.get("retailer"),
            purchaseDate=params.get("purchase_date"),
            purchaseTime=params.get("purchase_time")
        )
        if len(receipts) > 0:
            self.set_status_code(status_code=status.HTTP_400_BAD_REQUEST)
            self.error_message = GenericConstants.INVALID_RECEIPT_REQUEST

    def process_receipts(self, request_params) -> dict:
        """
        This function will calculate the points and insert the receipt data into the database.

        @params: Dictionary params - API request parameters

        @return: Dictionary - API response
        """
        points = self.calculate_points(request_params)
        # Insert receipt details in the database
        receipts = Receipt.objects.create(
            retailer=request_params.get("retailer"),
            purchaseDate=request_params.get("purchase_date"),
            purchaseTime=request_params.get("purchase_time"),
            total=float(request_params.get("total")),
            points=points
        )

        # Insert all the items on the receipt in the database
        for item in request_params.get("items"):
            Items.objects.create(
                receiptId=receipts,
                shortDescription=item.get("shortDescription"),
                price=float(item.get("price"))
            )
        return {"id": receipts.id}

    @staticmethod
    def calculate_points(request_params) -> int:
        """
        This function will calculate the points from the receipt based on below rules
            1. One point for every alphanumeric character in the retailer name.
            2. 50 points if the total is a round dollar amount with no cents.
            3. 25 points if the total is a multiple of 0.25.
            4. 5 points for every two items on the receipt.
            5. If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
            6. 6 points if the day in the purchase date is odd.
            7. 10 points if the time of purchase is after 2:00pm and before 4:00pm.

        @params: Dictionary params - API request parameters

        @return: Float points - Points calculated based on above rules
        """
        retailer = re.sub(r'\W+', '', request_params.get("retailer"))
        points = (len(retailer) +  # Rule 1
                  ((len(request_params.get("items")) // 2) * 5))  # Rule 4

        if int(request_params.get("total").split(".")[1]) == 0:  # Rule 2
            points += 50

        if float(request_params.get("total")) * 4 == float(int(float(request_params.get("total")) * 4)):  # Rule 3
            points += 25

        for item in request_params.get("items"):  # Rule 5
            if len(item.get("shortDescription").strip()) % 3 == 0:
                points += math.ceil(float(item.get("price")) * 0.2)

        if int(request_params.get("purchase_date").split("-")[2]) % 2 != 0:  # Rule 6
            points += 6

        if 14 <= int(request_params.get("purchase_time").split(":")[0]) < 16:  # Rule 7
            points += 10

        return points
