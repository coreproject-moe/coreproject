"use client";

import useSWR from "swr";
import { HTTP_ENDPOINT } from "@/constants/url";
import { TrackerDataResponse } from "@/types/api";

const TRACKER_DATA_URL = `${HTTP_ENDPOINT}/api/tracker_data`;

const fetcher = async (url: string) => {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as unknown as TrackerDataResponse;
};

export function useTrackerData(refreshInterval = 15000) {
  const { data, error, isLoading } = useSWR<TrackerDataResponse>(
    TRACKER_DATA_URL,
    fetcher,
    { refreshInterval },
  );

  return {
    data: data ?? null,
    isLoading,
    isError: error,
  };
}
