#
# responses/jsend.py
#

from fastapi.responses import JSONResponse

# Padrão JSEND:
#   https://github.com/omniti-labs/jsend

from app.schemas.jsend_schema import JSendSuccessResponse


def success_response(data: dict) -> JSendSuccessResponse:
    """
    Cria uma resposta de sucesso no padrão JSend.

    Esta função encapsula os dados retornados pela API dentro
    do atributo `data` e define o status da resposta como `success`.

    Args:
        data: Dados retornados pela operação realizada.

    Returns:
        Resposta estruturada no padrão JSend.
    """

    return JSendSuccessResponse(
        data=data
    )


def fail_response(
    status_code: int,
    code: str,
    message: str,
    field: str | None = None
) -> JSONResponse:
    """
    Cria uma resposta HTTP no formato JSend para falhas de validação ou regras de negócio.

    O campo `field` é opcional e somente será incluído na resposta quando a falha estiver associada a um campo específico da requisição.

    Args:
        status_code: Código HTTP que será retornado pela API.
        code: Código interno utilizado para identificar o tipo da falha.
        message: Mensagem descritiva apresentada ao consumidor da API.
        field: Nome do campo relacionado à falha, quando aplicável.

    Returns:
        Resposta HTTP no formato JSend contendo os detalhes da falha.
    """

    # Estrutura principal dos dados retornados em caso de falha.
    data = {
        'code': code,
        'message': message
    }

    # Inclui o campo somente quando a falha estiver associada
    # a uma propriedade específica da requisição.
    if field is not None:
        data['field'] = field

    # Retorna a resposta HTTP utilizando o formato JSend.
    return JSONResponse(
        status_code=status_code,
        content={
            'status': 'fail',
            'data': data
        }
    )