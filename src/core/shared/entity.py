import abc
import datetime
from typing import List


class Entity(abc.ABC):

    def __init__(self, 
                 id_        : int = None,
                 created_at : datetime.date = None,
                 updated_at : datetime.datetime = None):
        self.id         = id_
        self.created_at = created_at
        self.updated_at = updated_at

    @abc.abstractmethod
    def validate_data(self) -> List[str]:
        """Validates the data that was entered
        """

