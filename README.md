# 🌍 Country Information API

A **FastAPI** application that fetches, analyzes, and stores information about countries across the world. The API provides detailed data such as name, capital, region, population, currency, and estimated GDP. It also supports filtering, searching, and summary visualization.

---

## ✨ Features

- Fetch and store country data from an external API  
- Retrieve a list of all countries with filtering options  
- Get detailed information about a single country  
- Automatically estimate each country’s GDP using exchange rates  
- Generate a visual summary image showing global stats  
- Efficient database management with SQLAlchemy  
- Handles edge cases such as missing or invalid country fields  

---

## 🧠 Country Data Properties

Each stored country record includes:

| Field | Description |
|--------|--------------|
| **id** | Unique identifier for the country |
| **name** | Official country name |
| **capital** | Capital city of the country |
| **region** | Geographical region (e.g., Africa, Europe) |
| **population** | Total population |
| **currency_code** | ISO code of the primary currency |
| **exchange_rate** | Exchange rate against the US dollar |
| **estimated_gdp** | Computed GDP estimate using exchange rate and population |
| **flag** | URL to the country’s flag image |

---

## 🧰 Tech Stack

- **Python 3.12+**
- **FastAPI** — Web framework
- **Uvicorn** — ASGI server
- **SQLAlchemy** — ORM for database management
- **Requests** — For external API calls
- **Pillow** — For image generation

---

## 📦 Setup Instructions

Follow these steps to set up and run the project locally.

### 1. Clone the Repository
```bash
git clone https://github.com/izzyjosh/country_api.git
cd country_api
```
### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate 
```
### 3. Install Dependendies
```
pip install -r requirements.txt
```
### 4. Setup Database
- create a .env file and replace where necessary with your data
```
DATABASE_URL=mysql+pymysql://username:password@localhost:port/country_db
```
### 5. Run the project
```
uvicorn main:app --reload
```
