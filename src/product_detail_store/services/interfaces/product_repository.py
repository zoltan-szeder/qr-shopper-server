from abc import abstractmethod
from typing import Optional

from product_detail_store.models.product import Product


class ProductRepository:
    @abstractmethod
    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        pass

    @abstractmethod
    async def add_product(self, product: Product):
        pass
