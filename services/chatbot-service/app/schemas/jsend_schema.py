#
# schemas/jsend_schema.py
#

from typing import Any

from pydantic import BaseModel


class JSendSuccessResponse(BaseModel):
    """
    Representa uma resposta de sucesso no padrão JSend.

    O padrão JSend encapsula os dados retornados pela API dentro
    do atributo `data` e utiliza o campo `status` para indicar
    o resultado da operação.

    Attributes:
        status: Status da operação. Para respostas de sucesso,
            sempre possui o valor `success`.

        data: Dados retornados pela operação.
    """

    status: str = 'success'
    data: Any


class JSendFailResponse(BaseModel):
    """
    Representa uma resposta de falha no padrão JSend.

    Utilizado para erros de validação, regras de negócio ou falhas
    esperadas da aplicação.

    Attributes:
        status: Status da operação. Para falhas, sempre possui o 
            valor `fail`.
            
        data: Informações relacionadas ao erro.
    """

    status: str = 'fail'
    data: dict