from typing import List, Optional
from datetime import date, datetime
from enum import Enum
import random
from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import SQLModel, Field, Session, create_engine, select

# --- Enums ---
class CropType(str, Enum):
    MAIZE = "Maize"
    RICE = "Rice"
    CASSAVA = "Cassava"

# --- Data Models ---
class Farm(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    owner_name: str
    crop_type: CropType
    location_lat: float
    location_long: float
    planting_date: date

class WeatherLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    farm_id: int = Field(foreign_key="farm.id")
    temp: float
    rainfall_mm: float
    humidity: float
    date: datetime = Field(default_factory=datetime.now)

# --- Database Setup ---
sqlite_file_name = "agri_database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# --- Logic Engine (The Brain) ---
class AgriBrain:
    @staticmethod
    def analyze(weather: dict, farm: Farm) -> List[str]:
        advice = []
        crop = farm.crop_type
        
        # Extract weather data for easier access
        rain = weather.get('rainfall_mm', 0)
        temp = weather.get('temp', 0)
        humidity = weather.get('humidity', 0)

        # General Advice
        advice.append(f"Analyzing for {crop.value} at {farm.owner_name}...")

        # Specific Agronomic Rules
        if crop == CropType.MAIZE:
            if rain > 20:
                advice.append("🔴 ALERT: Heavy rain (>20mm) detected. Do NOT apply fertilizer today to avoid wash-off.")
            if temp > 28 and humidity < 50:
                advice.append("⚠️ WARNING: High risk of Fall Armyworm. Conditions (Temp > 28°C, Humidity < 50%) are favorable. Scout field immediately.")
        
        elif crop == CropType.RICE:
            if humidity > 80:
                advice.append("⚠️ WARNING: High humidity (>80%) detected. High risk of Rice Blast disease. Monitor crop closely.")

        elif crop == CropType.CASSAVA:
            if rain > 50:
                advice.append("🔴 ALERT: Excessive rainfall (>50mm). Risk of root rot and waterlogging. Ensure drainage channels are clear.")

        if len(advice) == 1: # Only the initial message was added
            advice.append("🟢 Conditions look normal. No specific alerts.")
            
        return advice

# --- Mock Data Generator ---
def seed_data(session: Session):
    # Check if data exists to avoid duplicates if run multiple times
    existing_farms = session.exec(select(Farm)).first()
    if existing_farms:
        return {"message": "Data already seeded."}

    farms = [
        Farm(owner_name="Musa Farms", crop_type=CropType.MAIZE, location_lat=12.0022, location_long=8.5920, planting_date=date(2023, 5, 15)), # Kano
        Farm(owner_name="Chinedu Agro", crop_type=CropType.RICE, location_lat=6.4584, location_long=7.5464, planting_date=date(2023, 6, 1)), # Enugu
        Farm(owner_name="Yoruba Cassava Co", crop_type=CropType.CASSAVA, location_lat=7.3775, location_long=3.9470, planting_date=date(2023, 4, 10)), # Ibadan
        Farm(owner_name="Biu Maize Enterprise", crop_type=CropType.MAIZE, location_lat=10.6129, location_long=12.1946, planting_date=date(2023, 5, 20)), # Borno
        Farm(owner_name="Delta Rice Fields", crop_type=CropType.RICE, location_lat=5.5544, location_long=5.7932, planting_date=date(2023, 6, 10)), # Warri
    ]

    for farm in farms:
        session.add(farm)
    
    session.commit()
    return {"message": "Seeded 5 Nigerian farms successfully."}

# --- FastAPI App ---
app = FastAPI(title="Agri-Tech Climate Intelligence API")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

@app.post("/farms/", response_model=Farm)
def create_farm(farm: Farm, session: Session = Depends(get_session)):
    session.add(farm)
    session.commit()
    session.refresh(farm)
    return farm

@app.post("/seed/")
def seed_database(session: Session = Depends(get_session)):
    return seed_data(session)

@app.get("/advice/{farm_id}")
def get_farm_advice(farm_id: int, session: Session = Depends(get_session)):
    farm = session.get(Farm, farm_id)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    # Simulate live weather API
    current_weather = {
        "temp": round(random.uniform(20, 35), 1),
        "rainfall_mm": round(random.uniform(0, 60), 1),
        "humidity": round(random.uniform(30, 90), 1)
    }

    # Generate advice
    alerts = AgriBrain.analyze(current_weather, farm)

    return {
        "farm": farm.owner_name,
        "crop": farm.crop_type,
        "current_weather": current_weather,
        "advice": alerts
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
