from fastapi import Depends, FastAPI, HTTPException

from .auth import require_token
from .providers import BrasilApiCepProvider, HttpCompanyProvider, ViaCepProvider
from .retry import RetryPolicy
from .schemas import AddressValidationRequest, AddressValidationResponse
from .services import AddressValidationService, CepResolverWithFallback
from .settings import Settings

app = FastAPI(title="Customer validation service")

service = AddressValidationService(
    company_provider=HttpCompanyProvider(),  # type: ignore[arg-type]
    cep_resolver=CepResolverWithFallback(
        primary=ViaCepProvider(),  # type: ignore[arg-type]
        secondary=BrasilApiCepProvider(),  # type: ignore[arg-type]
        retry_policy=RetryPolicy(
            attempts=Settings.RETRY_ATTEMPTS,
            base_delay_seconds=Settings.RETRY_BASE_DELAY_SECONDS,
        ),
    ),
)


@app.post("/v1/customers/address/validate", response_model=AddressValidationResponse)
async def validate_customer_address(
    payload: AddressValidationRequest,
    _: None = Depends(require_token),
):
    matched, cnpj_address, cep_address = await service.validate(payload.cnpj, payload.cep)

    if matched:
        return AddressValidationResponse(
            matched=True,
            cnpj_address={
                "uf": cnpj_address.state,
                "city": cnpj_address.city,
                "street": cnpj_address.street,
            },
            cep_address={
                "uf": cep_address.state,
                "city": cep_address.city,
                "street": cep_address.street,
            },
        )

    raise HTTPException(
        status_code=404,
        detail={
            "matched": False,
            "cnpj_address": {
                "uf": cnpj_address.state,
                "city": cnpj_address.city,
                "street": cnpj_address.street,
            },
            "cep_address": {
                "uf": cep_address.state,
                "city": cep_address.city,
                "street": cep_address.street,
            },
        },
    )
