from typing import Generic
from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared import UseCase, Repository, Entity

from src.core.tree import Tree, TreeRepository

@usecase_map('/tree/get_especies')
class TreeGetESpecies(UseCase):
    def __init__(self, repository: TreeRepository):
        self.repository = repository

    def execute(self, entity: Tree) -> Result:
        result = Result()

        try:
            tree_list = self.repository.get_all(entity)
            if not tree_list:
                result.info_msg = 'There are no registred trees'
            result.entities = tree_list
            result.objects = set([t.especie for t in tree_list])
        except Exception as error:
            result.error_msg = f'TreeGetEspecie error: {error}'
            return result

        return result