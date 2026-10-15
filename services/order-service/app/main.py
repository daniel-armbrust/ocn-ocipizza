#
# main.py
#

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config.logging import configure_logging
from app.config.settings import settings

from app.clients.jwks_client import jwks_client

from app.exceptions.order_exceptions import (
    OrderCreationError,
    OrderIdempotencyConflictError,
    OrderNotFoundError,
    OrderQueryError,
    OrderUpdateError,
    OrderDeleteError
)

from app.routes.order_routes import router as order_router
from app.routes.order_admin_routes import router as order_admin_router

from app.responses.jsend import fail_response

configure_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tenta antecipar o carregamento das chaves públicas utilizadas
    # para validação dos tokens JWT.
    await jwks_client.warm_up()
    yield

app = FastAPI(
    title='OCI Pizza - Order Service API',
    version='1.0.0',
    lifespan=lifespan,
    docs_url='/docs' if settings.app_env == 'development' else None,
    redoc_url='/redoc' if settings.app_env == 'development' else None,
    openapi_url='/openapi.json' if settings.app_env == 'development' else None
)


@app.exception_handler(OrderIdempotencyConflictError)
async def order_idempotency_conflict_handler(
    request: Request,
    ex: OrderIdempotencyConflictError
) -> JSONResponse:
    """
    Converte a reutilização inválida de uma chave em HTTP 409.

    Args:
        request: Requisição de criação que originou o conflito.
        ex: Exceção contendo a falha de idempotência.

    Returns:
        Resposta JSend informando o conflito de idempotência.
    """

    logger.warning(
        'Idempotency conflict while processing %s %s',
        request.method,
        request.url.path
    )

    return fail_response(
        status_code=status.HTTP_409_CONFLICT,
        code='ORDER_SERVICE_IDEMPOTENCY_CONFLICT',
        message=str(ex)
    )


@app.exception_handler(OrderCreationError)
async def order_creation_error_handler(
    request: Request,
    ex: OrderCreationError
) -> JSONResponse:
    """
    Oculta detalhes internos de uma falha ao persistir o pedido.

    Args:
        request: Requisição de criação que não pôde ser concluída.
        ex: Exceção gerada pela camada de serviço.

    Returns:
        Resposta JSend genérica com HTTP 500.
    """

    logger.exception(
        'Order creation failed while processing %s %s',
        request.method,
        request.url.path
    )

    return fail_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code='ORDER_SERVICE_CREATION_ERROR',
        message='Unable to create order.'
    )


@app.exception_handler(OrderQueryError)
async def order_query_error_handler(
    request: Request,
    ex: OrderQueryError
) -> JSONResponse:
    """
    Oculta detalhes internos de uma falha durante a consulta de pedidos.

    Args:
        request: Requisição que não pôde ser processada.
        ex: Exceção gerada pela camada de serviço.

    Returns:
        Resposta JSend genérica com HTTP 500.
    """

    logger.exception(
        'Order query failed while processing %s %s',
        request.method,
        request.url.path
    )

    return fail_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code='ORDER_SERVICE_QUERY_ERROR',
        message='Unable to retrieve orders.'
    )


@app.exception_handler(OrderNotFoundError)
async def order_not_found_error_handler(
    request: Request,
    ex: OrderNotFoundError
) -> JSONResponse:
    """
    Converte a ausência de um pedido do usuário em HTTP 404.

    Args:
        request: Requisição que solicitou o pedido.
        ex: Exceção emitida quando o pedido não foi encontrado.

    Returns:
        Resposta JSend informando que o pedido não foi encontrado.
    """

    logger.warning(
        'Order not found while processing %s %s',
        request.method,
        request.url.path
    )

    return fail_response(
        status_code=status.HTTP_404_NOT_FOUND,
        code='ORDER_SERVICE_ORDER_NOT_FOUND',
        message=str(ex)
    )


