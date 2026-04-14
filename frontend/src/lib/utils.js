import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  return date.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getSeverityColor(severity) {
  switch (severity?.toLowerCase()) {
    case "critical":
      return "text-destruct bg-destruct/20 border-destruct";
    case "high":
      return "text-orange-400 bg-orange-500/20 border-orange-500";
    case "medium":
      return "text-warning bg-warning/20 border-warning";
    case "low":
      return "text-success bg-success/20 border-success";
    default:
      return "text-accent bg-accent/20 border-accent";
  }
}

export function getRiskColor(risk) {
  switch (risk?.toLowerCase()) {
    case "critical":
      return "#F85149";
    case "high":
      return "#F0883E";
    case "medium":
      return "#D29922";
    case "low":
      return "#3FB950";
    default:
      return "#58A6FF";
  }
}