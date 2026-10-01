#
# main.py
#

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.user_routes import router as user_router
from app.routes.user_password_routes import router as user_password_router
# from app.routes.email_routes import router as email_router
# from app.routes.jwks_routes import router as jwks_router
# from app.routes.login_routes import router as login_router


app = FastAPI(
    title='OCI Pizza - User Service API',
    version='1.0.0'
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, ex: RequestValidationError) -> JSONResponse:
    """
    Converte erros de validação do FastAPI para o padrão JSend fail.

    Args:
        request: Requisição HTTP que originou o erro de validação.
        exc: Exceção de validação emitida pelo FastAPI/Pydantic.

    Returns:
        Resposta JSON JSend `fail` com o primeiro erro de validação.
    """

    error = ex.errors()[0]
    location = error.get('loc', [])
    field = str(location[-1]) if location else 'request'

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'status': 'fail',
            'data': {
                'field': field,
                'code': 'VALIDATION_ERROR',
                'message': error.get('msg', 'Invalid request')
            },
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, ex: HTTPException) -> JSONResponse:
    """
    Converte exceções HTTP conhecidas para o padrão JSend error.

    Args:
        request: Requisição HTTP que originou a exceção.
        exc: Exceção HTTP lançada por dependências, rotas ou serviços.

    Returns:
        Resposta JSON JSend `error` preservando o status HTTP da exceção.
    """

    return JSONResponse(
        status_code=ex.status_code,
        content={'status': 'error', 'message': str(ex.detail)}
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(request: Request, ex: Exception) -> JSONResponse:
    """
    Oculta detalhes de erros inesperados e retorna resposta JSend error.

    Args:
        request: Requisição HTTP que originou a falha inesperada.
        exc: Exceção não tratada durante o processamento da requisição.

    Returns:
        Resposta JSON JSend `error` genérica com HTTP 500.
    """

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'status': 'error', 'message': 'Internal server error'}
    )


@app.get("/health")
def health_check() -> dict:
    """
    Retorna o estado básico de saúde do `user-service`.

    Returns:
        Dicionário JSend simples identificando o serviço ativo.
    """

    return {'status': 'success', 'data': {'service': 'user-service'}}


# Rotas de cadastro, consulta, atualização e desativação de usuários.
app.include_router(user_router)

# Rotas para operações relacionadas as senhas dos usuários.
app.include_router(user_password_router)

# # Rotas de autenticação e gerenciamento de sessão.
# app.include_router(login_router)

# # Rotas de confirmação e reenvio de confirmação de e-mail.
# app.include_router(email_router)

# # Rota de publicação das chaves públicas para validação de JWT.
# app.include_router(jwks_router)