@app.exception_handler(OrderUpdateError)
async def order_update_error_handler(
    request: Request,
    ex: OrderUpdateError
) -> JSONResponse:
    """
    Oculta detalhes internos de uma falha ao atualizar um pedido.

    Args:
        request: Requisição de atualização que não pôde ser concluída.
        ex: Exceção gerada pela camada de serviço.

    Returns:
        Resposta JSend genérica com HTTP 500.
    """

    logger.exception(
        'Order update failed while processing %s %s',
        request.method,
        request.url.path
    )

    return fail_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code='ORDER_SERVICE_UPDATE_ERROR',
        message='Unable to update order.'
    )


@app.exception_handler(OrderDeleteError)
async def order_delete_error_handler(
    request: Request,
    ex: OrderDeleteError
) -> JSONResponse:
    """
    Oculta detalhes internos de uma falha ao remover um pedido.

    Args:
        request: Requisição de remoção que não pôde ser concluída.
        ex: Exceção gerada pela camada de serviço.

    Returns:
        Resposta JSend genérica com HTTP 500.
    """

    logger.exception(
        'Order deletion failed while processing %s %s',
        request.method,
        request.url.path
    )

    return fail_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code='ORDER_SERVICE_DELETE_ERROR',
        message='Unable to delete order.'
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    ex: RequestValidationError
) -> JSONResponse:
    """
    Converte erros de validação do FastAPI para o padrão JSend fail.

    Args:
        request: Requisição HTTP que originou o erro de validação.
        exc: Exceção de validação emitida pelo FastAPI/Pydantic.

    Returns:
        Resposta JSON JSend `fail` com o primeiro erro de validação.
    """

    logger.exception(
        'Unexpected error while processing %s %s',
        request.method,
        request.url.path
    )

    error = ex.errors()[0]
    location = error.get('loc', [])
    field = str(location[-1]) if location else 'request'

    return fail_response(
        status_code=status.HTTP_400_BAD_REQUEST,
        code='ORDER_SERVICE_VALIDATION_ERROR',
        message=error.get('msg', 'Invalid request'),
        field=field
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    ex: HTTPException
) -> JSONResponse:
    """
    Converte exceções HTTP conhecidas para o padrão JSend fail.

    Args:
        request: Requisição HTTP que originou a exceção.
        exc: Exceção HTTP lançada por dependências, rotas ou serviços.

    Returns:
        Resposta JSON JSend `fail` preservando o status HTTP da exceção.
    """

    logger.warning(
        'HTTP error while processing %s %s: %s',
        request.method,
        request.url.path,
        ex.detail
    )

    if ex.status_code == status.HTTP_401_UNAUTHORIZED:
        code = 'ORDER_SERVICE_AUTHENTICATION_ERROR'
    elif ex.status_code == status.HTTP_403_FORBIDDEN:
        code = 'ORDER_SERVICE_AUTHORIZATION_ERROR'
    else:
        code = 'ORDER_SERVICE_HTTP_ERROR'

    return fail_response(
        status_code=ex.status_code,
        code=code,
        message=str(ex.detail)
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    ex: Exception
) -> JSONResponse:
    """
    Oculta detalhes de erros inesperados e retorna resposta JSend fail.

    Args:
        request: Requisição HTTP que originou a falha inesperada.
        exc: Exceção não tratada durante o processamento da requisição.

    Returns:
        Resposta JSON JSend `fail` genérica com HTTP 500.
    """

    logger.exception(
        'Unexpected error while processing %s %s',
        request.method,
        request.url.path
    )

    return fail_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code='ORDER_SERVICE_INTERNAL_SERVER_ERROR',
        message='Internal server error.'
    )


@app.get('/health')
def health_check() -> dict:
    """
    Retorna o estado básico de saúde do `order-service`.

    Returns:
        Dicionário JSend simples identificando o serviço ativo.
    """

    return {
        'status': 'success', 
        'data': {'service': 'order-service'}
    }


# Rotas responsáveis pela criação e consulta dos pedidos.
app.include_router(order_router)

# Rotas administrativas responsáveis pelo gerenciamento e
# acompanhamento dos pedidos.
app.include_router(order_admin_router)
