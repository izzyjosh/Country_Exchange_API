from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
import uvicorn
import os
from src.utils.database import Base
from src.utils.database import engine
from fastapi.exceptions import FastAPIError, RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHttpException

from src.responses.responses import ErrorResponse, ValidationErrorResponse
from src.responses.responses import success_response


app = FastAPI(
        title="Country, Currency & Exchange",
        description="Api to manage country current exchange rate and its GDP",
        )


Base.metadata.create_all(engine)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        errors.append({
            "field": error.get("loc")[-1],
            "message": error.get("msg")
        })

    is_query_param_error = any(
        err.get("loc")[0] == "query" for err in exc.errors()
    )

    is_missing_field = any(
        err.get("type") in ["value_error.missing", "missing"] for err in exc.errors()
    )

    if is_missing_field or is_query_param_error:
        response = ValidationErrorResponse(status_code=status.HTTP_400_BAD_REQUEST, errors=errors)
    else:
        response = ValidationErrorResponse(errors=errors)

    status_code = (
        status.HTTP_400_BAD_REQUEST
        if is_missing_field or is_query_param_error
        else status.HTTP_422_UNPROCESSABLE_ENTITY
    )

    return JSONResponse(content=response.model_dump(), status_code=status_code)


@app.exception_handler(StarletteHttpException)
async def starlette_http_handler(request: Request, exc: StarletteHttpException) -> JSONResponse:
    response: ErrorResponse = ErrorResponse(status_code=exc.status_code, message=exc.detail)
    return JSONResponse(content=response.model_dump(), status_code=exc.status_code)


@app.exception_handler(FastAPIError)
async def http_exception_handler(request: Request, exc: FastAPIError) -> JSONResponse:

    response: ErrorResponse = ErrorResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message="Internal Server Error")

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=response.model_dump())



@app.get("/")
async def welcome():
    return JSONResponse(status_code=200, content={"message": "welcome to my APi"})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get("PORT", 8000)), reload=True )

