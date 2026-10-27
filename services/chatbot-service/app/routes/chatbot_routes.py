#
# routes/chatbot_routes.py
#

from uuid import UUID

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.services.chat_service import ChatService, get_chat_service

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import success_response


router = APIRouter()

#
# POST: /chat/messages
#
@router.post(
    '/messages',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
async def send_message(
    request: ChatMessageRequest,
    user_id: UUID | None = Depends(get_optional_current_user_id),
    service: ChatService = Depends(get_chat_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Processa uma mensagem enviada pelo usuário ao chatbot.

    Args:
        request: Mensagem enviada pelo usuário para processamento.
        user_id: Identificador do usuário autenticado ou None quando
            não houver autenticação.
        service: Serviço responsável pela detecção de intenção,
            consulta aos microsserviços e geração da resposta.

    Returns:
        Resposta contendo a mensagem gerada pelo chatbot e a
        intenção identificada.
    """

    # Processa a mensagem e obtém a resposta gerada pelo chatbot.
    chat_response = await service.process_message(
        message=request.message,
        user_id=user_id
    )

    # Retorna a resposta e a intenção identificada no formato JSend.
    return success_response({
        'reply': chat_response.reply
    })

