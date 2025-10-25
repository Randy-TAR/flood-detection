import pandas as pd
import joblib

# --- Load trained model once ---
model = joblib.load("flood_rf_model.joblib")
print("✅ Flood model loaded successfully!")

def predict_flood_from_weather(weather_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame with columns:
    ['city', 'rain_mm', 'temp', 'weather_id', 'weather_desc', 'time_label']
    
    Returns a DataFrame with flood predictions and risk description.
    """
    if weather_df.empty:
        return pd.DataFrame()  # no data

    # --- Convert rainfall into features ---
    weather_df["rfh"] = weather_df["rain_mm"] * 20
    weather_df["r1h"] = weather_df["rain_mm"] * 15
    weather_df["r3h"] = weather_df["rain_mm"] * 10
    weather_df["rfq"] = weather_df["rain_mm"] * 5
    weather_df["r1q"] = weather_df["rain_mm"] * 3
    weather_df["r3q"] = weather_df["rain_mm"] * 2

    features = ['rfh','r1h','r3h','rfq','r1q','r3q']

    # --- Predict ---
    weather_df["flood_pred"] = model.predict(weather_df[features])
    weather_df["flood_prob"] = model.predict_proba(weather_df[features])[:,1].round(2)
    
    # --- Add human-readable risk column ---
    weather_df["risk_predict"] = weather_df["flood_pred"].apply(
        lambda x: "⚠️ FLOOD RISK" if x == 1 else "✅ Safe"
    )

    # --- For console display: city info + risk in one line ---
    for _, row in weather_df.iterrows():
        print(f"{row['city']} ({row['time_label']}): ({row['weather_id']}) {row['weather_desc']} — {row['rain_mm']}mm — {row['temp']}°C | {row['risk_predict']} (prob={row['flood_prob']})")

    return weather_df

