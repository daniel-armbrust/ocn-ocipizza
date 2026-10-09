#
# main.py
#

import logging

from fastapi import Depends, FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import CSRFError, CSRFProtectMiddleware

from app.config.logging import configure_logging
from app.config.settings import settings

from app.dependencies.templates import templates
from app.dependencies.authentication import load_authentication_context

from app.routes import (
    pizza_routes,
    user_routes,
    user_auth_routes,
    cart_routes
)

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title='OCI Pizza - Frontend Service',
    version='1.0.0',
    dependencies=[Depends(load_authentication_context)],
    docs_url='/docs' if settings.app_env == 'development' else None,
    redoc_url='/redoc' if settings.app_env == 'development' else None,
    openapi_url='/openapi.json' if settings.app_env == 'development' else None
)

# Adiciona o suporte a sessões internas utilizadas pelo middleware
# de proteção CSRF.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret_key
)

# Adiciona proteção contra ataques CSRF.
app.add_middleware(
    CSRFProtectMiddleware,
    csrf_secret=settings.csrf_secret_key
)

# Disponibiliza os arquivos estáticos utilizados pelo frontend,
# incluindo JavaScript, CSS e imagens locais.
app.mount(
    '/static',
    StaticFiles(directory='app/static'),
    name='static'
)

@app.exception_handler(CSRFError)
async def csrf_error_handler(
    request: Request,
    ex: CSRFError
) -> RedirectResponse:
    """
    Redireciona requisições cujo token CSRF seja inválido ou tenha expirado.

    Args:
        request: Requisição HTTP que falhou na validação CSRF.
        ex: Exceção produzida pela proteção CSRF.

    Returns:
        Redirecionamento para a página inicial da aplicação.
    """

    return RedirectResponse(
        url='/',
        status_code=303
    )

@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    ex: Exception
) -> HTMLResponse:
    """
    Renderiza a página apresentada quando uma rota não é encontrada.

    Args:
        request: Requisição HTTP que tentou acessar a rota inexistente.
        ex: Exceção associada ao erro HTTP 404.

    Returns:
        Resposta HTML com a página de erro e status HTTP 404.
    """

    return templates.TemplateResponse(
        request=request,
        name='errors/404.html',
        status_code=404
    )

@app.exception_handler(Exception)
async def internal_error_handler(
    request: Request,
    ex: Exception
) -> HTMLResponse:
    """
    Renderiza uma resposta genérica para falhas inesperadas.

    Args:
        request: Requisição HTTP durante a qual ocorreu a falha.
        ex: Exceção inesperada capturada pela aplicação.

    Returns:
        Resposta HTML sem detalhes internos e com status HTTP 500.
    """

    logger.exception(
        'Unexpected error while processing %s %s',
        request.method,
        request.url.path
    )

    # Não inclui informações da exceção na página para evitar o vazamento
    # de detalhes internos da aplicação.
    return templates.TemplateResponse(
        request=request,
        name='errors/500.html',
        status_code=500
    )

@app.get('/', include_in_schema=False)
def root(request: Request) -> RedirectResponse:
    """
    Redireciona a raiz da aplicação para o catálogo de pizzas.

    Args:
        request: Requisição utilizada para resolver a URL nomeada da rota.

    Returns:
        Redirecionamento temporário para a página do catálogo.
    """

    return RedirectResponse(
        url=request.url_for('list_all_pizzas'),
        status_code=307
    )

# Rotas responsáveis pelo cadastro e gerenciamento dos usuários.
app.include_router(user_routes.router)

# Rotas responsáveis pelos fluxos de autenticação dos usuários.
app.include_router(user_auth_routes.router)

# Rotas responsáveis pela consulta e interação com as pizzas.
app.include_router(pizza_routes.router)

# Rotas responsáveis pelo gerenciamento do carrinho de compras.
app.include_router(cart_routes.router)
