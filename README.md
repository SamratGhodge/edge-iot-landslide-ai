# Edge IoT System with Agentic AI for Landslide Detection

This project is a real-time landslide monitoring system that uses a Multi-Agent AI architecture to process sensor data at the "Edge" (locally), reducing false alarms and latency.

## 🏗️ System Architecture
* **Sensing Layer:** Simulated mmWave Radar and IMU sensors.
* **AI Core:** A FastAPI backend running Sentinel, Analyst, and Commander agents.
* **Dashboard:** A Next.js web interface with live maps and trend charts.

## 💻 Tech Stack
* **Backend:** Python, FastAPI.
* **Frontend:** Next.js, Tailwind CSS, Leaflet.js.
* **Database:** Supabase (PostgreSQL).

## 🚀 How to Run
1. **Setup Env:** Add your Supabase keys to `.env` and `frontend/.env.local`.
2. **Install:** Run `pip install -r requirements.txt` and `npm install` in the frontend folder.
3. **Launch:** Use the "God Command":
   ```bash
   npx concurrently -k -n "AI,SENSOR,UI" "uvicorn ai_core.main:app" "python3 simulation/sensor_sim.py" "cd frontend && npm run dev"