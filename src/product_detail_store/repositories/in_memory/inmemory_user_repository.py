from product_detail_store.services.interfaces.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self, records):
        self._records = records

    async def get_password_for_user(self, user_id) -> str:
        return self._records.get(user_id, {}).get("password")
