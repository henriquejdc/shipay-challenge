from .domain import AddressData
from .ports import CepProvider, CompanyProvider
from .retry import RetryPolicy


class CepResolverWithFallback:
    def __init__(self, primary: CepProvider, secondary: CepProvider, retry_policy: RetryPolicy) -> None:
        self._primary = primary
        self._secondary = secondary
        self._retry_policy = retry_policy

    async def resolve(self, cep: str) -> AddressData:
        try:
            return await self._retry_policy.run(lambda: self._primary.get_address_by_cep(cep))
        except Exception:
            return await self._retry_policy.run(lambda: self._secondary.get_address_by_cep(cep))


class AddressValidationService:
    def __init__(self, company_provider: CompanyProvider, cep_resolver: CepResolverWithFallback) -> None:
        self._company_provider = company_provider
        self._cep_resolver = cep_resolver

    async def validate(self, cnpj: str, cep: str) -> tuple[bool, AddressData, AddressData]:
        cnpj_address = await self._company_provider.get_address_by_cnpj(cnpj)
        cep_address = await self._cep_resolver.resolve(cep)
        matched = cnpj_address.normalized() == cep_address.normalized()
        return matched, cnpj_address, cep_address

