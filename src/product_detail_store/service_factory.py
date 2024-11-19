from functools import lru_cache
from typing import Optional

from product_detail_store.fastapi.exception_handler import ExceptionHandler
from product_detail_store.repositories.in_memory.inmemory_product_repository import InMemoryProductRepository
from product_detail_store.repositories.in_memory.inmemory_user_repository import InMemoryUserRepository
from product_detail_store.services.interfaces.product_repository import ProductRepository
from product_detail_store.services.interfaces.user_repository import UserRepository

INSTANCE = None


class ServiceFactory:
    def __init__(self, config):
        self._config = config

        global INSTANCE
        INSTANCE = self

    @lru_cache
    def get_product_repository(self) -> ProductRepository:
        if self._get_config("repositories.products.mocked", True):
            return InMemoryProductRepository()

    def get_users_repository(self) -> UserRepository:
        if self._get_config("repositories.users.mocked", True):
            return InMemoryUserRepository(
                records=self._get_config("repositories.users.records", {})
            )

    def _get_config(self, path, default=None):
        d = self._config

        for segment in path.split("."):
            d = d.get(segment, {})

        return d or default

    @lru_cache
    def get_exception_handler(self):
        return ExceptionHandler()


def get_instance() -> Optional[ServiceFactory]:
    if INSTANCE is None:
        raise Exception(
            "ServiceFactory instance is not initialized. "
            "Use set_instance(ServiceFactory) to initialize it"
        )

    return INSTANCE


def set_instance(service_factory: ServiceFactory):
    global INSTANCE
    INSTANCE = service_factory
