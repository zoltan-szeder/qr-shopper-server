import asyncio
import base64
import hmac
import http.client
from datetime import UTC, datetime
from random import randint
from threading import Thread
from time import sleep
from unittest import TestCase
import requests

import uvicorn

from product_detail_store.models.product import Product
from product_detail_store.repositories.in_memory.inmemory_product_repository import InMemoryProductRepository
from product_detail_store import service_factory
from product_detail_store.service_factory import ServiceFactory


class MyTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.PORT = 9090
        cls.HOST = "127.0.0.1"
        cls.CONFIG = uvicorn.Config(
            "product_detail_store.fastapi.api:app",
            host=cls.HOST,
            port=cls.PORT,
            # log_level=logging.DEBUG
        )
        cls.UVICORN = uvicorn.Server(cls.CONFIG)

        cls.APP_THREAD = Thread(target=cls.UVICORN.run)
        cls.APP_THREAD.start()

        while not cls.UVICORN.started:
            sleep(0.1)

    @classmethod
    def tearDownClass(cls):
        cls.UVICORN.should_exit = True
        cls.APP_THREAD.join()

    def setUp(self):
        self._bearer_token = "password"
        self.service_factory = ServiceFactory({
            "repositories": {
                "products": {
                    "mocked": True
                },
                "users": {
                    "mocked": True,
                    "records": {
                        "test-user": {
                            "password": "mock"
                        }
                    }
                }
            },
            "auth": {
                "type": "bearer_simple",
                "secret": self._bearer_token
            }
        })
        service_factory.set_instance(self.service_factory)
        self._repository: InMemoryProductRepository = self.service_factory.get_product_repository()

    def tearDown(self):
        self._repository.clear()

    def test_get_product_mocked_repo(self):
        product = Product(
            id=str(self._get_random_barcode()),
            name="Product 1",
            price=randint(10000, 99999) / 100,
            currency="USD"
        )
        asyncio.run(self._repository.add_product(product))

        response = self._get_product_by_barcode(product.id)

        self.assertEqual(http.client.OK, response.status_code)
        self.assertEqual(
            {
                "id": product.id,
                "name": product.name,
                "price": product.price,
                "currency": product.currency
            },
            response.json()
        )

    def test_get_missing_product(self):
        barcode = self._get_random_barcode()
        response = self._get_product_by_barcode(str(barcode))

        self.assertEqual(http.client.NOT_FOUND, response.status_code)
        self.assertEqual(
            {
                "message": f"Could not find product with barcode \"{barcode}\"",
                "errors": {
                    "location": f"/products/{barcode}",
                    "message": f"Could not find product with barcode \"{barcode}\"",
                },
                "code": 404
            },
            response.json()
        )

    def _get_product_by_barcode(self, barcode):
        now = int(datetime.now(tz=UTC).timestamp())
        return requests.get(
            f"http://{self.HOST}:{self.PORT}/products/{barcode}",
            headers={
                "Authorization-Time": str(now),
                "Authorization-User": "test-user",
                "Authorization": f"HMAC {self.sign_request(now, barcode)}"
            }
        )

    def sign_request(self, now, barcode):
        msg = (
                f"GET /products/{barcode}\n" +
                f"Authorization-Time: {now}\n" +
                f"Authorization-User: test-user"
        )
        hmac_signature = hmac.digest(
            b"mock",
            msg.encode(),
            "sha-256"
        )
        return base64.b64encode(hmac_signature).decode()

    def _get_random_barcode(self):
        return randint(1000000000000, 9999999999999)
