import os
import random
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client

# 1. Setup and Configurations
load_dotenv()
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
app = FastAPI(title="Agentic AI Landslide Command Center")

# Allow Next.js frontend to communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Data Models
class SensorData(BaseModel):
    node_id: str
    radar_displacement: float
    imu_vibration_x: float
    imu_vibration_y: float
    imu_vibration_z: float
    soil_moisture: float

# 3. The AI Agents
def sentinel_agent(data: SensorData) -> dict:
    reasoning = "Sentinel Analysis: "
    anomaly_score = 0
    if data.radar_displacement > 0.5:
        anomaly_score += 2
        reasoning += f"High radar displacement ({data.radar_displacement}mm). "
    else:
        reasoning += "Radar normal. "
    if abs(data.imu_vibration_x) > 0.5 or abs(data.imu_vibration_y) > 0.5:
        anomaly_score += 1
        reasoning += "Tremors detected. "
    return {"score": anomaly_score, "reasoning": reasoning}

def analyst_agent(data: SensorData, sentinel_finding: dict) -> dict:
    reasoning = sentinel_finding["reasoning"] + "\nAnalyst Context: "
    risk_multiplier = 1.0
    if data.soil_moisture > 60.0:
        risk_multiplier = 1.5
        reasoning += f"Soil is highly saturated ({data.soil_moisture}%). Risk elevated. "
    else:
        reasoning += "Soil moisture is stable. "
    final_score = sentinel_finding["score"] * risk_multiplier
    return {"final_score": final_score, "reasoning": reasoning}

def commander_agent(data: SensorData, analyst_finding: dict):
    score = analyst_finding["final_score"]
    reasoning = analyst_finding["reasoning"] + "\nCommander Decision: "
    severity = "Normal"
    if score >= 3.0:
        severity = "Danger"
        reasoning += "CRITICAL EVENT CONFIRMED. Triggering Immediate Alert."
    elif score >= 1.0:
        severity = "Warning"
        reasoning += "Moderate anomaly detected. Monitoring closely."
    else:
        reasoning += "Conditions stable. No action required."

    supabase.table("ai_logs").insert({"node_id": data.node_id, "agent_type": "Multi-Agent Workflow", "reasoning": reasoning}).execute()
    
    if severity != "Normal":
        supabase.table("alerts").insert({"node_id": data.node_id, "severity": severity, "message": reasoning}).execute()
    print(f"[{severity}] Node {data.node_id} processed.")

# 4. API Endpoints
@app.post("/ingest-telemetry")
async def ingest_telemetry(data: SensorData, background_tasks: BackgroundTasks):
    # Save raw data to Supabase first for the charts
    try:
        supabase.table("telemetry_data").insert(data.dict()).execute()
    except Exception as e:
        print(f"Database error: {e}")

    # Run Agents in background
    def run_agents():
        s_res = sentinel_agent(data)
        a_res = analyst_agent(data, s_res)
        commander_agent(data, a_res)
    background_tasks.add_task(run_agents)
    return {"status": "success"}

@app.post("/trigger-anomaly")
async def trigger_anomaly(background_tasks: BackgroundTasks):
    """Manual override from the dashboard to simulate an immediate landslide event."""
    danger_dict = {
        "node_id": "node_alpha_01",
        "radar_displacement": round(random.uniform(1.5, 4.0), 4),
        "imu_vibration_x": round(random.uniform(-2.0, 2.0), 4),
        "imu_vibration_y": round(random.uniform(-2.0, 2.0), 4),
        "imu_vibration_z": round(random.uniform(7.0, 12.0), 4),
        "soil_moisture": round(random.uniform(85.0, 98.0), 2)
    }
    
    danger_data = SensorData(**danger_dict)

    def run_agents():
        s_res = sentinel_agent(danger_data)
        a_res = analyst_agent(danger_data, s_res)
        commander_agent(danger_data, a_res)
    
    try:
        supabase.table("telemetry_data").insert(danger_dict).execute()
    except Exception as e:
        print(f"Database error during manual trigger: {e}")
        
    background_tasks.add_task(run_agents)
    return {"status": "success", "message": "Manual Anomaly Triggered"}

@app.get("/")
def health_check():
    return {"status": "AI Core is Online"}