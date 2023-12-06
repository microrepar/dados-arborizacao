
import datetime
from typing import List

from src.core.shared import Entity


class Pruning(Entity):
    def __init__(self, 
                 id_        : int = None,
                 created_at : datetime.date = None,
                 updated_at : datetime.datetime = None,
                 data       : str = None,
                 tipo       : str = None,
                 resp       : str = None):
        
        super().__init__(id_, created_at, updated_at)
        
        self.data = data
        self.tipo = tipo
        self.resp = resp

    def data_to_dataframe(self):
        return{}

    def validate_data(self) -> List[str]:
        return super().validate_data()