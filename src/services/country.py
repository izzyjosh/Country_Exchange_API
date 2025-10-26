from datetime import datetime, timezone
from sqlalchemy import func, select, asc, desc
from sqlalchemy.orm import Session
from fastapi.exceptions import HTTPException
import httpx
from src.models.country_data import CountryData
from src.schemas.country import CountryResponseSchema, CountryQuery
from fastapi.encoders import jsonable_encoder
from fastapi import status
from fastapi.responses import FileResponse
import os
from PIL import Image, ImageDraw, ImageFont
import random

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
SUMMARY_PATH = os.path.join(CACHE_DIR, "summary.png")


class CountryService:

    @staticmethod
    def generate_summary_image(total_countries: int, top_five: list, last_updated: datetime):
        width, height = 600, 350
        bg_color = (240, 240, 255)
        text_color = (20, 20, 60)

        img = Image.new("RGB", (width, height), bg_color)
        draw = ImageDraw.Draw(img)

        # Load default font
        font = ImageFont.load_default()

        # Title
        draw.text((20, 20), "Country Summary Report", fill=text_color, font=font)

        # Total countries
        draw.text((20, 60), f"Total Countries: {total_countries}", fill=text_color, font=font)

        # Top 5 GDP
        draw.text((20, 100), "Top 5 by Estimated GDP:", fill=text_color, font=font)
        y_offset = 130
        for i, (name, gdp) in enumerate(top_five, start=1):
            draw.text((40, y_offset), f"{i}. {name}    {gdp:,}", fill=text_color, font=font)
            y_offset += 25

        # Last refreshed
        draw.text((20, y_offset + 20), f"Last Refreshed: {last_updated.strftime('%Y-%m-%d %H:%M:%SZ')}", fill=text_color, font=font)

        # Save to /cache/summary.png
        img.save(SUMMARY_PATH)


    
    @staticmethod
    async def refresh_countries(db: Session):


        #-------------------------------------
        # Fetch country data from external API
        #-------------------------------------
        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(30.0)) as client:

            # Fetch countries data
                countries_response = await client.get("https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies")

                if countries_response.status_code != 200:
                    raise HTTPException(status_code=countries_response.status_code, detail="Failed to fetch countries data")
                countries_data = countries_response.json()

                exchange_rates_response = await client.get("https://open.er-api.com/v6/latest/USD")
                if exchange_rates_response.status_code != 200:
                    raise HTTPException(status_code=exchange_rates_response.status_code, detail="Failed to fetch exchage rates")
                exchange_data = exchange_rates_response.json()
                exchange_rates = exchange_data.get("rates", {})

        except httpx.ReadTimeout:
            raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from external API - network error"})

        except httpx.RequestError as e:
            raise HTTPException(
            status_code=503,
            detail={
                "error": "External data source unavailable",
                "details": f"Could not fetch data from external API - network error"})


            # Clean countriee data
        total_stored = 0

        new_records = []
        update_mappings = [] 

        existing_countries = {
        c.name: c for c in db.scalars(select(CountryData)).all()}

        for c in countries_data:
            name = c.get("name")
            capital = c.get("capital")
            region = c.get("region")
            population = c.get("population")
            currencies = c.get("currencies", [])
            flag = c.get("flag")

            if not name or not population:
                continue

            if not currencies:
                currency_code = None
                exchange_rate = None
                estimated_gdp = 0


            else:
                first_currency = currencies[0]

                currency_code = first_currency.get("code") if first_currency else None

                exchange_rate = exchange_rates.get(currency_code)

                multiplier = random.randint(1000,2000)

                if exchange_rate:
                    estimated_gdp = int((population * multiplier) / exchange_rate)
                else:
                    estimated_gdp = 0


            if name not in existing_countries:
                new_records.append(CountryData(
                name=name,
                capital=capital,
                region=region,
                population=population,
                currency_code=currency_code,
                exchange_rate=exchange_rate,
                estimated_gdp=estimated_gdp,
                flag_url=flag
                ))
            else:
                existing = existing_countries[name]
                existing.capital = capital
                existing.region = region
                existing.population = population
                existing.currency_code = currency_code
                existing.exchange_rate = exchange_rate
                existing.flag_url = flag
                existing.estimated_gdp = estimated_gdp



            total_stored += 1

        db.bulk_save_objects(new_records)
        print(True)
        db.commit()
        print("complete insert")


        # Summary image prep
        total_stmt = select(func.count(CountryData.id))
        total_countries = db.scalars(total_stmt).first() or 0

        top5_stmt = (
            select(CountryData.name, CountryData.estimated_gdp)
            .order_by(desc(CountryData.estimated_gdp))
            .limit(5)
        )
        top_five = db.execute(top5_stmt).all()

        last_updated_stmt = select(func.max(CountryData.last_refreshed_at))
        last_updated_date = db.scalars(last_updated_stmt).first() or datetime.now()

        # ---- (3) Generate image ----
        CountryService.generate_summary_image(
            total_countries=total_countries,
            top_five=top_five,
            last_updated=last_updated_date
        )

        response = {
                    "message": "countries refreshed successfully",
                    "total_countries": total_stored,
                    "last_refreshed": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                }

        return jsonable_encoder(response)

        #-------------------------
        # End of Country API fetch
        #-------------------------



    async def fetch(self, query: CountryQuery, db: Session):

        stmt = select(CountryData)

        if query.region:
            stmt = stmt.where(CountryData.region == query.region)
        if query.currency:
            stmt = stmt.where(CountryData.currency_code == query.currency)

        if query.sort:
            if query.sort.lower() == "gdp_asc":
                stmt = stmt.order_by(asc(CountryData.estimated_gdp))
            elif query.sort.lower() == "gdp_desc":
                stmt = stmt.order_by(desc(CountryData.estimated_gdp))
            else:
                raise HTTPException(status_code=400, detail={"error": "Invalid value for sort"})


        datas = db.scalars(stmt).all()
        countries = [CountryResponseSchema.model_validate(country, from_attributes=True) for country in datas]

        return countries


    async def get_one(self, name: str, db: Session):
        country = db.scalars(select(CountryData).where(CountryData.name == name)).first()

        if not country:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Country not found"})

        return CountryResponseSchema.model_validate(country, from_attributes=True)


    async def delete_country(self, name: str, db: Session):
        country = db.scalars(select(CountryData).where(CountryData.name == name)).first()

        if not country:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Country not found"})

        db.delete(country)
        db.commit()


    async def status(self, db: Session):
        stmt = select(
                func.count(CountryData.id).label("total_countries"),
                func.max(CountryData.last_refreshed_at).label("last_updated_date")
                )
        result = db.execute(stmt).first()
        if not  result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Not found"})

        response = {
                "total_countries": result.total_countries,
                "last_refreshed_at": result.last_updated_date.strftime("%Y-%m-%dT%H:%M:%SZ")
                }

        return response


    async def image(self):
        if not os.path.exists(SUMMARY_PATH):
            raise HTTPException(status_code=404, detail={"error": "Summary image not found. Please refresh countries first."})
        return FileResponse(SUMMARY_PATH, media_type="image/png")



country_service = CountryService()
