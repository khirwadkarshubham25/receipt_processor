import sys
import traceback
from abc import ABC, abstractmethod

from receipt_processor.commons.generic_constants import GenericConstants


class BaseService(ABC):
    """ Applicable to all modules like, employer, employee and bank"""

    def __init__(self):
        self.error = False
        self.data = None
        self.status_code = None

    @abstractmethod
    def get_request_params(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_data(self, *args, **kwargs):
        pass

    @abstractmethod
    def set_status_code(self, *args, **kwargs):
        """ should be implement in child class if status code needs to set inside service """
        pass

    def execute_service(self, *args, **kwargs):
        try:
            self.data = self.get_data(*args, **kwargs)
        except:
            traceback.print_exc(file=sys.stdout)
            self.error = True
            self.data = GenericConstants.ERROR_MESSAGE
