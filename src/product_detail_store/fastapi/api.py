import importlib
import pkgutil
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request

from product_detail_store import service_factory
from product_detail_store.fastapi.middlewares.hmac_authorizer import HMACAuthorizer
from product_detail_store.service_factory import ServiceFactory

app = FastAPI()
app.add_middleware(HMACAuthorizer)

service_factory.set_instance(
    ServiceFactory({
        "repositories": {
            "products": {
                "mocked": True
            }
        }
    })
)


@app.exception_handler(HTTPException)
def exception_handler(request: Request, exc: HTTPException):
    factory = service_factory.get_instance()
    exc_handler = factory.get_exception_handler()
    return exc_handler.handle_exception(request, exc)


def include_all_routers(fastapi: FastAPI, package: str):
    package_path = Path(__file__).parent / package
    for _, module_name, _ in pkgutil.iter_modules([str(package_path)]):
        module = importlib.import_module(
            f".{package}.{module_name}",
            "product_detail_store.fastapi"
        )
        if hasattr(module, "router"):
            fastapi.include_router(module.router)


include_all_routers(app, "endpoints")
