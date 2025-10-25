import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from flood_predictor2 import predict_flood_from_weather
from weather_utils import get_weather_data,get_weather_data_by_city

latest_results = []


# 🔁 Scheduled background flood check
async def scheduled_flood_check():
    global latest_results
    while True:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n🕒 Weather check at {now_str}")
        try:
            # 1️⃣ Get live weather
            rain_data = get_weather_data()  # DataFrame with weather info

            if rain_data.empty:
                print("🌤️ No rainfall detected anywhere.")
            else:
                # 2️⃣ Predict flood
                results_df = predict_flood_from_weather(rain_data)

                # 3️⃣ Merge weather info + flood predictions
                merged_df = rain_data.copy()
                merged_df["flood_pred"] = results_df["flood_pred"]
                merged_df["flood_prob"] = results_df["flood_prob"]
                merged_df["risk_predict"] = merged_df["flood_pred"].apply(
                    lambda x: "⚠️ FLOOD RISK" if x == 1 else "✅ Safe"
                )

                # 4️⃣ Keep only relevant columns for console & API
                columns_to_keep = [
                    "city", "weather_id", "weather_desc",
                    "rain_mm", "temp", "flood_pred", "flood_prob", "risk_predict"
                ]
                latest_results = merged_df[columns_to_keep].to_dict(orient="records")

                # 5️⃣ Console output
                for row in latest_results:
                    print(
                        f"{row['city']}: "
                        f"({row['weather_id']}) {row['weather_desc']} — "
                        f"{row['rain_mm']}mm — {row['temp']}°C | "
                        f"{row['risk_predict']} (prob={row['flood_prob']:.2f})"
                    )

        except Exception as e:
            print(f"❌ Error during flood check: {e}")

        await asyncio.sleep(1800)  # every 30 minutes


# 🌍 Application lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🌍 Starting Flood Monitoring Service...")
    task = asyncio.create_task(scheduled_flood_check())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    print("🛑 Flood Monitoring Service Stopped.")


# 🚀 Initialize FastAPI app
app = FastAPI(title="Flood Detection API", version="1.0", lifespan=lifespan)

# 🌐 Enable CORS
origins = [
    "*",  # Allow all for now — replace with your frontend URLs in production
    # Example:
    # "https://yourfrontend.onrender.com",
    # "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 📍 API Endpoints
@app.get("/")
async def root():
    return {"message": "🌧️ Flood Detection API is running"}


@app.get("/flood_prediction")
async def flood_prediction():
    results = latest_results
    flood_cities = [r for r in results if r["flood_pred"] == 1]
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_cities_checked": len(results),
        "flood_risk_cities": len(flood_cities),
        "details": results,  # weather info + flood prediction + risk_predict
    }

@app.post("/flood_prediction/{city_name}")
async def flood_prediction_by_city(city_name: str):
    data = get_weather_data_by_city(city_name)
    if "error" in data:
        return data

    results = predict_flood_from_weather(pd.DataFrame([data]))
    data["flood_pred"] = int(results["flood_pred"][0])
    data["flood_prob"] = float(results["flood_prob"][0])
    data["risk_predict"] = "⚠️ FLOOD RISK" if data["flood_pred"] == 1 else "✅ Safe"

    return data
