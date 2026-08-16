import pytest
from fastapi import HTTPException
import httpx

import application.providers as providers_module
from application.domain import AddressData


class FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class FakeAsyncClient:
    def __init__(self, response: FakeResponse, recorder: dict, **kwargs) -> None:
        self._response = response
        self._recorder = recorder
        self._kwargs = kwargs

    async def __aenter__(self):
        self._recorder["init_kwargs"] = self._kwargs
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str):
        self._recorder["url"] = url
        return self._response


@pytest.mark.asyncio
async def test_http_company_provider_builds_address_and_sends_user_agent(monkeypatch):
    recorder = {}
    response = FakeResponse(
        200,
        {
            "uf": "SP",
            "municipio": "São Paulo",
            "logradouro": "Rua A",
        },
    )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response=response, recorder=recorder, **kwargs),
    )

    provider = providers_module.HttpCompanyProvider(base_url="https://example.test")
    result = await provider.get_address_by_cnpj("00924432000199")

    assert result == AddressData(state="SP", city="São Paulo", street="Rua A")
    assert recorder["url"] == "https://example.test/00924432000199"
    assert recorder["init_kwargs"]["headers"]["User-Agent"] == providers_module.Settings.USER_AGENT


@pytest.mark.asyncio
async def test_via_cep_provider_raises_when_rate_limited(monkeypatch):
    recorder = {}
    response = FakeResponse(429, {"message": "Too Many Requests"})

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response=response, recorder=recorder, **kwargs),
    )

    provider = providers_module.ViaCepProvider(base_url="https://viacep.com.br/ws")

    with pytest.raises(HTTPException) as exc_info:
        await provider.get_address_by_cep("01001000")

    assert exc_info.value.status_code == 502
    assert recorder["url"] == "https://viacep.com.br/ws/01001000/json/"


@pytest.mark.asyncio
async def test_brasil_api_provider_parses_address(monkeypatch):
    recorder = {}
    response = FakeResponse(
        200,
        {
            "state": "RJ",
            "city": "Rio de Janeiro",
            "street": "Rua B",
        },
    )

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: FakeAsyncClient(response=response, recorder=recorder, **kwargs),
    )

    provider = providers_module.BrasilApiCepProvider(base_url="https://brasilapi.com.br/api/cep/v1")
    result = await provider.get_address_by_cep("20040002")

    assert result == AddressData(state="RJ", city="Rio de Janeiro", street="Rua B")
    assert recorder["url"] == "https://brasilapi.com.br/api/cep/v1/20040002"
