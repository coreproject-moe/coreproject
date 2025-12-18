"use client";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { IframeMessage } from "@/types/iframe";
import { WS_TRACKER_ENDPOINT } from "@/constants/url";
import { isDataBencoded } from "@/functions/bencode";
import { useHttpData } from "@/hooks/useHttpData";
import { CheckCheck, HeartPulse, LoaderCircle, X, XCircle } from "lucide-react";
import { useState, useRef, useEffect, useCallback } from "react";
import { cn } from "@/lib/utils";

function HttpCard() {
  const {
    data: httpData,
    status: httpStatus,
    isLoading: httpIsLoading,
    isError: httpIsError,
  } = useHttpData();

  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading",
  );
  const [errorMessage, setErrorMessage] = useState<string>("");

  // Main status management effect
  useEffect(() => {
    if (httpIsLoading) {
      setStatus("loading");
      return;
    }

    if (httpIsError) {
      setStatus("error");
      setErrorMessage("Failed to connect to the tracker");
      return;
    }

    if (httpStatus !== 200) {
      setStatus("error");
      setErrorMessage(`HTTP Error: Status code ${httpStatus}`);
      return;
    }

    if (!httpData || !isDataBencoded(httpData)) {
      setStatus("error");
      setErrorMessage("Invalid or malformed response from tracker");
      return;
    }

    setStatus("success");
    setErrorMessage("");
  }, [httpIsLoading, httpIsError, httpStatus, httpData]);

  // Development logging effect
  useEffect(() => {
    if (process.env.NODE_ENV !== "development") return;

    console.log("HTTP Component State:", {
      loading: httpIsLoading,
      status: httpStatus,
      data: httpData,
      error: httpIsError,
    });

    if (!httpIsLoading && httpData) {
      console.log("Data validation result:", isDataBencoded(httpData));
    }
  }, [httpIsLoading, httpData, httpIsError, httpStatus]);

  const getStatusContent = () => {
    switch (status) {
      case "loading":
        return {
          icon: <LoaderCircle className="animate-spin" />,
          description: "Checking if the tracker is responding with HTTP",
          text: "Checking",
          className: "text-primary/90",
        };
      case "success":
        return {
          icon: <CheckCheck className="text-green-400" />,
          description: "Successfully communicated with the tracker",
          text: "Tracker is working",
          className: "text-primary/90",
        };
      case "error":
        return {
          icon: <X className="text-red-500" />,
          description: "Failed to communicate with the tracker",
          text: errorMessage,
          className: "text-red-300",
        };
    }
  };

  const statusContent = getStatusContent();

  return (
    <Card className="md:h-[22vh] lg:h-[17vh]">
      <CardHeader>
        <CardTitle>HTTP Tracker</CardTitle>
        <CardDescription>{statusContent.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex h-full flex-col items-center justify-center gap-2">
          {statusContent.icon}
          <p className={cn("whitespace-nowrap", statusContent.className)}>
            {statusContent.text}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function WebsocketCard() {
  const [status, setStatus] = useState<"loading" | "connected" | "error">(
    "loading",
  );
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const ws = new WebSocket(WS_TRACKER_ENDPOINT);

    const handleError = (errorMessage: string, closeReason?: string) => {
      const message = closeReason
        ? `${errorMessage}: ${closeReason}`
        : errorMessage;
      setStatus("error");
      setError(new Error(message));
    };

    ws.onopen = () => {
      setStatus("connected");
      setError(null);
    };

    ws.onerror = () => {
      handleError("WebSocket connection error");
    };

    ws.onclose = (event) => {
      if (!event.wasClean) {
        handleError("WebSocket connection closed unexpectedly", event.reason);
      }
    };

    return () => {
      // Close connection when component unmounts
      if (ws.readyState === WebSocket.OPEN) {
        ws.close();
      }
    };
  }, []);

  const getStatusContent = () => {
    switch (status) {
      case "loading":
        return {
          icon: <LoaderCircle className="animate-spin" />,
          text: "Checking",
          description:
            "Checking if the connection to the tracker is possible with websocket",
        };
      case "connected":
        return {
          icon: <CheckCheck className="text-green-400" />,
          text: "Websocket Connection Established",
          description: "Successfully connected to WebSocket endpoint",
        };
      case "error":
        return {
          icon: <X className="text-red-500" />,
          text: error?.message || "Unknown error occurred",
          description: "Failed to establish WebSocket connection",
        };
    }
  };

  const statusContent = getStatusContent();

  return (
    <Card className="md:h-[22vh] lg:h-[17vh]">
      <CardHeader>
        <CardTitle>Websocket Status</CardTitle>
        <CardDescription>{statusContent.description}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex h-full flex-col items-center justify-center gap-2">
          {statusContent.icon}
          <p
            className={cn(
              "whitespace-nowrap",
              status === "error" ? "text-red-300" : "text-primary/90",
            )}
          >
            {statusContent.text}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

function WebsocketTrackerCard() {
  const SHOW_CONSOLE = process.env.NODE_ENV === "development";
  const [status, setStatus] = useState<{
    working: boolean;
    checking: boolean;
    error?: string;
  }>({ working: false, checking: true });

  const seederIframeRef = useRef<HTMLIFrameElement>(null);
  const clientIframeRef = useRef<HTMLIFrameElement>(null);

  // Disable console in iframes for production
  const disableConsole = useCallback(
    (ref: React.RefObject<HTMLIFrameElement | null>) => {
      if (!ref.current?.contentWindow || SHOW_CONSOLE) return;
      // @ts-expect-error: console is present in runtime
      ref.current.contentWindow!.console = {
        ...console,
        log: () => { },
        error: () => { },
        warn: () => { },
      };
    },
    [SHOW_CONSOLE],
  );

  // Handle iframe load
  const handleSeederLoad = useCallback(() => {
    disableConsole(seederIframeRef);
    setStatus((prev) => ({ ...prev, checking: true }));

    const message = {
      type: "seeder",
      data: WS_TRACKER_ENDPOINT,
    } as const;

    seederIframeRef.current?.contentWindow?.postMessage(
      { from: "parent", message: JSON.stringify(message) },
      "*",
    );
  }, [disableConsole]);

  // Message handler
  useEffect(() => {
    const handler = (event: MessageEvent<IframeMessage>) => {
      if (!event.data.message) return;

      // Handle seeder response
      if (event.data.from === "seeder-iframe") {
        const magnetURI = event.data.message as string;
        const clientMessage = {
          type: "client",
          data: magnetURI,
          trackerURI: WS_TRACKER_ENDPOINT,
        };

        setTimeout(() => {
          clientIframeRef.current?.contentWindow?.postMessage(
            { from: "parent", message: JSON.stringify(clientMessage) },
            "*",
          );
        }, 5000); // Allow time for seeder initialization
      }

      // Handle client response
      if (event.data.from === "client-iframe") {
        setStatus({
          working: event.data.message === "Download Complete",
          checking: false,
        });
      }
    };

    window.addEventListener("message", handler);
    return () => window.removeEventListener("message", handler);
  }, []);

  return (
    <Card className="md:h-[22vh] lg:h-[17vh]">
      <CardHeader>
        <CardTitle>WebSocket Tracker</CardTitle>
        <CardDescription>
          {status.checking
            ? "Testing WebRTC connectivity..."
            : status.working
              ? "Successfully transferred data via WebRTC"
              : "Failed to establish WebRTC connection"}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="flex h-full flex-col items-center justify-center gap-2">
          {status.checking ? (
            <>
              <LoaderCircle className="animate-spin" />
              <span>Testing...</span>
            </>
          ) : status.working ? (
            <>
              <CheckCheck className="text-green-500" />

              <span className="text-primary/90">Tracker Operational</span>
            </>
          ) : (
            <>
              <XCircle className="text-red-500" />
              <span className="text-destructive">Connection Failed</span>
            </>
          )}
        </div>
      </CardContent>

      {/* Hidden iframes */}
      <div className="hidden">
        <iframe
          ref={seederIframeRef}
          src="/torrent-tester.html"
          onLoad={handleSeederLoad}
          title="WebTorrent Seeder"
        />
        <iframe
          ref={clientIframeRef}
          src="/torrent-tester.html"
          onLoad={() => disableConsole(clientIframeRef)}
          title="WebTorrent Client"
        />
      </div>
    </Card>
  );
}

export default function Page() {
  return (
    <div className="mx-10">
      <div className="mb-5 flex flex-col gap-5">
        <div className="flex items-center gap-3">
          <HeartPulse className="text-red-400" />
          <h1 className="text-3xl">Tracker Health Check:</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 items-center justify-center gap-10 md:grid-cols-3">
        <WebsocketCard />
        <HttpCard />
        <WebsocketTrackerCard />
      </div>
    </div>
  );
}
