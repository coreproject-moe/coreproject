"use client";

import {
  Map as MapContainer,
  MapControls,
  MapMarker,
  MarkerContent,
  MarkerTooltip,
} from "@/components/ui/map";

interface MapRadarProps {
  peerLocations: {
    ip: string;
    country: string;
    seeders: number;
  }[];
}

const countryCenters: Record<string, [number, number]> = {
  US: [-98.5, 39.8],
  CA: [-106.3, 56.1],
  GB: [-3.4, 55.4],
  DE: [10.5, 51.2],
  FR: [2.2, 46.2],
  ES: [-3.7, 40.5],
  IT: [12.6, 41.9],
  NL: [5.3, 52.1],
  PL: [19.1, 51.9],
  RU: [98.9, 61.5],
  UA: [31.2, 48.4],
  BR: [-51.9, -14.2],
  AR: [-63.6, -38.4],
  MX: [-102.6, 23.6],
  JP: [138.3, 36.2],
  KR: [128.0, 35.9],
  CN: [104.2, 35.9],
  IN: [78.9, 20.6],
  AU: [133.8, -25.3],
  ID: [120.4, -0.8],
  SG: [103.8, 1.3],
  TH: [100.5, 15.9],
  PH: [121.8, 12.9],
  MY: [101.9, 4.2],
  VN: [108.3, 14.1],
  TR: [35.2, 39.1],
  SA: [45.1, 23.9],
  AE: [53.7, 23.4],
  EG: [30.8, 26.8],
  ZA: [22.9, -30.6],
  NG: [8.7, 9.1],
  KE: [37.9, -0.02],
  TZ: [34.9, -6.4],
  CO: [-74.3, 4.6],
  PE: [-75.0, -9.2],
  CL: [-71.5, -35.7],
  NO: [8.5, 60.5],
  SE: [18.6, 60.1],
  FI: [25.7, 61.9],
  DK: [9.5, 56.3],
  CZ: [15.5, 49.8],
  AT: [14.6, 47.5],
  CH: [8.2, 46.8],
  BE: [4.5, 50.5],
  PT: [-8.2, 39.4],
  GR: [24.0, 39.1],
  RO: [24.9, 45.9],
  HU: [19.1, 47.2],
  NZ: [174.9, -40.9],
  IL: [34.9, 31.0],
  PK: [69.3, 30.4],
  BD: [90.4, 23.8],
  IR: [53.7, 32.4],
  KZ: [66.9, 48.0],
  UZ: [64.6, 41.4],
  GE: [43.2, 42.3],
  AM: [45.1, 40.1],
  AZ: [47.5, 40.1],
  BY: [27.9, 53.7],
  LT: [23.6, 55.2],
  LV: [24.1, 56.9],
  EE: [25.0, 58.6],
  IS: [-19.0, 64.9],
  IE: [-8.2, 53.1],
};

function getCenter(code: string): [number, number] | null {
  return countryCenters[code] ?? null;
}

export default function MapRadar({ peerLocations }: MapRadarProps) {
  const byCountry = new Map<
    string,
    { peers: number; seeders: number }
  >();

  for (const peer of peerLocations) {
    if (!peer.country) continue;
    const existing = byCountry.get(peer.country);
    if (existing) {
      existing.peers += 1;
      existing.seeders += peer.seeders;
    } else {
      byCountry.set(peer.country, { peers: 1, seeders: peer.seeders });
    }
  }

  return (
    <MapContainer center={[10, 20]} zoom={1.8} maxZoom={6} minZoom={1.2}>
      <MapControls position="top-left" showZoom />

      {Array.from(byCountry.entries()).map(([country, stats]) => {
        const center = getCenter(country);
        if (!center) return null;

        return (
          <MapMarker
            key={country}
            longitude={center[0]}
            latitude={center[1]}
          >
            <MarkerContent>
              <div
                className="rounded-full border-2 border-white shadow-lg"
                style={{
                  width: Math.max(8, Math.min(stats.peers * 1.5, 48)),
                  height: Math.max(8, Math.min(stats.peers * 1.5, 48)),
                  backgroundColor:
                    stats.seeders > stats.peers / 2
                      ? "#22c55e"
                      : "#eab308",
                }}
              />
            </MarkerContent>
            <MarkerTooltip>
              <div className="text-center">
                <div className="font-bold">{country}</div>
                <div>
                  Peers: {stats.peers} | Seeders: {stats.seeders}
                </div>
              </div>
            </MarkerTooltip>
          </MapMarker>
        );
      })}
    </MapContainer>
  );
}
