import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Loader2, Search, Trash2, Download, Eye } from "lucide-react";
import axios from "axios";
import { useAuth } from "../hooks/useAuth";
import { Navbar } from "../components/Navbar";
import { RiskBadge } from "../components/RiskBadge";
import { formatDateTime, cn } from "../lib/utils";

export function History() {
  const { user, loading: authLoading } = useAuth();
  const [scans, setScans] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [filterRisk, setFilterRisk] = useState("all");
  const [deleting, setDeleting] = useState(null);

  useEffect(() => {
    if (!authLoading && user) {
      fetchScans();
    }
  }, [user, authLoading]);

  const fetchScans = async () => {
    try {
      const response = await axios.get("/api/history");
      setScans(response.data);
    } catch (error) {
      console.error("Failed to fetch history:", error);
    } finally {
      setLoading(false);
    }
  };

  const deleteScan = async (scanId) => {
    if (!confirm("Are you sure you want to delete this scan?")) return;
    
    setDeleting(scanId);
    try {
      await axios.delete(`/api/scan/${scanId}`);
      setScans(scans.filter(s => s.id !== scanId));
    } catch (error) {
      console.error("Failed to delete scan:", error);
    } finally {
      setDeleting(null);
    }
  };

  const downloadReport = async (scanId, target) => {
    try {
      const response = await axios.get(`/api/report/${scanId}`, {
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `metatron_${target}_${scanId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to download report:", error);
    }
  };

  const filteredScans = scans.filter(scan => {
    const matchesSearch = !search || scan.target.toLowerCase().includes(search.toLowerCase());
    const matchesRisk = filterRisk === "all" || scan.overall_risk?.toLowerCase() === filterRisk.toLowerCase();
    return matchesSearch && matchesRisk;
  });

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-6 py-8">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <h1 className="text-2xl font-bold">Scan History</h1>
        </div>

        <div className="mb-6 flex flex-wrap gap-4">
          <div className="relative flex-1 min-w-[200px]">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by target..."
              className="input pl-10"
            />
          </div>
          <select
            value={filterRisk}
            onChange={(e) => setFilterRisk(e.target.value)}
            className="input w-auto"
          >
            <option value="all">All Risks</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>

        {filteredScans.length === 0 ? (
          <div className="card p-8 text-center">
            <p className="text-muted-foreground">No scans found</p>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="border-b border-border bg-card">
                  <tr>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Target</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Date</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Risk</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Tools</th>
                    <th className="px-4 py-3 text-left text-sm font-medium text-muted-foreground">Vulns</th>
                    <th className="px-4 py-3 text-right text-sm font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredScans.map((scan) => (
                    <tr key={scan.id} className="hover:bg-border/30">
                      <td className="px-4 py-3">
                        <Link
                          to={`/scan/results/${scan.id}`}
                          className="font-medium text-accent hover:underline"
                        >
                          {scan.target}
                        </Link>
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {formatDateTime(scan.scan_date)}
                      </td>
                      <td className="px-4 py-3">
                        <RiskBadge risk={scan.overall_risk} />
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {scan.tools_used?.length || 0}
                      </td>
                      <td className="px-4 py-3 text-sm text-muted-foreground">
                        {scan.vuln_count}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center justify-end gap-2">
                          <Link
                            to={`/scan/results/${scan.id}`}
                            className="rounded p-2 text-muted-foreground hover:bg-border hover:text-foreground"
                            title="View"
                          >
                            <Eye className="h-4 w-4" />
                          </Link>
                          <button
                            onClick={() => downloadReport(scan.id, scan.target)}
                            className="rounded p-2 text-muted-foreground hover:bg-border hover:text-foreground"
                            title="Download PDF"
                          >
                            <Download className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => deleteScan(scan.id)}
                            disabled={deleting === scan.id}
                            className="rounded p-2 text-muted-foreground hover:bg-border hover:text-destruct"
                            title="Delete"
                          >
                            <Trash2 className="h-4 w-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}