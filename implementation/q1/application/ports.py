from typing import Protocol

from .domain import AddressData


class CompanyProvider(Protocol):
    async def get_address_by_cnpj(self, cnpj: str) -> AddressData:
        ...


class CepProvider(Protocol):
    async def get_address_by_cep(self, cep: str) -> AddressData:
        ...

