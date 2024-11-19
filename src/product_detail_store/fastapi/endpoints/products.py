from fastapi import APIRouter, HTTPException

from product_detail_store import service_factory
from product_detail_store.models.product import Product

router = APIRouter()


@router.get("/products/{barcode}")
async def get_product(barcode: str, response_model=Product):
    factory = service_factory.get_instance()
    product_repository = factory.get_product_repository()
    product = await product_repository.get_by_barcode(barcode)
    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Could not find product with barcode \"{barcode}\""
        )

    return product
