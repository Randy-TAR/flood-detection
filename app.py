import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from datetime import datetime
from flood_predictor2 import predict_flood_from_weather
from weather_utils import get_weather_data

latest_results = []

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
                        f"{row['city']} ({row['time_label']}): "
                        f"({row['weather_id']}) {row['weather_desc']} — "
                        f"{row['rain_mm']}mm — {row['temp']}°C | "
                        f"{row['risk_predict']} (prob={row['flood_prob']:.2f})"
                    )

        except Exception as e:
            print(f"❌ Error during flood check: {e}")

        await asyncio.sleep(1800)  # every 30 minutes


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

app = FastAPI(title="Flood Detection", version="1.0", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "🌧️ Flood Detection API is running"}

@app.get("/flood_prediction")
async def flood_prediction():
    # Return latest weather + flood info
    results = latest_results
    flood_cities = [r for r in results if r["flood_pred"] == 1]
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_cities_checked": len(results),
        "flood_risk_cities": len(flood_cities),
        "details": results  # includes weather info + flood prediction + risk_predict
    }
