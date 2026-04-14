import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Loader2, AlertTriangle, AlertCircle, CheckCircle } from "lucide-react";
import axios from "axios";
import { useAuth } from "../hooks/useAuth";
import { Navbar } from "../components/Navbar";
import { ToolSelector } from "../components/ToolSelector";

export function NewScan() {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();
  
  const [target, setTarget] = useState("");
  const [selectedTools, setSelectedTools] = useState(["nmap", "whois", "curl_headers", "dig"]);
  const [autoRecon, setAutoRecon] = useState(false);
  const [disclaimer, setDisclaimer] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const validateTarget = (value) => {
    if (!value) return null;
    const ipRegex = /^(\d{1,3}\.){3}\d{1,3}$/;
    const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9]?)*$/;
    const blocked = ["localhost", "127.", "192.168.", "10.", "0.0.0.0", "::1", "172.16.", "172.17.", "172.18.", "172.19.", "172.2", "172.30.", "172.31."];
    
    if (blocked.some(b => value.toLowerCase().startsWith(b))) {
      return { valid: false, message: "Internal/loopback addresses not allowed" };
    }
    if (ipRegex.test(value) || domainRegex.test(value)) {
      return { valid: true, message: "Valid target" };
    }
    return { valid: false, message: "Invalid format" };
  };

  const targetValidation = validateTarget(target);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (!targetValidation?.valid) {
      setError("Please enter a valid target IP or domain");
      return;
    }

    if (!disclaimer) {
      setError("You must accept the disclaimer before scanning");
      return;
    }

    if (selectedTools.length === 0) {
      setError("Please select at least one tool");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("/api/scan/start", {
        target,
        tools: selectedTools,
        preset: "custom",
        auto_recon: autoRecon,
        has_accepted_disclaimer: disclaimer ? 1 : 0,
      });
      navigate(`/scan/live/${response.data.scan_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to start scan");
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto max-w-4xl px-6 py-8">
        <h1 className="mb-8 text-3xl font-bold">New Scan</h1>

        {error && (
          <div className="mb-6 flex items-center gap-2 rounded-lg border border-destruct bg-destruct/10 p-4 text-destruct">
            <AlertCircle className="h-5 w-5" />
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-8">
          <div className="card p-6">
            <h2 className="mb-4 text-xl font-semibold">Target</h2>
            <div className="flex gap-4">
              <div className="relative flex-1">
                <input
                  type="text"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  placeholder="example.com or 192.168.1.1"
                  className="input pr-10"
                />
                {target && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2">
                    {targetValidation?.valid ? (
                      <CheckCircle className="h-5 w-5 text-success" />
                    ) : (
                      <AlertCircle className="h-5 w-5 text-destruct" />
                    )}
                  </div>
                )}
              </div>
            </div>
            {target && targetValidation && (
              <p className={`mt-2 text-sm ${targetValidation.valid ? "text-success" : "text-destruct"}`}>
                {targetValidation.message}
              </p>
            )}
          </div>

          <div className="card p-6">
            <h2 className="mb-4 text-xl font-semibold">Tool Selection</h2>
            <ToolSelector selectedTools={selectedTools} onChange={setSelectedTools} />
          </div>

          <div className="card p-6">
            <h2 className="mb-4 text-xl font-semibold">Options</h2>
            <label className="flex cursor-pointer items-center gap-3">
              <input
                type="checkbox"
                checked={autoRecon}
                onChange={(e) => setAutoRecon(e.target.checked)}
                className="h-5 w-5 accent-accent"
              />
              <div>
                <p className="font-medium">Enable Agentic Mode</p>
                <p className="text-sm text-muted-foreground">
                  AI will request additional tools based on findings
                </p>
              </div>
            </label>
          </div>

          <div className="card border-warning p-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-warning" />
              <div>
                <h3 className="font-semibold text-warning">Disclaimer</h3>
                <p className="mt-2 text-sm text-muted-foreground">
                  METATRON is for authorized penetration testing only. Only scan systems you own or have 
                  explicit written permission to test. Unauthorized scanning is illegal and may 
                  result in legal action.
                </p>
                <label className="mt-4 flex cursor-pointer items-center gap-3">
                  <input
                    type="checkbox"
                    checked={disclaimer}
                    onChange={(e) => setDisclaimer(e.target.checked)}
                    className="h-5 w-5 accent-accent"
                  />
                  <span className="text-sm">I understand and accept the disclaimer</span>
                </label>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading || !targetValidation?.valid || !disclaimer}
            className="btn btn-primary w-full"
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting Scan...
              </>
            ) : (
              "Start Scan"
            )}
          </button>
        </form>
      </main>
    </div>
  );
}