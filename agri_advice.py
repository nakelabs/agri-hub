def generate_agri_advice(weather_data, crop_stage):
    """
    weather_data: dict containing temp, rain_forecast_mm, humidity
    crop_stage: string ('planting', 'growing', 'harvesting')
    """
    advice = []
    
    # 1. Fertilizer Logic
    if crop_stage == 'growing':
        if weather_data['rain_forecast_mm'] > 20:
            advice.append("🔴 DO NOT apply fertilizer. Heavy rain (>20mm) will wash it away.")
        elif weather_data['rain_forecast_mm'] < 5 and weather_data['soil_moisture'] > 40:
            advice.append("🟢 Good conditions to apply NPK fertilizer today.")

    # 2. Pest Logic (Example: Fall Armyworm thrives in dry/warm spells)
    if weather_data['temp'] > 28 and weather_data['humidity'] < 50:
        advice.append("⚠️ ALERT: High risk of Armyworm. Scout your field this evening.")

    # 3. Harvest Logic
    if crop_stage == 'harvesting':
        if weather_data['rain_forecast_mm'] > 10:
            advice.append("🔴 Rush harvest! Rain expected. Cover harvested crops immediately.")
        else:
            advice.append("🟢 Weather is clear for drying crops.")

    return advice

# Example Usage
current_weather = {
    'temp': 30,
    'rain_forecast_mm': 25,
    'humidity': 45,
    'soil_moisture': 60
}

print(generate_agri_advice(current_weather, 'growing'))
