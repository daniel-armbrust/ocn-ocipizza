#
# schemas/chat.py
#

from pydantic import BaseModel, Field, ConfigDict


class ChatMessageRequest(BaseModel):
    """
    Representa uma mensagem enviada pelo usuário ao chatbot.

    Attributes:
        message: Mensagem ou pergunta enviada pelo usuário para
            processamento pelo chatbot.
    """
    
    model_config = ConfigDict(str_strip_whitespace=True)

    message: str = Field(min_length=1, max_length=2000)


class ChatMessageResponse(BaseModel):
    """
    Representa a resposta produzida pelo chatbot após o 
    processamento da mensagem.

    Attributes:
        reply: Resposta gerada pelo provedor configurado para 
            geração de respostas.
        intent: Intenção identificada pelo provedor de 
            classificação de intenção.
    """

    reply: str
    intent: str