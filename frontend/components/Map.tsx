"use client";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";

// Fix for default Leaflet icons in Next.js
const customIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

export default function Map({ alertStatus }: { alertStatus: string }) {
  const position: [number, number] = [18.5204, 73.8567]; // Coordinates for Node Alpha
  const isDanger = alertStatus === "Danger";

  return (
    <MapContainer center={position} zoom={13} style={{ height: "100%", width: "100%", borderRadius: "0.5rem" }}>
      <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" />
      <Marker position={position} icon={customIcon}>
        <Popup>Node Alpha_01 <br/> Status: {alertStatus}</Popup>
      </Marker>
      {/* Red pulsing circle if in Danger */}
      {isDanger && (
        <Circle center={position} pathOptions={{ color: 'red', fillColor: '#f03', fillOpacity: 0.5 }} radius={500} />
      )}
    </MapContainer>
  );
}