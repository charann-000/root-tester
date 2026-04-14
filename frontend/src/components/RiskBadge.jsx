import { cn } from "../lib/utils";

export function RiskBadge({ risk, className }) {
  const colors = {
    Critical: "bg-destruct/20 text-destruct border-destruct",
    High: "bg-orange-500/20 text-orange-400 border-orange-500",
    Medium: "bg-warning/20 text-warning border-warning",
    Low: "bg-success/20 text-success border-success",
    Info: "bg-accent/20 text-accent border-accent",
    Unknown: "bg-border text-muted-foreground border-border",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
        colors[risk] || colors.Unknown,
        className
      )}
    >
      {risk || "Unknown"}
    </span>
  );
}