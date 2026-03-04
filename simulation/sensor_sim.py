import os
import time
import random
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Load environment variables securely
load_dotenv()
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

if not url or not key:
    raise ValueError("Missing Supabase URL or Key. Check your .env file.")

# 2. Initialize Supabase client
supabase: Client = create_client(url, key)

# The dummy node we created in the database earlier
NODE_ID = "node_alpha_01"

def generate_sensor_data(is_event=False):
    """Generates synthetic sensor data. Simulates an anomaly if is_event is True."""
    
    # Baseline: Normal, safe conditions
    radar_disp = random.uniform(0.0, 0.05)  # mmWave micro-displacement (0 to 0.05 mm)
    imu_x = random.uniform(-0.02, 0.02)     # Negligible vibration
    imu_y = random.uniform(-0.02, 0.02)
    imu_z = random.uniform(9.78, 9.82)      # Baseline gravity pull
    moisture = random.uniform(20.0, 30.0)   # Dry/normal soil
    
    # Anomaly: Heavy rain, ground shifting, severe vibrations
    if is_event:
        radar_disp = random.uniform(0.8, 3.5)   # Dangerous ground shift detected by Radar
        imu_x = random.uniform(-1.5, 1.5)       # Heavy tremor/vibration
        imu_y = random.uniform(-1.5, 1.5)
        imu_z = random.uniform(8.0, 11.0)
        moisture = random.uniform(75.0, 95.0)   # Highly saturated soil (monsoon simulation)
        
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
    print("Press Ctrl+C to stop.")
    
    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            
            # Every 10th reading, simulate a dangerous landslide event to test the AI later
            is_anomaly = (cycle_count % 10 == 0)
            
            data = generate_sensor_data(is_anomaly)
            
            # Push data to Supabase
            response = supabase.table("telemetry_data").insert(data).execute()
            
            # Print to terminal so we can watch it work
            status = "🚨 DANGER/ANOMALY" if is_anomaly else "✅ Normal"
            print(f"[{status}] Radar: {data['radar_displacement']}mm | Moisture: {data['soil_moisture']}%")
            
            # Wait 3 seconds before the next reading
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n🛑 Simulation stopped by user.")