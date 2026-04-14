import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { Loader2, Download, Search, FileText, AlertTriangle, Play, RefreshCw } from "lucide-react";
import axios from "axios";
import { useAuth } from "../hooks/useAuth";
import { Navbar } from "../components/Navbar";
import { RiskBadge } from "../components/RiskBadge";
import { VulnCard } from "../components/VulnCard";
import { formatDateTime, getRiskColor } from "../lib/utils";
import { cn } from "../lib/utils";

export function Results() {
  const { scanId } = useParams();
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [scan, setScan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState("overview");
  const [filterSeverity, setFilterSeverity] = useState("all");
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    if (!authLoading && user) {
      fetchScan();
    }
  }, [user, authLoading, scanId]);

  const fetchScan = async () => {
    try {
      const response = await axios.get(`/api/scan/${scanId}`);
      setScan(response.data);
    } catch (error) {
      console.error("Failed to fetch scan:", error);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = async () => {
    setDownloading(true);
    try {
      const response = await axios.get(`/api/report/${scanId}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `metatron_${scan?.target}_${scanId}.pdf`
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download report:", error);
    } finally {
      setDownloading(false);
    }
  };

  const reScan = () => {
    navigate(`/scan/new?target=${scan?.target}`);
  };

  const startNewScan = async (e) => {
    e.preventDefault();
    if (!scan) return;
    
    try {
      const response = await axios.post("/api/scan/start", {
        target: scan.target,
        tools: scan.tools_used,
        preset: "custom",
        has_accepted_disclaimer: 1,
      });
      navigate(`/scan/live/${response.data.scan_id}`);
    } catch (error) {
      console.error("Failed to start scan:", error);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  if (!scan) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <div className="text-center">
          <p className="text-muted-foreground">Scan not found</p>
        </div>
      </div>
    );
  }

  const vulnerabilities = scan.vulnerabilities || [];
  const filteredVulns = filterSeverity === "all" 
    ? vulnerabilities 
    : vulnerabilities.filter(v => v.severity?.toLowerCase() === filterSeverity.toLowerCase());

  let attackSurface = {};
  try {
    if (scan.summary?.attack_surface) {
      attackSurface = typeof scan.summary.attack_surface === "string" 
        ? JSON.parse(scan.summary.attack_surface)
        : scan.summary.attack_surface;
    }
  } catch (e) {
    attackSurface = {};
  }

  const tabs = [
    { id: "overview", label: "Overview", icon: Search },
    { id: "vulnerabilities", label: "Vulnerabilities", icon: AlertTriangle, count: filteredVulns.length },
    { id: "raw", label: "Raw Output", icon: FileText },
    { id: "report", label: "Report", icon: Download },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-6 py-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold">{scan.target}</h1>
            <p className="text-sm text-muted-foreground">
              {formatDateTime(scan.scan_date)} • {scan.tools_used?.length || 0} tools
            </p>
          </div>
          <div className="flex items-center gap-3">
            <RiskBadge risk={scan.overall_risk} />
            <button onClick={downloadReport} disabled={downloading} className="btn btn-secondary">
              <Download className="mr-2 h-4 w-4" />
              {downloading ? "Downloading..." : "PDF Report"}
            </button>
            <button onClick={startNewScan} className="btn btn-primary">
              <Play className="mr-2 h-4 w-4" />
              Re-scan
            </button>
          </div>
        </div>

        <div className="mb-6 flex gap-2 border-b border-border">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors",
                  activeTab === tab.id
                    ? "border-accent text-accent"
                    : "border-transparent text-muted-foreground hover:text-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {tab.label}
                {tab.count !== undefined && (
                  <span className="ml-1 rounded-full bg-border px-2 py-0.5 text-xs">
                    {tab.count}
                  </span>
                )}
              </button>
            );
          })}
        </div>

        {activeTab === "overview" && (
          <div className="space-y-6">
            {scan.summary?.executive_summary && (
              <div className="card border-l-4 border-l-accent p-6">
                <h2 className="mb-2 text-lg font-semibold">Executive Summary</h2>
                <p className="text-muted-foreground">{scan.summary.executive_summary}</p>
              </div>
            )}

            <div className="grid gap-6 lg:grid-cols-2">
              <div className="card p-6">
                <h3 className="mb-4 text-lg font-semibold">Attack Surface</h3>
                
                {attackSurface.open_ports && attackSurface.open_ports.length > 0 && (
                  <div className="mb-4">
                    <h4 className="mb-2 text-sm font-medium">Open Ports</h4>
                    <div className="flex flex-wrap gap-2">
                      {attackSurface.open_ports.map((port, i) => (
                        <span
                          key={i}
                          className="rounded border border-border bg-background px-2 py-1 font-mono text-sm"
                        >
                          {port.port}/{port.protocol}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {attackSurface.technologies && attackSurface.technologies.length > 0 && (
                  <div>
                    <h4 className="mb-2 text-sm font-medium">Technologies</h4>
                    <div className="flex flex-wrap gap-2">
                      {attackSurface.technologies.map((tech, i) => (
                        <span
                          key={i}
                          className="rounded bg-accent/20 px-2 py-1 text-sm text-accent"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="card p-6">
                <h3 className="mb-4 text-lg font-semibold">Vulnerability Summary</h3>
                <div className="space-y-3">
                  {["Critical", "High", "Medium", "Low", "Info"].map((severity) => {
                    const count = vulnerabilities.filter(
                      (v) => v.severity?.toLowerCase() === severity.toLowerCase()
                    ).length;
                    return (
                      <div key={severity} className="flex items-center justify-between">
                        <span className={cn(
                          "text-sm",
                          severity === "Critical" && "text-destruct",
                          severity === "High" && "text-orange-400",
                          severity === "Medium" && "text-warning",
                          severity === "Low" && "text-success",
                          severity === "Info" && "text-accent"
                        )}>{severity}</span>
                        <span className="font-mono">{count}</span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === "vulnerabilities" && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-2">
              {["all", "Critical", "High", "Medium", "Low", "Info"].map((severity) => (
                <button
                  key={severity}
                  onClick={() => setFilterSeverity(severity)}
                  className={cn(
                    "rounded-lg border px-3 py-1 text-sm font-medium transition-colors",
                    filterSeverity === severity
                      ? "border-accent bg-accent/10 text-accent"
                      : "border-border text-muted-foreground hover:border-accent"
                  )}
                >
                  {severity.charAt(0).toUpperCase() + severity.slice(1)}
                </button>
              ))}
            </div>

            {filteredVulns.length === 0 ? (
              <div className="card p-8 text-center">
                <p className="text-muted-foreground">No vulnerabilities found</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredVulns.map((vuln, index) => (
                  <VulnCard key={index} vulnerability={vuln} />
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "raw" && (
          <div className="space-y-4">
            <h2 className="text-lg font-semibold">Raw Tool Output</h2>
            {scan.summary?.raw_outputs && (
              <div className="card overflow-hidden">
                <div className="max-h-[600px] overflow-auto p-4">
                  <pre className="font-mono text-sm text-success whitespace-pre-wrap">
                    {scan.summary.raw_outputs}
                  </pre>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === "report" && (
          <div className="space-y-6">
            <div className="card p-6">
              <h2 className="mb-4 text-lg font-semibold">Report Preview</h2>
              <p className="text-muted-foreground">
                The PDF report includes all findings, attack surface analysis, 
                remediation steps, and executive summary.
              </p>
              <button
                onClick={downloadReport}
                disabled={downloading}
                className="btn btn-primary mt-4"
              >
                <Download className="mr-2 h-4 w-4" />
                {downloading ? "Generating..." : "Download PDF"}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}