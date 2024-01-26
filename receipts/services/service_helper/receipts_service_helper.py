from abc import ABC

from receipt_processor.services.base_service import BaseService


class ReceiptsServiceHelper(BaseService, ABC):

    def __init__(self):
        super().__init__()

    def set_status_code(self, *args, **kwargs):
        """
        This function will set the status code of the API in case of error.

        @params: *args
        @params: **kwargs
        """
        self.status_code = kwargs['status_code']
