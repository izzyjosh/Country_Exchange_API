from typing import Annotated
from fastapi import APIRouter, Depends, Query
from fastapi import status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from src.utils.database import get_db
from src.services.country import country_service
from src.responses.responses import success_response
from src.schemas.country import CountryQuery


country = APIRouter()

@country.post("/countries/refresh")
async def countries_refresh(db: Annotated[Session, Depends(get_db)]):

    result = await country_service.refresh_countries(db=db)
    return success_response(status_code=201, data=result)

@country.get("/countries")
async def filter(query: Annotated[CountryQuery, Query()], db: Annotated[Session, Depends(get_db)]):

    result = await country_service.fetch(query=query, db=db)
    return success_response(data=result)

@country.get("/countries/image")
async def get_summary_image():
    result = await country_service.image()
    return result

@country.get("/countries/{name}")
async def get_one(name: str, db: Annotated[Session, Depends(get_db)]):
    result = await country_service.get_one(name=name, db=db)

    return success_response(data=result)


@country.delete("/countries/{name}", status_code=204)
async def delete_country(name: str, db: Annotated[Session, Depends(get_db)]):
    await country_service.delete_country(name=name, db=db)


@country.get("/status")
async def status(db: Annotated[Session, Depends(get_db)]):

    result = await country_service.status(db=db)

    return success_response(data=result)
