# Q1 — Validação de endereço por CNPJ + CEP

## O que foi implementado
Foi criada uma API FastAPI em `application/app.py` com o endpoint:

- `POST /v1/customers/address/validate`

O fluxo implementado:
1. Recebe `cnpj` e `cep`.
2. Consulta o endereço da empresa por CNPJ (`HttpCompanyProvider`).
3. Consulta CEP usando provedor primário (`ViaCepProvider`) com retentativas.
4. Em falha do primário, aplica fallback para provedor secundário (`BrasilApiCepProvider`), também com retentativas.
5. Normaliza e compara `UF`, `cidade` e `logradouro`.
6. Retorna:
   - `200` quando os dados coincidem.
   - `404` quando não coincidem, incluindo os dois endereços para rastreabilidade.

## Organização por responsabilidade
- `app/schemas.py`: contratos de entrada e saída da API.
- `app/domain.py`: modelo de domínio (`AddressData`) e normalização de comparação.
- `app/ports.py`: contratos (Protocols) para provedores externos.
- `app/providers.py`: adapters HTTP para CNPJ e CEP.
- `app/retry.py`: política de retentativa reutilizável.
- `app/services.py`: regra de negócio (orquestração, fallback e comparação).
- `app/settings.py`: variáveis de ambiente e valores padrão.
- `app/app.py`: composição da aplicação e rota HTTP.

## Requisitos
- `requirements.txt`: `fastapi`, `httpx`, `pydantic`, `uvicorn`.
- **Python recomendado:** 3.11+

## Instalação e execução
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn application.app:app --reload
```

## Variáveis de ambiente
- `CUSTOMER_VALIDATION_API_TOKEN`
- `CUSTOMER_VALIDATION_COMPANY_API_BASE_URL`
- `CUSTOMER_VALIDATION_COMPANY_API_TIMEOUT_SECONDS`
- `CUSTOMER_VALIDATION_CEP_PRIMARY_BASE_URL`
- `CUSTOMER_VALIDATION_CEP_SECONDARY_BASE_URL`
- `CUSTOMER_VALIDATION_CEP_API_TIMEOUT_SECONDS`
- `CUSTOMER_VALIDATION_RETRY_ATTEMPTS`
- `CUSTOMER_VALIDATION_RETRY_BASE_DELAY_SECONDS`

Exemplo:
```bash
export CUSTOMER_VALIDATION_API_TOKEN="token-fixo-da-api"
export CUSTOMER_VALIDATION_COMPANY_API_BASE_URL="https://brasilapi.com.br/api/cnpj/v1"
export CUSTOMER_VALIDATION_CEP_PRIMARY_BASE_URL="https://viacep.com.br/ws"
export CUSTOMER_VALIDATION_CEP_SECONDARY_BASE_URL="https://brasilapi.com.br/api/cep/v1"
```

## Autenticação
- O token é fixo e deve ser definido em `CUSTOMER_VALIDATION_API_TOKEN`.
- Caso definido um token envie o header `Authorization: Bearer <token>`.

## Escolhas técnicas e por quê
- **Separação por camadas**: reduz acoplamento e facilita manutenção/testes.
- **Adapter (providers)**: padroniza integração com APIs de terceiros.
- **Strategy/Fallback** no resolvedor de CEP: permite trocar provedores sem alterar a regra principal.
- **Retry com backoff exponencial**: melhora resiliência em falhas transitórias.
- **Normalização de endereço no domínio**: evita comparação frágil por caixa/espaços.

## Testes
- `app/tests/unit/test_providers.py`
- `app/tests/unit/test_retry.py`
- `app/tests/unit/test_services.py`
- `app/tests/api/test_customer_validation_api.py`

```bash
pytest
```

## Exemplos de uso (curl)

### Validação com endereços correspondentes
```bash
curl -X POST http://localhost:8000/v1/customers/address/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token-fixo-da-api" \
  -d '{
    "cnpj": "00924432000199",
    "cep": "01001000"
  }'
```

### Validação com endereços divergentes
```bash
curl -X POST http://localhost:8000/v1/customers/address/validate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token-fixo-da-api" \
  -d '{
    "cnpj": "00924432000199",
    "cep": "20040020"
  }'
```

### Sem token (erro 401)
```bash
curl -X POST http://localhost:8000/v1/customers/address/validate \
  -H "Content-Type: application/json" \
  -d '{
    "cnpj": "00924432000199",
    "cep": "01001000"
  }'
```

## Decisões de design
- A resposta traz os dois endereços para facilitar auditoria funcional.
- Erros de provedores externos retornam como indisponibilidade de dependência (`502`).
- O endpoint permanece síncrono, conforme requisito do challenge.
