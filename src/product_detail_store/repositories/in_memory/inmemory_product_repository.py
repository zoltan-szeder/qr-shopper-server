from typing import Optional

from product_detail_store.models.product import Product
from product_detail_store.services.interfaces.product_repository import ProductRepository


class InMemoryProductRepository(ProductRepository):
    def __init__(self):
        self._products_by_barcode = {}

    async def add_product(self, product: Product):
        self._products_by_barcode[product.id] = product

    async def get_by_barcode(self, barcode: str) -> Optional[Product]:
        return self._products_by_barcode.get(barcode)

    def clear(self):
        self._products_by_barcode = {}