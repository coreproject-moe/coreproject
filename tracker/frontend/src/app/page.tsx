"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  AudioLines,
  EarthLock,
  File,
  GlobeLock,
  HardDriveDownload,
  HardDriveUpload,
  Layers2,
  LoaderCircle,
  Router,
  WaypointsIcon,
  X,
} from "lucide-react";

import { useBackendData } from "@/hooks/useBackendData";
import React, { useMemo } from "react";
import { BackendData, RedisData } from "@/types/api";
import RedisLogo from "@/icons/logos/redis.svg";
import PythonLogo from "@/icons/logos/python.svg";
import QuartLogo from "@/icons/logos/quart.svg";

function VersionCardComponent({ data }: { data: BackendData }) {
  const mapping = [
    {
      title: "Quart",
      description:
        "An async Python micro framework for building web applications.",
      icon: QuartLogo,
      version: data.quart_version,
    },
    {
      title: "Python",
      description:
        "Python is a programming language that lets you work quickly and integrate systems more effectively.",
      icon: PythonLogo,
      version: data.python_version,
    },
    {
      title: "Redis",
      description: "Redis is an in-memory database that persists on disk.",
      icon: RedisLogo,
      version: {
        client: data.redis_version.client,
        server: data.redis_version.server,
      },
    },
  ];

  return (
    <div className="grid grid-cols-1 items-center justify-center gap-10 md:grid-cols-3">
      {mapping.map((value, index) => {
        const IconComponent = value.icon as React.FunctionComponent<
          React.SVGProps<SVGSVGElement>
        >;

        return (
          <Card
            key={`version-card-component-${index}`}
            className="md:h-[22vh] lg:h-[19vh]"
          >
            <CardHeader>
              <CardTitle>{value.title}</CardTitle>
              <CardDescription>
                <p>{value.description}</p>
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative inset-0 flex h-[50px] items-center justify-center">
                <IconComponent
                  width="120"
                  height="250"
                  className="absolute z-20 h-[40px]"
                />

                <div className="dark:bg-primary absolute z-10 h-[45px] w-[125px] rounded-lg"></div>
              </div>
            </CardContent>
            <CardFooter className="justify-center gap-2">
              {typeof value.version === "string" && (
                <>
                  <p>Version:</p>
                  <code>{value.version}</code>
                </>
              )}
              {typeof value.version === "object" && (
                <>
                  <div className="space-x-2">
                    <span>Server:</span>
                    <code>{value.version.server}</code>
                  </div>
                  <div className="text-primary/30">|</div>
                  <div className="space-x-2">
                    <span>Client:</span>
                    <code>{value.version.client}</code>
                  </div>
                </>
              )}
            </CardFooter>
          </Card>
        );
      })}
    </div>
  );
}
function TorrentCardComponent({ data }: { data: BackendData }) {
  const metrics = useMemo(() => {
    let seeders = 0,
      leechers = 0,
      udpClients = 0,
      websocketClients = 0,
      httpClients = 0;

    // Process redis data
    Object.values(data.redis_data).forEach((torrent) => {
      Object.values(torrent).forEach((peerData) => {
        try {
          const peerInfo = JSON.parse(peerData) satisfies RedisData;

          // Update seeder/leecher counts
          if (peerInfo.left === 0) {
            seeders++;
          } else {
            leechers++;
          }

          // Update protocol counts
          switch (peerInfo.type) {
            case "http":
              httpClients++;
              break;
            case "udp":
              udpClients++;
              break;
            case "websocket":
              websocketClients++;
              break;
            default:
              console.error(`Unknown client type: ${peerInfo.type}`);
          }
        } catch {
          console.warn("Invalid peer data format:", peerData);
        }
      });
    });

    return {
      totalTorrents: Object.keys(data.redis_data).length,
      totalClients: Object.values(data.redis_data).reduce(
        (acc, torrent) => acc + Object.keys(torrent).length,
        0,
      ),
      seeders,
      leechers,
      udpClients,
      httpClients,
      websocketClients,
    };
  }, [data]);

  // Card configuration
  const cardConfigs = [
    {
      title: "Total Torrents and Clients",
      description: "The amount of torrents and clients",
      metrics: [
        {
          name: "Torrents",
          value: metrics.totalTorrents,
          icon: File,
          iconClass: "text-green-400",
        },
        {
          name: "Clients",
          value: metrics.totalClients,
          icon: Router,
          iconClass: "text-green-600",
        },
      ],
    },
    {
      title: "Client Distribution",
      description: "The amount of clients by protocol",
      metrics: [
        {
          name: "UDP",
          value: metrics.udpClients,
          icon: GlobeLock,
          iconClass: "text-green-400",
        },
        {
          name: "HTTP",
          value: metrics.httpClients,
          icon: EarthLock,
          iconClass: "text-green-600",
        },
        {
          name: "Websocket",
          value: metrics.websocketClients,
          icon: WaypointsIcon,
          iconClass: "text-green-400",
        },
      ],
    },
    {
      title: "Total Seeders/Leechers",
      description: "The amount of seeders or leechers",
      metrics: [
        {
          name: "Seeders",
          value: metrics.seeders,
          icon: HardDriveUpload,
          iconClass: "text-green-400",
        },
        {
          name: "Leechers",
          value: metrics.leechers,
          icon: HardDriveDownload,
          iconClass: "text-red-400",
        },
      ],
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-10 md:grid-cols-3">
      {cardConfigs.map((card) => (
        <Card key={card.title} className="md:h-[22vh] lg:h-[17vh]">
          <CardHeader>
            <CardTitle>{card.title}</CardTitle>
            <CardDescription>{card.description}</CardDescription>
          </CardHeader>
          <CardContent>
            <div
              className="grid h-full gap-4"
              style={{
                gridTemplateColumns: `repeat(${Number(card.metrics.length ?? 0)}, minmax(0, 1fr))`,
              }}
            >
              {card.metrics.map((metric) => {
                const IconComponent = metric.icon;
                return (
                  <div
                    key={metric.name}
                    className="flex flex-col items-center justify-center gap-2"
                  >
                    <IconComponent
                      className={metric.iconClass}
                      aria-label={metric.name}
                    />
                    <p className="text-primary/90 text-sm whitespace-nowrap">
                      {metric.name}: <code>{metric.value}</code>
                    </p>
                  </div>
                );
              })}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default function Page() {
  const {
    data: backendData,
    isLoading: backendIsLoading,
    isError: backendIsError,
  } = useBackendData();

  return (
    <div className="mx-10">
      {backendIsLoading ? (
        <div className="flex w-full items-center justify-center gap-3">
          <p>Loading</p>
          <LoaderCircle className="animate-spin" />
        </div>
      ) : (
        <>
          {backendIsError ? (
            <div className="flex h-96 flex-col items-center justify-center">
              <X className="text-red-500" />
              <p className="text-red-300"> {backendIsError.toString()}</p>
            </div>
          ) : (
            backendData && (
              <>
                {/* Stack version */}
                <div className="mb-5 flex flex-col gap-5">
                  <div className="flex items-center gap-3">
                    <Layers2 className="text-amber-600" />
                    <h1 className="text-3xl">Stack version:</h1>
                  </div>
                </div>

                {/* Grid to show version  */}
                <VersionCardComponent data={backendData} />

                {/* Tracker information */}
                <div className="my-10 flex flex-col gap-5">
                  <div className="flex items-center gap-3">
                    <AudioLines className="text-orange-600" />
                    <h1 className="text-3xl">Tracker information:</h1>
                  </div>
                </div>

                {/* Grid to show tracker information  */}
                <TorrentCardComponent data={backendData} />
              </>
            )
          )}
        </>
      )}
    </div>
  );
}
