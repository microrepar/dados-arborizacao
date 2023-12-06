from typing import Protocol, runtime_checkable

from src.core.shared import Repository


@runtime_checkable
class PruningRepository(Repository, Protocol):...