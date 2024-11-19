from abc import abstractmethod


class UserRepository:
    @abstractmethod
    async def get_password_for_user(self, user_id) -> str:
        pass
