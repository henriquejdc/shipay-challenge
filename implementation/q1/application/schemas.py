from pydantic import BaseModel, Field


class AddressValidationRequest(BaseModel):
    cnpj: str = Field(min_length=14)
    cep: str = Field(min_length=8)


class AddressValidationResponse(BaseModel):
    matched: bool
    cnpj_address: dict
    cep_address: dict

