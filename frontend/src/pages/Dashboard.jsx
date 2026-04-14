import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Shield, AlertTriangle, CheckCircle, Activity, Plus, Loader2 } from "lucide-react";
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts";
import axios from "axios";
import { useAuth } from "../hooks/useAuth";
import { Navbar } from "../components/Navbar";
import { RiskBadge } from "../components/RiskBadge";
import { formatDateTime, getRiskColor } from "../lib/utils";

export function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentScans, setRecentScans] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!authLoading && user) {
      fetchData();
    }
  }, [user, authLoading]);

  const fetchData = async () => {
    try {
      const [statsRes, historyRes] = await Promise.all([
        axios.get("/api/history/stats"),
        axios.get("/api/history?limit=5"),
      ]);
      setStats(statsRes.data);
      setRecentScans(historyRes.data);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const riskData = stats
    ? [
        { name: "Critical", value: stats.critical, color: "#F85149" },
        { name: "High", value: stats.high, color: "#F0883E" },
        { name: "Medium", value: stats.medium, color: "#D29922" },
        { name: "Low", value: stats.low, color: "#3FB950" },
      ].filter((d) => d.value > 0)
    : [];

  const statCards = [
    {
      label: "Total Scans",
      value: stats?.total || 0,
      icon: Shield,
      color: "text-accent",
    },
    {
      label: "Critical Findings",
      value: stats?.critical || 0,
      icon: AlertTriangle,
      color: "text-destruct",
    },
    {
      label: "High Findings",
      value: stats?.high || 0,
      icon: AlertTriangle,
      color: "text-orange-400",
    },
    {
      label: "Scans Complete",
      value: stats?.complete || 0,
      icon: CheckCircle,
      color: "text-success",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      <Navbar />
      <main className="container mx-auto px-6 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground">Welcome back, {user.username}</p>
          </div>
          <Link to="/scan/new" className="btn btn-primary">
            <Plus className="mr-2 h-4 w-4" />
            New Scan
          </Link>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="card p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                    <p className="text-3xl font-bold">{stat.value}</p>
                  </div>
                  <Icon className={`h-8 w-8 ${stat.color}`} />
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          <div className="card p-6">
            <h2 className="mb-4 text-xl font-semibold">Risk Distribution</h2>
            {riskData.length > 0 ? (
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={riskData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {riskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#161B22",
                        border: "1px solid #30363D",
                        borderRadius: "8px",
                      }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <div className="flex h-64 items-center justify-center text-muted-foreground">
                No vulnerability data yet
              </div>
            )}
          </div>

          <div className="card p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-xl font-semibold">Recent Scans</h2>
              <Link to="/history" className="text-sm text-accent hover:underline">
                View all
              </Link>
            </div>
            {recentScans.length > 0 ? (
              <div className="space-y-3">
                {recentScans.map((scan) => (
                  <Link
                    key={scan.id}
                    to={`/scan/results/${scan.id}`}
                    className="flex items-center justify-between rounded-lg border border-border p-3 transition-colors hover:bg-border/50"
                  >
                    <div>
                      <p className="font-medium">{scan.target}</p>
                      <p className="text-xs text-muted-foreground">
                        {formatDateTime(scan.scan_date)}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">
                        {scan.vuln_count} vulns
                      </span>
                      <RiskBadge risk={scan.overall_risk} />
                    </div>
                  </Link>
                ))}
              </div>
            ) : (
              <div className="flex h-32 items-center justify-center text-muted-foreground">
                No scans yet.{" "}
                <Link to="/scan/new" className="ml-1 text-accent hover:underline">
                  Start your first scan
                </Link>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}