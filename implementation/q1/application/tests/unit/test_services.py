import pytest

from application.domain import AddressData
from application.retry import RetryPolicy
from application.services import AddressValidationService, CepResolverWithFallback


class FakeCompanyProvider:
    async def get_address_by_cnpj(self, cnpj: str) -> AddressData:
        return AddressData(state="SP", city="Sao Paulo", street="Rua Sao Paulo")


class FakeCepProvider:
    def __init__(self, address: AddressData) -> None:
        self._address = address

    async def get_address_by_cep(self, cep: str) -> AddressData:
        return self._address


@pytest.mark.asyncio
async def test_address_validation_service_matches_normalized_addresses():
    company = FakeCompanyProvider()
    cep = FakeCepProvider(AddressData(state="sp", city="são paulo", street="rua são páulo"))
    resolver = CepResolverWithFallback(
        primary=cep,
        secondary=cep,
        retry_policy=RetryPolicy(attempts=1, base_delay_seconds=0)
    )
    service = AddressValidationService(company_provider=company, cep_resolver=resolver)

    matched, cnpj_address, cep_address = await service.validate("123", "456")

    assert matched is True
    assert cnpj_address.state == "SP"
    assert cep_address.street == "rua são páulo"
    assert cnpj_address.street == "Rua Sao Paulo"
