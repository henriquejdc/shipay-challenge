from types import SimpleNamespace

from fastapi.testclient import TestClient

import application.app as app_module
import application.providers as providers_module
from application.retry import RetryPolicy
from application.services import AddressValidationService, CepResolverWithFallback


class FakeResponse:
    def __init__(self, status_code: int, payload: dict) -> None:
        self.status_code = status_code
        self._payload = payload

    def json(self) -> dict:
        return self._payload


class FakeAsyncClient:
    def __init__(self, responses: dict[str, FakeResponse], recorder: dict, **kwargs) -> None:
        self._responses = responses
        self._recorder = recorder
        self._kwargs = kwargs

    async def __aenter__(self):
        self._recorder.setdefault("init_kwargs", []).append(self._kwargs)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, url: str):
        self._recorder.setdefault("urls", []).append(url)
        if url not in self._responses:
            raise AssertionError(f"Unexpected URL: {url}")
        return self._responses[url]


def _build_http_client(monkeypatch, responses: dict[str, FakeResponse], recorder: dict):
    monkeypatch.setattr(
        providers_module,
        "httpx",
        SimpleNamespace(
            AsyncClient=lambda **kwargs: FakeAsyncClient(responses=responses, recorder=recorder, **kwargs)
        ),
    )


def _build_service():
    return AddressValidationService(
        company_provider=providers_module.HttpCompanyProvider(),
        cep_resolver=CepResolverWithFallback(
            primary=providers_module.ViaCepProvider(),
            secondary=providers_module.BrasilApiCepProvider(),
            retry_policy=RetryPolicy(attempts=1, base_delay_seconds=0),
        ),
    )


def test_api_returns_200_when_addresses_match(monkeypatch):
    monkeypatch.setattr(app_module.Settings, "API_TOKEN", "secret-token")

    responses = {
        "https://brasilapi.com.br/api/cnpj/v1/00924432000199": FakeResponse(
            200,
            {
                "uf": "SP",
                "municipio": "SAO PAULO",
                "logradouro": "RUA AA",
            },
        ),
        "https://viacep.com.br/ws/01001000/json/": FakeResponse(
            200,
            {
                "uf": "SP",
                "localidade": "São Paulo",
                "logradouro": "Rua AÁ",
            },
        ),
    }
    recorder = {}
    _build_http_client(monkeypatch, responses, recorder)
    monkeypatch.setattr(app_module, "service", _build_service())

    client = TestClient(app_module.app)

    response = client.post(
        "/v1/customers/address/validate",
        json={"cnpj": "00924432000199", "cep": "01001000"},
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 200
    assert response.json()["matched"] is True
    assert recorder["urls"] == [
        "https://brasilapi.com.br/api/cnpj/v1/00924432000199",
        "https://viacep.com.br/ws/01001000/json/",
    ]


def test_api_falls_back_when_primary_cep_provider_errors(monkeypatch):
    monkeypatch.setattr(app_module.Settings, "API_TOKEN", "secret-token")

    responses = {
        "https://brasilapi.com.br/api/cnpj/v1/00924432000199": FakeResponse(
            200,
            {
                "uf": "SP",
                "municipio": "Sao Paulo",
                "logradouro": "Rua A",
            },
        ),
        "https://viacep.com.br/ws/01001000/json/": FakeResponse(429, {"message": "Too Many Requests"}),
        "https://brasilapi.com.br/api/cep/v1/01001000": FakeResponse(
            200,
            {
                "state": "SP",
                "city": "São Paulo",
                "street": "Rua Á",
            },
        ),
    }
    recorder = {}
    _build_http_client(monkeypatch, responses, recorder)
    monkeypatch.setattr(app_module, "service", _build_service())

    client = TestClient(app_module.app)

    response = client.post(
        "/v1/customers/address/validate",
        json={"cnpj": "00924432000199", "cep": "01001000"},
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 200
    assert response.json()["matched"] is True
    assert recorder["urls"] == [
        "https://brasilapi.com.br/api/cnpj/v1/00924432000199",
        "https://viacep.com.br/ws/01001000/json/",
        "https://brasilapi.com.br/api/cep/v1/01001000",
    ]


def test_api_rejects_missing_token(monkeypatch):
    monkeypatch.setattr(app_module.Settings, "API_TOKEN", "secret-token")
    client = TestClient(app_module.app)

    response = client.post("/v1/customers/address/validate", json={"cnpj": "00924432000199", "cep": "01001000"})

    assert response.status_code == 401
