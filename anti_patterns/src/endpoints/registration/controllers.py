from fastapi import APIRouter, Depends, FastAPI, Request
from dependency_injector.wiring import inject, Provide

from infrastructure.containers import Container
from endpoints.registration.manager import Orchestrator

router = APIRouter()


@router.get('/registration/customers')
@inject
async def get_customers(request: Request, orchestrator: Orchestrator = Depends(Provide[Container.registration_service]),):
    # REVIEW: Esta rota não declara path param "identity"; Tende a quebrar com KeyError.
    customer_id = request.path_params['identity'].get('customer_id')
    # REVIEW: O provider configurado injeta RegistrationService, mas o parâmetro
    # da rota está tipado como Orchestrator. Verifique se o tipo e o provider estão corretos.
    return await orchestrator.find_customer_by_id(customer_id=customer_id)


def configure(app: FastAPI):
    app.include_router(router)
