#
# main.py
#

import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config.logging import configure_logging
from app.config.settings import settings

from app.routes.pizza_routes import router as pizza_router

from app.responses.jsend import fail_response

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title='OCI Pizza - Pizza Service API',
    version='1.0.0',
    docs_url='/docs' if settings.app_env == 'development' else None,
    redoc_url='/redoc' if settings.app_env == 'development' else None,
    openapi_url='/openapi.json' if settings.app_env == 'development' else None
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, 
    ex: RequestValidationError) -> JSONResponse:
    """
    Converte erros de validação do FastAPI para o padrão JSend fail.

    Args:
        request: Requisição HTTP que originou o erro de validação.
        exc: Exceção de validação emitida pelo FastAPI/Pydantic.

    Returns:
        Resposta JSON JSend `fail` com o primeiro erro de validação.
    """

    logger.error(
        'Unexpected error while processing %s %s',
        request.method,
        request.url.path,
        exc_info=ex
    )

    error = ex.errors()[0]
    location = error.get('loc', [])
    field = str(location[-1]) if location else 'request'

    return fail_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code='PIZZA_VALIDATION_ERROR',
        message=error.get('msg', 'Invalid request'),
        field=field
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request, 
    ex: HTTPException) -> JSONResponse:
    """
    Converte exceções HTTP conhecidas para o padrão JSend fail.

    Args:
        request: Requisição HTTP que originou a exceção.
        exc: Exceção HTTP lançada por dependências, rotas ou serviços.

    Returns:
        Resposta JSON JSend `fail` preservando o status HTTP da exceção.
    """

    logger.error(
        'Unexpected error while processing %s %s',
        request.method,
        request.url.path,
        exc_info=ex
    )

    return fail_response(
        status_code=ex.status_code,
        code='PIZZA_HTTP_ERROR',
        message=str(ex.detail),
        headers=ex.headers
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request, 
    ex: Exception) -> JSONResponse:
    """
    Oculta detalhes de erros inesperados e retorna resposta JSend fail.

    Args:
        request: Requisição HTTP que originou a falha inesperada.
        exc: Exceção não tratada durante o processamento da requisição.

    Returns:
        Resposta JSON JSend `fail` genérica com HTTP 500.
    """

    logger.error(
        'Unexpected error while processing %s %s',
        request.method,
        request.url.path,
        exc_info=ex
    )

    return fail_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code='PIZZA_INTERNAL_SERVER_ERROR',
        message='Internal server error.'
    )


@app.get('/health')
def health_check() -> dict:
    """
    Retorna o estado básico de saúde do `pizza-service`.

    Returns:
        Dicionário JSend simples identificando o serviço ativo.
    """

    return {'status': 'success', 'data': {'service': 'pizza-service'}}


app.include_router(pizza_router)
