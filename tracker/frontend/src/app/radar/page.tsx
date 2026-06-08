"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import MapRadar from "@/components/radar-map";
import { useTrackerData } from "@/hooks/useTrackerData";
import { LoaderCircle, Globe, Users, Network, X } from "lucide-react";
import { useMemo } from "react";

export default function RadarPage() {
  const { data, isLoading, isError } = useTrackerData();

  const allPeers = useMemo(() => {
    if (!data) return [];
    return data.swarms.flatMap((s) => s.peers);
  }, [data]);

  const countryStats = useMemo(() => {
    const map = new Map<
      string,
      { peers: number; seeders: number }
    >();
    for (const peer of allPeers) {
      if (!peer.country) continue;
      const existing = map.get(peer.country);
      if (existing) {
        existing.peers += 1;
        existing.seeders += peer.seeders;
      } else {
        map.set(peer.country, { peers: 1, seeders: peer.seeders });
      }
    }
    return Array.from(map.entries())
      .map(([country, stats]) => ({ country, ...stats }))
      .sort((a, b) => b.peers - a.peers);
  }, [allPeers]);

  if (isLoading) {
    return (
      <div className="mx-10 flex items-center justify-center gap-3 py-20">
        <LoaderCircle className="animate-spin" />
        <p>Loading radar data...</p>
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="mx-10 flex h-96 flex-col items-center justify-center">
        <X className="text-red-500" />
        <p className="text-red-300">{isError?.toString() ?? "Unknown error"}</p>
      </div>
    );
  }

  return (
    <div className="mx-10 space-y-6">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Total Peers</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3">
              <Users className="text-green-400" />
              <span className="text-2xl font-bold">
                {data.total_peers}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Active Swarms</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3">
              <Network className="text-blue-400" />
              <span className="text-2xl font-bold">
                {data.total_swarms}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">Countries</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-3">
              <Globe className="text-amber-400" />
              <span className="text-2xl font-bold">
                {countryStats.length}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="h-[60vh]">
        <CardHeader>
          <CardTitle>Peer Distribution</CardTitle>
          <CardDescription>
            Real-time peer locations from tracker data
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[calc(100%-5rem)]">
          <MapRadar peerLocations={allPeers} />
        </CardContent>
      </Card>

      {countryStats.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Top Countries by Peer Count</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="max-h-60 overflow-y-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left">
                    <th className="py-2 pr-4">Country</th>
                    <th className="py-2 pr-4">Peers</th>
                    <th className="py-2">Seeders</th>
                  </tr>
                </thead>
                <tbody>
                  {countryStats.map((row) => (
                    <tr key={row.country} className="border-b last:border-0">
                      <td className="py-2 pr-4">{row.country}</td>
                      <td className="py-2 pr-4">{row.peers}</td>
                      <td className="py-2">{row.seeders}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
