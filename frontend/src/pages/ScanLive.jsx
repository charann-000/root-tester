import { useState, useEffect, useRef, useCallback } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Loader2, Play, CheckCircle, XCircle, Clock } from "lucide-react";
import axios from "axios";
import { useAuth } from "../hooks/useAuth";
import { Navbar } from "../components/Navbar";
import { LiveTerminal } from "../components/LiveTerminal";
import { cn } from "../lib/utils";

export function ScanLive() {
  const { scanId } = useParams();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  
  const [messages, setMessages] = useState([]);
  const [scan, setScan] = useState(null);
  const [status, setStatus] = useState("running");
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  const fetchScan = useCallback(async () => {
    try {
      const response = await axios.get(`/api/scan/${scanId}`);
      setScan(response.data);
      setStatus(response.data.status);
      
      if (response.data.status === "complete") {
        setTimeout(() => {
          navigate(`/scan/results/${scanId}`);
        }, 2000);
      } else if (response.data.status === "failed") {
        setMessages(prev => [...prev, { type: "error", tool: "scan", message: "Scan failed" }]);
      }
    } catch (error) {
      console.error("Failed to fetch scan:", error);
    }
  }, [scanId, navigate]);

  const connectWebSocket = useCallback(() => {
    if (!scanId || !token) return;

    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `${window.location.protocol === "https:" ? "wss:" : "ws:"}//${window.location.host}/ws/scan/${scanId}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);
        
        if (data.type === "scan_complete") {
          setStatus("complete");
          setTimeout(() => {
            navigate(`/scan/results/${scanId}`);
          }, 2000);
        } else if (data.type === "error") {
          setStatus("failed");
        }
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
      }
    };

    ws.onclose = () => {
      setConnected(false);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    wsRef.current = ws;
  }, [scanId, token, navigate]);

  useEffect(() => {
    if (!user || !scanId) return;

    fetchScan();
    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [user, scanId, fetchScan, connectWebSocket]);

  useEffect(() => {
    if (!connected && status === "running") {
      const interval = setInterval(connectWebSocket, 5000);
      return () => clearInterval(interval);
    }
  }, [connected, status, connectWebSocket]);

  const getStatusIcon = (toolStatus) => {
    switch (toolStatus) {
      case "running":
        return <Loader2 className="h-4 w-4 animate-spin text-accent" />;
      case "complete":
        return <CheckCircle className="h-4 w-4 text-success" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-destruct" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getToolStatus = (tool) => {
    for (const msg of messages) {
      if (msg.tool === tool) {
        if (msg.type === "tool_done") return "complete";
        if (msg.type === "error") return "failed";
      }
    }
    for (const msg of messages) {
      if (msg.tool === tool && msg.type === "tool_start") return "running";
    }
    return "waiting";
  };

  if (!scan) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  const tools = scan.tools_used || [];
  const completedTools = messages.filter(m => m.type === "tool_done").length;
  const progress = tools.length > 0 ? (completedTools / tools.length) * 100 : 0;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-6 py-8">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Live Scan</h1>
            <p className="text-muted-foreground">{scan.target}</p>
          </div>
          <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${connected ? "bg-success" : "bg-warning"}`} />
            <span className="text-sm text-muted-foreground">
              {connected ? "Connected" : "Reconnecting..."}
            </span>
          </div>
        </div>

        <div className="grid gap-6 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <div className="card h-full p-4">
              <h2 className="mb-4 text-lg font-semibold">Tool Progress</h2>
              <div className="space-y-2">
                {tools.map((tool) => {
                  const toolStatus = getToolStatus(tool);
                  return (
                    <div
                      key={tool}
                      className={cn(
                        "flex items-center justify-between rounded-lg border border-border p-3",
                        toolStatus === "running" && "border-accent bg-accent/10"
                      )}
                    >
                      <div className="flex items-center gap-3">
                        {getStatusIcon(toolStatus)}
                        <span className="font-mono text-sm">{tool}</span>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {toolStatus === "running" && "Running..."}
                        {toolStatus === "complete" && "Done"}
                        {toolStatus === "failed" && "Failed"}
                        {toolStatus === "waiting" && "Waiting"}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>

          <div className="lg:col-span-3">
            <div className="card h-full p-4">
              <h2 className="mb-4 text-lg font-semibold">Terminal Output</h2>
              <div className="h-[500px]">
                <LiveTerminal messages={messages} />
              </div>
            </div>
          </div>
        </div>

        <div className="mt-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Phase: {status === "complete" ? "Complete" : status === "failed" ? "Failed" : `Running tools (${completedTools}/${tools.length})`}
            </span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-card">
            <div
              className="h-full bg-accent transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {status === "complete" && (
          <div className="mt-4 flex items-center justify-center">
            <button
              onClick={() => navigate(`/scan/results/${scanId}`)}
              className="btn btn-primary"
            >
              View Results
            </button>
          </div>
        )}
      </main>
    </div>
  );
}