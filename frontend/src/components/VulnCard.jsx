import { ExternalLink, AlertTriangle } from "lucide-react";
import { cn, getSeverityColor } from "../lib/utils";

export function VulnCard({ vulnerability, className }) {
  const { vuln_id, name, severity, cvss_score, affected_port, affected_service, description, evidence, cve_ids } = vulnerability;
  
  const severityClass = getSeverityColor(severity);

  return (
    <div className={cn("card overflow-hidden", className)}>
      <div className={cn("h-1 w-full", severityClass.split(" ")[2] || "bg-accent")} />
      <div className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="text-sm font-mono text-muted-foreground">{vuln_id}</span>
            <h3 className="text-lg font-semibold">{name}</h3>
          </div>
          <span
            className={cn(
              "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium",
              severityClass
            )}
          >
            {severity}
          </span>
        </div>

        {cvss_score !== undefined && cvss_score !== null && (
          <div className="mt-2 flex items-center gap-2">
            <span className="text-sm text-muted-foreground">CVSS:</span>
            <div className="flex items-center gap-1">
              {[...Array(10)].map((_, i) => (
                <div
                  key={i}
                  className={cn(
                    "h-2 w-2 rounded-full",
                    i < cvss_score ? "bg-accent" : "bg-border"
                  )}
                />
              ))}
              <span className="ml-2 text-sm font-medium">{cvss_score}</span>
            </div>
          </div>
        )}

        <div className="mt-2 flex flex-wrap gap-2 text-sm text-muted-foreground">
          {affected_port && (
            <span className="flex items-center gap-1">
              <span className="font-medium">Port:</span> {affected_port}
            </span>
          )}
          {affected_service && (
            <span className="flex items-center gap-1">
              <span className="font-medium">Service:</span> {affected_service}
            </span>
          )}
        </div>

        {cve_ids && cve_ids.length > 0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {cve_ids.map((cve) => (
              <a
                key={cve}
                href={`https://nvd.nist.gov/vuln/detail/${cve}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-sm text-accent hover:underline"
              >
                {cve}
                <ExternalLink className="h-3 w-3" />
              </a>
            ))}
          </div>
        )}

        {description && (
          <p className="mt-3 text-sm text-muted-foreground">{description}</p>
        )}

        {evidence && (
          <div className="mt-3 rounded border border-border bg-background p-3">
            <pre className="font-mono text-xs text-success whitespace-pre-wrap">{evidence}</pre>
          </div>
        )}
      </div>
    </div>
  );
}