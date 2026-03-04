import time
import random
import requests

# The dummy node we created
NODE_ID = "node_alpha_01"

# The local API endpoint for your Agentic AI Core
API_URL = "http://127.0.0.1:8000/ingest-telemetry"

def generate_sensor_data(is_event=False):
    """Generates synthetic sensor data. Simulates an anomaly if is_event is True."""
    
    # Baseline: Normal, safe conditions
    radar_disp = random.uniform(0.0, 0.05)  
    imu_x = random.uniform(-0.02, 0.02)     
    imu_y = random.uniform(-0.02, 0.02)
    imu_z = random.uniform(9.78, 9.82)      
    moisture = random.uniform(20.0, 30.0)   
    
    # Anomaly: Heavy rain, ground shifting, severe vibrations
    if is_event:
        radar_disp = random.uniform(0.8, 3.5)   
        imu_x = random.uniform(-1.5, 1.5)       
        imu_y = random.uniform(-1.5, 1.5)
        imu_z = random.uniform(8.0, 11.0)
        moisture = random.uniform(75.0, 95.0)   
        
    return {
        "node_id": NODE_ID,
        "radar_displacement": round(radar_disp, 4),
        "imu_vibration_x": round(imu_x, 4),
        "imu_vibration_y": round(imu_y, 4),
        "imu_vibration_z": round(imu_z, 4),
        "soil_moisture": round(moisture, 2)
    }

if __name__ == "__main__":
    print(f"🚀 Starting IoT & Radar Simulation for {NODE_ID}...")
    print(f"📡 Sending data to AI Core at {API_URL}")
    print("Press Ctrl+C to stop.")
    
    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            
            # Every 10th reading, simulate a dangerous landslide event
            is_anomaly = (cycle_count % 10 == 0)
            data = generate_sensor_data(is_anomaly)
            
            try:
                # POST the data to the FastAPI server instead of Supabase directly
                response = requests.post(API_URL, json=data)
                
                if response.status_code == 200:
                    status = "🚨 ANOMALY SENT" if is_anomaly else "✅ Normal Data Sent"
                    print(f"[{status}] Radar: {data['radar_displacement']}mm | Moisture: {data['soil_moisture']}%")
                else:
                    print(f"⚠️ Error: AI Core returned status {response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print("❌ Connection Error: Is the FastAPI AI Core running? (uvicorn ai_core.main:app)")
            
            # Wait 3 seconds before the next reading
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user.")