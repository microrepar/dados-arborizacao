from src.core import usecase_map
from src.core.shared import UseCase
from src.core.shared.application import Result
from src.core.tree import Tree

from .tree_repository import TreeRepository

@usecase_map('/tree/registry')
class TreeRegistry(UseCase):
    def __init__(self, repository: TreeRepository):
        self.repository = repository

    def execute(self, entity: Tree) -> Result:
        result = Result()

        result.error_msg = entity.validate_data()

        if result.qty_msg() > 0:
            return result

        try:
            new_tree = self.repository.registry(entity)
            result.entities = new_tree
            result.success_msg = f'Registred tree {new_tree} successfully'
            return result
        except Exception as error:
            result.error_msg = f'TreeRegistry error: {error}'
            return result