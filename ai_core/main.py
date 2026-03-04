import os
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime

# 1. Setup and Configurations
load_dotenv()
supabase: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))
app = FastAPI(title="Agentic AI Landslide Command Center")

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
    """Agent 1: Detects raw anomalies in movement and vibration."""
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
    """Agent 2: Provides environmental context."""
    reasoning = sentinel_finding["reasoning"] + "\nAnalyst Context: "
    risk_multiplier = 1.0
    
    if data.soil_moisture > 60.0:
        risk_multiplier = 1.5
        reasoning += f"Soil is highly saturated ({data.soil_moisture}%). Landslide risk elevated."
    else:
        reasoning += "Soil moisture is stable."
        
    final_score = sentinel_finding["score"] * risk_multiplier
    return {"final_score": final_score, "reasoning": reasoning}

def commander_agent(data: SensorData, analyst_finding: dict):
    """Agent 3: Makes the final decision and logs to database."""
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

    # Log the AI reasoning to Supabase
    supabase.table("ai_logs").insert({
        "node_id": data.node_id,
        "agent_type": "Multi-Agent Workflow",
        "reasoning": reasoning
    }).execute()

    # If it's a Warning or Danger, log an Alert
    if severity != "Normal":
        supabase.table("alerts").insert({
            "node_id": data.node_id,
            "severity": severity,
            "message": reasoning
        }).execute()
        
    print(f"[{severity}] Node {data.node_id} processed.")

# 4. API Endpoints
@app.post("/ingest-telemetry")
async def ingest_telemetry(data: SensorData, background_tasks: BackgroundTasks):
    """Endpoint for the Edge Node (Raspberry Pi) to send data to the AI."""
    
    # Run the Agentic workflow in the background so the sensor isn't delayed
    def run_agents():
        sentinel_result = sentinel_agent(data)
        analyst_result = analyst_agent(data, sentinel_result)
        commander_agent(data, analyst_result)
        
    background_tasks.add_task(run_agents)
    return {"status": "success", "message": "Data received and Agents deployed."}

@app.get("/")
def health_check():
    return {"status": "AI Core is Online"}