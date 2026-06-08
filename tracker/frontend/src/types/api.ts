export interface BackendData {
  quart_version: string;
  redis_version: {
    client: string;
    server: string;
  };
  python_version: string;
  redis_data: {
    [infoHash: string]: {
      [peerAddress: string]: string;
    };
  };
  geo?: GeoStats;
}

export interface GeoStats {
  provider: string;
  license: string;
  attribution_url: string;
  loaded: boolean;
  countries_count: number;
  ipv4_blocks_count: number;
  ipv6_blocks_count: number;
}

export interface TrackerDataResponse {
  swarms: SwarmData[];
  total_peers: number;
  total_swarms: number;
}

export interface SwarmData {
  info_hash: string;
  peers: PeerLocation[];
  peer_count: number;
}

export interface PeerLocation {
  ip: string;
  port: number;
  country: string;
  continent: string;
  seeders: number;
}

export interface RedisData {
  info_hash: string;
  type: "http" | "udp" | "websocket";
  peer_id: string;
  peer_ip: string;
  port: number;
  left: number | null;
  country?: string;
}

// Country → center coordinates for map rendering
export interface LatLng {
  lng: number;
  lat: number;
}

export interface MapConnection {
  from: LatLng;
  to: LatLng;
  from_country: string;
  to_country: string;
  peer_count: number;
  seeder_count: number;
}

export interface MapNode {
  country: string;
  center: LatLng;
  peer_count: number;
  seeder_count: number;
  continent: string;
}
