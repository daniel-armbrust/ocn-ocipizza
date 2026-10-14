#
# main.py
#

import logging

import httpx

from fastapi import Depends, FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from starlette.middleware.sessions import SessionMiddleware
from starlette_wtf import CSRFError, CSRFProtectMiddleware

from app.config.logging import configure_logging
from app.config.settings import settings

from app.dependencies.templates import templates
from app.exceptions.auth_exceptions import AuthenticationRequiredError

from app.routes.auth_routes import router as auth_router


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title='OCI Pizza - Admin Service',
    version='1.0.0',
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

@app.exception_handler(AuthenticationRequiredError)
async def authentication_required_handler(
    request: Request,
    ex: AuthenticationRequiredError
) -> RedirectResponse:
    """
    Redireciona visitantes sem sessão válida para a página de autenticação.

    Args:
        request: Requisição feita a uma página protegida.
        ex: Exceção que indica a ausência de uma sessão autenticada.

    Returns:
        Redirecionamento para o login com o código da mensagem correspondente.
    """

    return RedirectResponse(
        url='/admin/login?code=USER_LOGIN_REQUIRED',
        status_code=status.HTTP_303_SEE_OTHER
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
        url='/admin/login',
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.exception_handler(status.HTTP_405_METHOD_NOT_ALLOWED)
async def method_not_allowed_handler(
    request: Request,
    ex: Exception
) -> RedirectResponse:
    """
    Redireciona para a página inicial quando o método HTTP não é aceito.

    Args:
        request: Requisição realizada com um método não permitido.
        ex: Exceção associada ao erro HTTP 405.

    Returns:
        Redirecionamento para a página inicial da aplicação.
    """

    return RedirectResponse(
        url='/admin/login',
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.exception_handler(httpx.HTTPStatusError)
async def upstream_http_error_handler(
    request: Request,
    ex: httpx.HTTPStatusError
) -> Response:
    """
    Trata respostas HTTP de erro devolvidas pelos microserviços.

    Args:
        request: Requisição processada pelo frontend-service.
        ex: Erro contendo a resposta recebida do microserviço.

    Returns:
        Redirecionamento para o login quando a autenticação for rejeitada
        ou página HTML de erro de gateway para as demais respostas.
    """

    if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
        return RedirectResponse(
            url='/admin/login?code=USER_LOGIN_REQUIRED',
            status_code=status.HTTP_303_SEE_OTHER
        )

    logger.warning(
        'Upstream HTTP error while processing %s %s: %s returned %s',
        request.method,
        request.url.path,
        ex.request.url,
        ex.response.status_code
    )

    # Repetir automaticamente uma requisição POST poderia duplicar uma
    # operação. Por isso, somente requisições GET recebem a própria URL
    # como destino para uma nova tentativa.
    retry_url = request.url.path if request.method == 'GET' else '/'

    return templates.TemplateResponse(
        request=request,
        name='errors/502.html',
        context={'retry_url': retry_url},
        status_code=status.HTTP_502_BAD_GATEWAY
    )

@app.exception_handler(httpx.RequestError)
async def upstream_unavailable_handler(
    request: Request,
    ex: httpx.RequestError
) -> HTMLResponse:
    """
    Trata falhas de rede durante a comunicação com os microserviços.

    Args:
        request: Requisição processada pelo frontend-service.
        ex: Falha de comunicação produzida pelo cliente HTTP.

    Returns:
        Página HTML informando a indisponibilidade temporária do serviço.
    """

    logger.exception(
        'Upstream service unavailable while processing %s %s',
        request.method,
        request.url.path
    )

    retry_url = request.url.path if request.method == 'GET' else '/'

    return templates.TemplateResponse(
        request=request,
        name='errors/503.html',
        context={'retry_url': retry_url},
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE
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
        url='/admin/login',
        status_code=status.HTTP_303_SEE_OTHER
    )

@app.get('/health')
def health_check() -> dict:
    """
    Retorna o estado básico de saúde do `frontend-service`.

    Returns:
        Dicionário JSend simples identificando o serviço ativo.
    """

    return {
        'status': 'success', 
        'data': {'service': 'frontend-service'}
    }

# Rotas responsáveis pelos fluxos de autenticação dos usuários.
app.include_router(auth_router)