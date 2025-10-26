from pydantic import BaseModel
from fastapi import status
from typing import Optional
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse


class ValidationErrorResponse(BaseModel):
    status_code: int = status.HTTP_422_UNPROCESSABLE_CONTENT
    message: str = "Validation Error"
    errors: list 

class ErrorResponse(BaseModel):
    status_code: int = status.HTTP_400_BAD_REQUEST
    message: str


def success_response(status_code: int = status.HTTP_200_OK, data: Optional[dict | list] = None) -> JSONResponse:

    response = {}

    if data is not None:
        response = data

    return JSONResponse(status_code=status_code, content=jsonable_encoder(response))
