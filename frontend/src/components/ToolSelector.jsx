import { Check, Network, Globe, Lock, Search, User } from "lucide-react";
import { cn } from "../lib/utils";

const TOOL_GROUPS = {
  "Network Scanning": {
    icon: Network,
    tools: [
      { id: "nmap", name: "nmap", desc: "Port scanning, service detection, OS fingerprint, vuln scripts" },
      { id: "masscan", name: "masscan", desc: "Ultra-fast full port scanner" },
      { id: "rustscan", name: "rustscan", desc: "Fastest port scanner, feeds to nmap" },
    ],
  },
  "Web Application": {
    icon: Globe,
    tools: [
      { id: "nikto", name: "nikto", desc: "Web server vulnerability scanner" },
      { id: "whatweb", name: "whatweb", desc: "Web technology fingerprinting" },
      { id: "gobuster", name: "gobuster", desc: "Directory and file brute-forcing" },
      { id: "wfuzz", name: "wfuzz", desc: "Web fuzzer for hidden endpoints" },
      { id: "curl_headers", name: "curl_headers", desc: "HTTP response headers check" },
    ],
  },
  "DNS & Subdomains": {
    icon: Search,
    tools: [
      { id: "dig", name: "dig", desc: "DNS record enumeration (A, MX, TXT, NS)" },
      { id: "dnsenum", name: "dnsenum", desc: "DNS brute-force, zone transfers" },
      { id: "sublist3r", name: "sublist3r", desc: "Subdomain enumeration" },
    ],
  },
  "SSL/TLS": {
    icon: Lock,
    tools: [
      { id: "sslscan", name: "sslscan", desc: "SSL/TLS cipher strength, certificates" },
      { id: "testssl", name: "testssl", desc: "Comprehensive TLS testing" },
    ],
  },
  "OSINT": {
    icon: User,
    tools: [
      { id: "whois", name: "whois", desc: "Domain registration lookup" },
      { id: "theHarvester", name: "theHarvester", desc: "OSINT email/subdomain harvest" },
    ],
  },
};

const PRESETS = {
  quick: { name: "Quick Scan", tools: ["nmap", "whois", "curl_headers", "dig"], description: "Fast reconnaissance" },
  full: { name: "Full Scan", tools: ["nmap", "masscan", "nikto", "whatweb", "gobuster", "wfuzz", "curl_headers", "dig", "dnsenum", "sublist3r", "sslscan", "whois", "theHarvester"], description: "Comprehensive testing" },
  web: { name: "Web Focus", tools: ["nikto", "whatweb", "gobuster", "wfuzz", "curl_headers"], description: "Web application testing" },
};

export function ToolSelector({ selectedTools, onChange }) {
  const toggleTool = (toolId) => {
    if (selectedTools.includes(toolId)) {
      onChange(selectedTools.filter((t) => t !== toolId));
    } else {
      onChange([...selectedTools, toolId]);
    }
  };

  const selectPreset = (preset) => {
    onChange(PRESETS[preset].tools);
  };

  const isPresetActive = (preset) => {
    const presetTools = PRESETS[preset].tools;
    return presetTools.every((t) => selectedTools.includes(t)) && selectedTools.length === presetTools.length;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        {Object.entries(PRESETS).map(([key, preset]) => (
          <button
            key={key}
            onClick={() => selectPreset(key)}
            className={cn(
              "rounded-lg border px-4 py-2 text-sm font-medium transition-colors",
              isPresetActive(key)
                ? "border-accent bg-accent/10 text-accent"
                : "border-border text-muted-foreground hover:border-accent hover:text-foreground"
            )}
          >
            {preset.name}
          </button>
        ))}
      </div>

      <div className="space-y-4">
        {Object.entries(TOOL_GROUPS).map(([groupName, group]) => {
          const Icon = group.icon;
          return (
            <div key={groupName} className="card p-4">
              <div className="mb-3 flex items-center gap-2">
                <Icon className="h-5 w-5 text-accent" />
                <h3 className="font-semibold">{groupName}</h3>
              </div>
              <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                {group.tools.map((tool) => (
                  <label
                    key={tool.id}
                    className={cn(
                      "flex cursor-pointer items-start gap-3 rounded-lg border border-border p-3 transition-colors hover:bg-border/30",
                      selectedTools.includes(tool.id) && "border-accent bg-accent/10"
                    )}
                  >
                    <input
                      type="checkbox"
                      checked={selectedTools.includes(tool.id)}
                      onChange={() => toggleTool(tool.id)}
                      className="mt-1 h-4 w-4 accent-accent"
                    />
                    <div>
                      <p className="font-medium">{tool.name}</p>
                      <p className="text-xs text-muted-foreground">{tool.desc}</p>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}