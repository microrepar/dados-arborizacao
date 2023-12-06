from typing import List

from src.core.pruning import Pruning, PruningRepository


class RedisPruningRepository(PruningRepository):

    def registry(self, entity: Pruning) -> Pruning:
        return super().registry(entity)
    
    def update(self, entity: Pruning) -> Pruning:
        return super().update(entity)
    
    def remove(self, entity: Pruning) -> bool:
        return super().remove(entity)
    
    def find_by_field(self, entity: Pruning) -> List[Pruning]:
        return super().find_by_field(entity)
    
    def get_by_id(self, entity: Pruning) -> Pruning:
        return super().get_by_id(entity)
    
    def get_all(self, entity: Pruning) -> List[Pruning]:
        return super().get_all(entity)