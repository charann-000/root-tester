import { useEffect, useRef } from "react";
import { cn } from "../lib/utils";

export function LiveTerminal({ messages, className }) {
  const containerRef = useRef(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [messages]);

  const formatMessage = (msg) => {
    const type = msg.type;
    
    switch (type) {
      case "tool_start":
        return (
          <span>
            <span className="text-accent">[{msg.tool}]</span>{" "}
            <span className="text-muted-foreground">{msg.message}</span>
          </span>
        );
      case "tool_output":
        return (
          <span className="text-success">
            {msg.line}
          </span>
        );
      case "tool_done":
        return (
          <span>
            <span className="text-success">[{msg.tool}]</span>{" "}
            <span className="text-muted-foreground">completed in {msg.duration}s</span>
          </span>
        );
      case "llm_start":
        return (
          <span>
            <span className="text-warning">[*]</span>{" "}
            <span className="text-muted-foreground">{msg.message}</span>
          </span>
        );
      case "llm_done":
        return (
          <span>
            <span className="text-success">[*]</span>{" "}
            <span className="text-muted-foreground">{msg.message}</span>
          </span>
        );
      case "agent_trigger":
        return (
          <span>
            <span className="text-purple-400">[@]</span>{" "}
            <span className="text-muted-foreground">{msg.message}</span>
          </span>
        );
      case "scan_complete":
        return (
          <span className="text-success font-bold">
            [+] Scan complete! Risk level: {msg.risk}
          </span>
        );
      case "error":
        return (
          <span>
            <span className="text-destruct">[{msg.tool || 'ERROR'}]</span>{" "}
            <span className="text-destruct">{msg.message}</span>
          </span>
        );
      default:
        return <span>{JSON.stringify(msg)}</span>;
    }
  };

  return (
    <div
      ref={containerRef}
      className={cn(
        "h-full overflow-auto rounded-lg border border-border bg-background p-4 font-mono text-sm",
        className
      )}
    >
      {messages.length === 0 ? (
        <span className="text-muted-foreground">Waiting for scan to start...</span>
      ) : (
        messages.map((msg, index) => (
          <div key={index} className="mb-1 whitespace-pre-wrap">
            {formatMessage(msg)}
          </div>
        ))
      )}
    </div>
  );
}