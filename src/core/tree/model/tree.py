import datetime
from typing import List
from src.core.shared.utils import date_to_string, datetime_to_string

from src.core.pruning import Pruning
from src.core.shared import Entity


class Tree(Entity):
    def __init__(
        self,
        id_: int = None,
        created_at: datetime.date = None,
        updated_at: datetime.datetime = None,
        created_by: str = None,
        especie: str = None,
        nome_comum: str = None,
        origem: str = None,
        altura: float = None,
        dap: float = None,
        fitossanidade: str = None,
        localizacao: str = None,
        latitude: float = None,
        longitude: float = None,
        podas: List[Pruning] = None,
        obs: str = None,
    ):
        super().__init__(id_, created_at, updated_at)

        self.created_by = created_by
        self.especie = especie
        self.nome_comum = nome_comum
        self.origem = origem
        self.altura = altura
        self.dap = dap
        self.fitossanidade = fitossanidade
        self.localizacao = localizacao
        self.podas = podas
        self.latitude = latitude
        self.longitude = longitude
        self.obs = obs

    def data_to_dataframe(self):
        return [
            {
                "id": self.id,
                "created_at": self.created_at,
                "updated_at": self.updated_at,
                "created_by": self.created_by,
                "especie": self.especie,
                "nome_comum": self.nome_comum,
                "origem": self.origem,
                "altura": self.altura,
                "dap": self.dap,
                "fitossanidade": self.fitossanidade,
                "localizacao": self.localizacao,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "obs": self.obs,
            }
        ]

    def data_to_redis(self):
        return {
            "id": self.id,
            "created_at": date_to_string(self.created_at),
            "updated_at": datetime_to_string(self.updated_at),
            "created_by": self.created_by,
            "especie": self.especie,
            "nome_comum": self.nome_comum,
            "origem": self.origem,
            "altura": self.altura,
            "dap": self.dap,
            "fitossanidade": self.fitossanidade,
            "localizacao": self.localizacao,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "obs": self.obs,
        }

    def __repr__(self):
        return (
            "Tree("
            f"id={self.id}, "
            f"created_at={self.created_at}, "
            f"updated_at={self.updated_at}, "
            f"created_by={self.created_by}, "
            f"especie={self.especie}, "
            f"nome_comum={self.nome_comum}, "
            f"origem={self.origem}, "
            f"altura={self.altura}, "
            f"dap={self.dap}, "
            f"fitossanidade={self.fitossanidade}, "
            f"localizacao={self.localizacao}, "
            f"latitude={self.latitude}, "
            f"longitude={self.longitude}, "
            f"podas={self.podas}, "
            f"obs={self.obs}"
            ")"
        )

    def validate_data(self) -> List[str]:
        return super().validate_data()
