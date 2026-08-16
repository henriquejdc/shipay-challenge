import httpx
from fastapi import HTTPException

from .domain import AddressData
from .ports import CepProvider, CompanyProvider
from .settings import Settings


class HttpCompanyProvider(CompanyProvider):
    def __init__(
        self,
        base_url: str = Settings.COMPANY_API_BASE_URL,
        timeout_seconds: float = Settings.COMPANY_API_TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._headers = {"User-Agent": Settings.USER_AGENT}

    async def get_address_by_cnpj(self, cnpj: str) -> AddressData:
        async with httpx.AsyncClient(timeout=self._timeout_seconds, headers=self._headers) as client:
            response = await client.get(f"{self._base_url}/{cnpj}")
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="cnpj provider unavailable")

            payload = response.json()
            street = ""
            if payload.get("descricao_tipo_de_logradouro"):
                street = payload["descricao_tipo_de_logradouro"] + " "

            return AddressData(
                state=payload["uf"],
                city=payload["municipio"],
                street=street + payload.get("logradouro", ""),
            )


class ViaCepProvider(CepProvider):
    def __init__(
        self,
        base_url: str = Settings.CEP_PRIMARY_BASE_URL,
        timeout_seconds: float = Settings.CEP_API_TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._headers = {"User-Agent": Settings.USER_AGENT}

    async def get_address_by_cep(self, cep: str) -> AddressData:
        async with httpx.AsyncClient(timeout=self._timeout_seconds, headers=self._headers) as client:
            response = await client.get(f"{self._base_url}/{cep}/json/")
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="primary cep provider unavailable")
            payload = response.json()
            if payload.get("erro"):
                raise HTTPException(status_code=404, detail="cep not found")
            return AddressData(
                state=payload["uf"],
                city=payload["localidade"],
                street=payload["logradouro"],
            )


class BrasilApiCepProvider(CepProvider):
    def __init__(
        self,
        base_url: str = Settings.CEP_SECONDARY_BASE_URL,
        timeout_seconds: float = Settings.CEP_API_TIMEOUT_SECONDS,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._headers = {"User-Agent": Settings.USER_AGENT}

    async def get_address_by_cep(self, cep: str) -> AddressData:
        async with httpx.AsyncClient(timeout=self._timeout_seconds, headers=self._headers) as client:
            response = await client.get(f"{self._base_url}/{cep}")
            if response.status_code != 200:
                raise HTTPException(status_code=502, detail="secondary cep provider unavailable")
            payload = response.json()
            return AddressData(
                state=payload["state"],
                city=payload["city"],
                street=payload["street"],
            )
