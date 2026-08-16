from sqlalchemy import select
from sqlalchemy.orm import selectinload

from endpoints.registration.models import Customers
from infrastructure.repositories.sql_repository import SqlRepository


class RegistrationRepository(SqlRepository):
    model = Customers

    async def get_customer(self, params) -> bool:
        async with self.session_factory() as session:
            # REVIEW: O selectinload é para relacionamentos, não para colunas simples como id/name/email.
            result = await session.execute(select(self.model).filter_by(**params).options(
                selectinload(self.model.id).selectinload(Customers.id),
                selectinload(self.model.name).selectinload(Customers.name),
                selectinload(self.model.email).selectinload(Customers.email)))
            # REVIEW: A tipagem indica bool, mas o metodo retorna um objeto ou None.
            return result.scalars().first()
