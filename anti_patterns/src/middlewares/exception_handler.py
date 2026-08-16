import traceback

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as exception:
            # REVIEW: Este format_exception pode não ser compátivel com versões mais novas do Python.
            # Sugestão: Utilize traceback.format_exc().
            trace = ''.join(traceback.format_exception(etype=type(exception), value=exception, tb=exception.__traceback__))
            # REVIEW: Não retorne erros internos para o cliente, retorne o trace internamente ou para um serviço de logs
            # para o cliente retorne um erro genérico com um id especifico.
            content_error = f'Exception: {exception} - StackTrace: {trace}'
            return JSONResponse(status_code=500, content=content_error)
