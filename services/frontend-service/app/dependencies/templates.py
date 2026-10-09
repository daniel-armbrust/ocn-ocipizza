#
# dependencies/templates.py
#

from fastapi.templating import Jinja2Templates
from starlette_wtf import csrf_token

templates = Jinja2Templates(
    directory='app/templates'
)

# Permite que os formulários renderizados pelo Jinja gerem o token assinado
# esperado pelo decorador `csrf_protect`.
templates.env.globals['csrf_token'] = csrf_token
