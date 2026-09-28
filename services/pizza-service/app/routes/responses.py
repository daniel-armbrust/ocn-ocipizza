from fastapi.responses import JSONResponse


def fail_response(
    status_code: int,
    code: str,
    message: str,
    field: str = "request",
) -> JSONResponse:
    """Cria resposta JSend fail para violações de validação ou domínio."""

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "fail",
            "data": {
                "field": field,
                "code": code,
                "message": message,
            },
        },
    )


def error_response(status_code: int, message: str) -> JSONResponse:
    """Cria resposta JSend error para falhas de autenticação ou operação."""

    return JSONResponse(
        status_code=status_code,
        content={"status": "error", "message": message},
    )
