from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routes.pizza_routes import router as pizza_router

app = FastAPI(
    title="OCI Pizza - Pizza Service API",
    version="1.0.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    error = exc.errors()[0]
    location = error.get("loc", [])
    field = str(location[-1]) if location else "request"

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "fail",
            "data": {
                "field": field,
                "code": "VALIDATION_ERROR",
                "message": error.get("msg", "Invalid request"),
            },
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    if isinstance(exc.detail, dict):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.detail["message"]},
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": str(exc.detail)},
    )


@app.exception_handler(Exception)
async def unexpected_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"status": "error", "message": "Internal server error"},
    )


@app.get("/health")
def health_check() -> dict:
    return {"status": "success", "data": {"service": "pizza-service"}}


app.include_router(pizza_router)
