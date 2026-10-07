#
# dependencies/templates.py
#

from fastapi.templating import Jinja2Templates
from starlette_wtf import csrf_token

from app.config.settings import settings

templates = Jinja2Templates(
    directory='app/templates'
)

# Disponibiliza ao layout somente o nome do cookie opaco da sessão.
# Tokens e demais dados de autenticação permanecem inacessíveis ao template.
templates.env.globals['session_cookie_name'] = settings.session_cookie_name

# Permite que os formulários renderizados pelo Jinja gerem o token assinado
# esperado pelo decorador `csrf_protect`.
templates.env.globals['csrf_token'] = csrf_token
