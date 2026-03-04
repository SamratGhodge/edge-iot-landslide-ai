"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { supabase } from "@/lib/supabase";
import { Activity, AlertTriangle, Radio, Network, Zap, Cpu, Clock } from "lucide-react";
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);
const LiveMap = dynamic(() => import("../components/Map"), { ssr: false });

export default function Dashboard() {
  const [telemetry, setTelemetry] = useState<any>(null);
  const [latestAlert, setLatestAlert] = useState<any>(null);
  const [aiLogs, setAiLogs] = useState<any[]>([]);
  
  // 1. New State for Time Toggle and Raw History Buffer
  const [timeView, setTimeView] = useState<'seconds' | 'minutes'>('seconds');
  const [historyBuffer, setHistoryBuffer] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      // Fetch the last 120 records (approx 6 minutes of data at 3s intervals)
      const { data: tData } = await supabase.from("telemetry_data").select("*").order("timestamp", { ascending: false }).limit(120);
      const { data: aData } = await supabase.from("alerts").select("*").order("timestamp", { ascending: false }).limit(1);
      const { data: lData } = await supabase.from("ai_logs").select("*").order("timestamp", { ascending: false }).limit(5);
      
      if (tData) {
        setTelemetry(tData[0]);
        setHistoryBuffer([...tData].reverse()); // Store chronologically
      }
      if (aData) setLatestAlert(aData[0]);
      if (lData) setAiLogs(lData);
    };
    fetchData();

    const channel = supabase.channel("realtime-dashboard")
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "telemetry_data" }, (payload) => {
        setTelemetry(payload.new);
        // Keep the buffer capped at the latest 120 items
        setHistoryBuffer(prev => [...prev, payload.new].slice(-120));
      })
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "alerts" }, (payload) => setLatestAlert(payload.new))
      .on("postgres_changes", { event: "INSERT", schema: "public", table: "ai_logs" }, (payload) => {
        setAiLogs((prev) => [payload.new, ...prev].slice(0, 5));
      })
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, []);

  const triggerSimulation = async () => {
    try {
      const response = await fetch("http://localhost:8000/trigger-anomaly", { 
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });
      
      if (response.ok) {
        alert("🚨 Danger Event Simulated! Agents are processing...");
      } else {
        alert("⚠️ Backend received the request but hit an error.");
      }
    } catch (e) {
      console.error("Simulation failed", e);
      alert("❌ Connection Error: Is the FastAPI server running on port 8000?");
    }
  };

  // 2. Dynamically calculate chart data based on the selected toggle
  const getChartData = () => {
    let displayData = historyBuffer;
    
    if (timeView === 'seconds') {
      // Show only the last 20 points (last 60 seconds)
      displayData = historyBuffer.slice(-20);
    } else {
      // For minutes, show the whole buffer, but maybe sample every 3rd point so the chart isn't overly crowded
      displayData = historyBuffer.filter((_, i) => i % 3 === 0);
    }

    return {
      labels: displayData.map(d => {
        const date = new Date(d.timestamp);
        // Show seconds in 'seconds' view, hide them in 'minutes' view
        return timeView === 'seconds' 
          ? date.toLocaleTimeString() 
          : date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      }),
      radar: displayData.map(d => d.radar_displacement),
    };
  };

  const currentChartData = getChartData();
  const isDanger = latestAlert?.severity === 'Danger';

  return (
    <div className="min-h-screen bg-slate-950 text-white p-6">
      <header className="mb-6 border-b border-slate-800 pb-4 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-blue-400">Agentic AI Landslide Command Center</h1>
          <p className="text-slate-400">Real-time edge telemetry and multi-agent reasoning</p>
        </div>
        <button 
          onClick={triggerSimulation}
          className="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded flex items-center gap-2 transition-all">
          <Zap size={18} /> Force Simulate Danger
        </button>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        
        {/* Map Panel */}
        <div className="bg-slate-900 p-2 rounded-xl border border-slate-800 col-span-1 md:col-span-2 h-64 z-0 relative">
          <LiveMap alertStatus={latestAlert?.severity || "Normal"} />
        </div>

        {/* Open RAN & Node Health Panel */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 col-span-1">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Network className="text-emerald-400"/> O-RAN & Node Health</h2>
          <div className="space-y-4">
            <div className="flex justify-between items-center bg-slate-800 p-2 rounded">
              <span className="text-slate-400 text-sm flex items-center gap-2"><Cpu size={14}/> Edge CPU Load</span>
              <span className="font-mono text-green-400">14%</span>
            </div>
            <div className="flex justify-between items-center bg-slate-800 p-2 rounded">
              <span className="text-slate-400 text-sm flex items-center gap-2"><Radio size={14}/> LoRa Signal</span>
              <span className="font-mono text-blue-400">-85 dBm</span>
            </div>
            <div className={`p-2 rounded text-sm font-bold border ${isDanger ? 'bg-red-900/30 border-red-500 text-red-400' : 'bg-green-900/30 border-green-500 text-green-400'}`}>
              Network Slice: {isDanger ? "EMERGENCY PRIORITY" : "Standard Traffic"}
            </div>
          </div>
        </div>

        {/* Alert Status Panel */}
        <div className={`p-6 rounded-xl border flex flex-col justify-center items-center text-center col-span-1 transition-colors duration-500 ${isDanger ? 'bg-red-900/20 border-red-500' : latestAlert?.severity === 'Warning' ? 'bg-yellow-900/20 border-yellow-500' : 'bg-green-900/20 border-green-500'}`}>
          <AlertTriangle size={48} className={`mb-4 ${isDanger ? 'text-red-500 animate-pulse' : latestAlert?.severity === 'Warning' ? 'text-yellow-500' : 'text-green-500'}`} />
          <h2 className="text-2xl font-bold">{latestAlert ? `STATUS: ${latestAlert.severity.toUpperCase()}` : "STATUS: NORMAL"}</h2>
          <p className="text-sm mt-2 opacity-80">{latestAlert?.message || "All systems nominal."}</p>
        </div>

        {/* Charts Panel with Time Toggle */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 col-span-1 md:col-span-2">
           <div className="flex justify-between items-center mb-4">
             <h2 className="text-lg font-semibold text-slate-300">Radar Displacement (mm)</h2>
             
             {/* 3. The Toggle Buttons */}
             <div className="flex bg-slate-800 rounded-lg p-1 border border-slate-700">
                <button 
                  onClick={() => setTimeView('seconds')}
                  className={`px-3 py-1 text-xs font-bold rounded-md flex items-center gap-1 transition-colors ${timeView === 'seconds' ? 'bg-blue-500 text-white' : 'text-slate-400 hover:text-white'}`}>
                  <Clock size={12}/> Live (Secs)
                </button>
                <button 
                  onClick={() => setTimeView('minutes')}
                  className={`px-3 py-1 text-xs font-bold rounded-md flex items-center gap-1 transition-colors ${timeView === 'minutes' ? 'bg-blue-500 text-white' : 'text-slate-400 hover:text-white'}`}>
                  History (Mins)
                </button>
             </div>
           </div>

           <Line data={{
             labels: currentChartData.labels,
             datasets: [{ label: 'Displacement', data: currentChartData.radar, borderColor: 'rgb(74, 222, 128)', tension: 0.1, pointRadius: timeView === 'seconds' ? 3 : 1 }]
           }} options={{ responsive: true, scales: { y: { beginAtZero: true } }, animation: { duration: 0 } }} />
        </div>

        {/* AI Agent "Think View" Log */}
        <div className="bg-slate-900 p-6 rounded-xl border border-slate-800 col-span-1 md:col-span-2 overflow-y-auto max-h-80">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2"><Activity className="text-purple-400"/> Agent Logic Think-View</h2>
          <div className="space-y-3 flex flex-col-reverse">
            {aiLogs.map((log, i) => (
              <div key={i} className="bg-slate-800 p-3 rounded text-xs font-mono text-slate-300 whitespace-pre-wrap">
                <span className="text-purple-400 font-bold block mb-1">[{log.agent_type}] - {new Date(log.timestamp).toLocaleTimeString()}</span> 
                {log.reasoning}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}