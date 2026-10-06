#
# main.py
#

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config.logging import configure_logging
from app.config.settings import settings

from app.dependencies.templates import templates
from app.routes import pizza_routes, user_routes

configure_logging()
is_development = settings.app_env == 'development'

app = FastAPI(
    title='OCI Pizza - Frontend Service',
    version='1.0.0',
    docs_url='/docs' if is_development else None,
    redoc_url='/redoc' if is_development else None,
    openapi_url='/openapi.json' if is_development else None
)

# Disponibiliza os arquivos estáticos utilizados pelo frontend,
# incluindo JavaScript, CSS e imagens locais.
app.mount(
    '/static',
    StaticFiles(directory='app/static'),
    name='static'
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

app.include_router(pizza_routes.router)
app.include_router(user_routes.router)
