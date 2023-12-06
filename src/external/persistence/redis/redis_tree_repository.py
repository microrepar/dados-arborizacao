import datetime
import json
from typing import List

import redis

from config import Config
from src.core.shared.utils import string_to_date, string_to_datetime
from src.core.tree import Tree, TreeRepository
from src.external.persistence import repository_map


@repository_map
class RedisArvoreRepository(TreeRepository):
    def __init__(self):
        self.r = redis.Redis(
            host             = Config.REDIS_HOST,
            port             = Config.REDIS_PORT,
            password         = Config.REDIS_PASSWORD,
            decode_responses = True,
        )

    def registry(self, entity: Tree) -> Tree:
        hash_main = entity.__class__.__name__

        # Get a id sequence to tree
        entity.id = self.get_tree_id_sequence()
        entity.created_at = datetime.datetime.now().date()

        tree_dict = entity.data_to_redis()

        new_tree = json.dumps(tree_dict)

        # Register the new tree in redis
        is_inserted = self.r.hsetnx(hash_main, entity.id, new_tree)

        # Checks if a tree was inserted
        if not is_inserted:
            raise Exception(
                f'The tree id={entity.id} already exist. Chose other id and try again!'
            )

        return entity
    
    def update(self, entity: Tree) -> Tree:
        return super().update(entity)
    
    def remove(self, entity: Tree) -> bool:
        return super().remove(entity)
    
    def find_by_field(self, entity: Tree) -> List[Tree]:
        return super().find_by_field(entity)
    
    def get_by_id(self, entity: Tree) -> Tree:
        return super().get_by_id(entity)
    
    def get_all(self, entity: Tree) -> List[Tree]:
        resp = self.r.hgetall(entity.__class__.__name__)

        tree_list = []

        for key, value in resp.items():
            data = json.loads(value)

            tree_list.append(
                Tree(
                    id_           = data.get('id'),
                    created_at    = string_to_date(data.get('created_at')),
                    updated_at    = data.get('updated_at'),
                    especie       = data.get('especie'),
                    created_by    = data.get('created_by'),
                    nome_comum    = data.get('nome_comum'),
                    origem        = data.get('origem'),
                    altura        = data.get('altura'),
                    dap           = data.get('dap'),
                    fitossanidade = data.get('fitossanidade'),
                    localizacao   = data.get('localizacao'),
                    latitude      = data.get('latitude'),
                    longitude     = data.get('longitude'),
                    podas         = data.get('podas'),
                    obs           = data.get('obs'),
                )
            )
        
        return list(sorted(tree_list, key=lambda x: x.id))
    
    def get_tree_id_sequence(self):
        key_sequence = "tree_id_sequence"
        if not self.r.exists(key_sequence):
            self.r.set(key_sequence, 0)
        new_id = self.r.incr(key_sequence)
        return new_id
