import subprocess
import asyncio
import json
import shutil
import os
import re
from typing import Dict, Any, Optional
from datetime import datetime

TOOL_TIMEOUTS = {
    "nmap": 120,
    "masscan": 60,
    "rustscan": 90,
    "nikto": 300,
    "whatweb": 180,
    "gobuster": 180,
    "wfuzz": 180,
    "curl_headers": 30,
    "dig": 30,
    "dnsenum": 120,
    "sublist3r": 120,
    "sslscan": 60,
    "testssl": 240,
    "whois": 30,
    "theHarvester": 120,
    "default": 90
}

def check_tool_available(tool_name: str) -> bool:
    return shutil.which(tool_name) is not None

def get_available_tools() -> Dict[str, bool]:
    tools = ["nmap", "masscan", "rustcan", "nikto", "whatweb", "gobuster", "wfuzz", 
            "curl", "dig", "dnsenum", "sublist3r", "sslscan", "testssl.sh", "whois", "theHarvester"]
    return {tool: check_tool_available(tool) for tool in tools}

async def run_tool(
    tool: str, 
    target: str, 
    extra_args: Optional[list] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    start_time = datetime.now()
    timeout = timeout or TOOL_TIMEOUTS.get(tool, TOOL_TIMEOUTS["default"])
    
    cmd = build_command(tool, target, extra_args)
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/tmp" if os.name != "nt" else os.environ.get("TEMP", ".")
        )
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            duration = (datetime.now() - start_time).total_seconds()
            return {
                "tool": tool,
                "output": stdout.decode("utf-8", errors="replace"),
                "error": stderr.decode("utf-8", errors="replace"),
                "duration": round(duration, 2),
                "returncode": process.returncode
            }
        except asyncio.TimeoutError:
            process.kill()
            duration = (datetime.now() - start_time).total_seconds()
            return {
                "tool": tool,
                "output": "",
                "error": f"Tool timed out after {timeout}s",
                "duration": round(duration, 2),
                "returncode": -1,
                "timed_out": True
            }
    except FileNotFoundError:
        return {
            "tool": tool,
            "output": "",
            "error": f"Tool '{tool}' not found. Is it installed?",
            "duration": 0,
            "returncode": -1
        }
    except Exception as e:
        return {
            "tool": tool,
            "output": "",
            "error": str(e),
            "duration": 0,
            "returncode": -1
        }

def build_command(tool: str, target: str, extra_args: Optional[list] = None) -> list:
    extra = extra_args or []
    
    commands = {
        "nmap": ["nmap", "-sV", "-sC", "-O", "-A", "--script=vuln,http-headers,ssl-enum-ciphers", target] + extra,
        "masscan": ["masscan", target, "-p1-65535", "--rate=1000"] + extra,
        "rustscan": ["rustscan", "-a", target, "--ulimit", "5000", "--", "-sV", "-sC"] + extra,
        "nikto": ["nikto", "-h", target, "-Format", "txt"] + extra,
        "whatweb": ["whatweb", "-a", "3", target] + extra,
        "gobuster": ["gobuster", "dir", "-u", f"http://{target}", "-w", "/usr/share/wordlists/dirb/common.txt", "-t", "50"] + extra,
        "wfuzz": ["wfuzz", "-c", "-z", "file,/usr/share/wordlists/dirb/common.txt", "--hc", "404", f"http://{target}/FUZZ"] + extra,
        "curl_headers": ["curl", "-I", "-L", "--max-time", "10", target] + extra,
        "dig": ["dig", target, "ANY", "+noall", "+answer"] + extra,
        "dnsenum": ["dnsenum", "--noreverse", target] + extra,
        "sublist3r": ["sublist3r", "-d", target] + extra,
        "sslscan": ["sslscan", "--no-colour", target] + extra,
        "testssl": ["testssl.sh", "--json", f"/tmp/ssl_{int(datetime.now().timestamp())}.json", target] + extra,
        "whois": ["whois", target] + extra,
        "theHarvester": ["theHarvester", "-d", target, "-b", "google,bing,duckduckgo", "-l", "100"] + extra,
    }
    
    return commands.get(tool, [tool, target] + extra)

async def run_nmap(target: str) -> Dict[str, Any]:
    return await run_tool("nmap", target)

async def run_masscan(target: str) -> Dict[str, Any]:
    return await run_tool("masscan", target)

async def run_rustscan(target: str) -> Dict[str, Any]:
    return await run_tool("rustscan", target)

async def run_nikto(target: str) -> Dict[str, Any]:
    return await run_tool("nikto", target)

async def run_whatweb(target: str) -> Dict[str, Any]:
    return await run_tool("whatweb", target)

async def run_gobuster(target: str) -> Dict[str, Any]:
    return await run_tool("gobuster", target)

async def run_wfuzz(target: str) -> Dict[str, Any]:
    return await run_tool("wfuzz", target)

async def run_curl_headers(target: str) -> Dict[str, Any]:
    return await run_tool("curl_headers", target)

async def run_dig(target: str) -> Dict[str, Any]:
    result = await run_tool("dig", target)
    mx_result = await run_tool("dig", target, ["MX"])
    txt_result = await run_tool("dig", target, ["TXT"])
    ns_result = await run_tool("dig", target, ["NS"])
    
    return {
        "tool": "dig",
        "output": result["output"] + "\n\nMX Records:\n" + mx_result["output"] + 
                  "\n\nTXT Records:\n" + txt_result["output"] + 
                  "\n\nNS Records:\n" + ns_result["output"],
        "error": result["error"],
        "duration": result["duration"],
        "returncode": result["returncode"]
    }

async def run_dnsenum(target: str) -> Dict[str, Any]:
    return await run_tool("dnsenum", target)

async def run_sublist3r(target: str) -> Dict[str, Any]:
    return await run_tool("sublist3r", target)

async def run_sslscan(target: str) -> Dict[str, Any]:
    return await run_tool("sslscan", target)

async def run_testssl(target: str) -> Dict[str, Any]:
    return await run_tool("testssl", target)

async def run_whois(target: str) -> Dict[str, Any]:
    return await run_tool("whois", target)

async def run_theHarvester(target: str) -> Dict[str, Any]:
    return await run_tool("theHarvester", target)

TOOL_MAP = {
    "nmap": run_nmap,
    "masscan": run_masscan,
    "rustscan": run_rustscan,
    "nikto": run_nikto,
    "whatweb": run_whatweb,
    "gobuster": run_gobuster,
    "wfuzz": run_wfuzz,
    "curl_headers": run_curl_headers,
    "dig": run_dig,
    "dnsenum": run_dnsenum,
    "sublist3r": run_sublist3r,
    "sslscan": run_sslscan,
    "testssl": run_testssl,
    "whois": run_whois,
    "theHarvester": run_theHarvester,
}

async def run_tool_by_name(tool_name: str, target: str) -> Dict[str, Any]:
    if tool_name in TOOL_MAP:
        return await TOOL_MAP[tool_name](target)
    return await run_tool(tool_name, target)

PRESETS = {
    "quick": ["nmap", "whois", "curl_headers", "dig"],
    "full": ["nmap", "nikto", "whatweb", "gobuster", "wfuzz", "curl_headers", "dig", "dnsenum", "sublist3r", "sslscan", "whois", "theHarvester"],
    "web": ["nikto", "whatweb", "gobuster", "wfuzz", "curl_headers"],
    "network": ["nmap", "masscan", "rustscan"],
    "dns": ["dig", "dnsenum", "sublist3r"],
    "ssl": ["sslscan", "testssl"],
    "osint": ["whois", "theHarvester"]
}

def get_tools_for_preset(preset: str) -> list:
    return PRESETS.get(preset, PRESETS["quick"])

def parse_nmap_output(output: str) -> dict:
    ports = []
    services = []
    os_info = ""
    
    port_pattern = r"(\d+)/(\w+)\s+(\w+)\s+(\S+)"
    for match in re.finditer(port_pattern, output):
        port, proto, state, service = match.groups()
        ports.append({"port": port, "protocol": proto, "state": state, "service": service})
    
    return {"ports": ports, "services": services, "os": os_info}

def parse_nikto_output(output: str) -> dict:
    findings = []
    lines = output.split("\n")
    for line in lines:
        if "+" in line and ("vulnerability" in line.lower() or "issue" in line.lower() or "error" in line.lower()):
            findings.append(line.strip())
    return {"findings": findings}

def parse_whois_output(output: str) -> dict:
    data = {}
    key_pattern = r"^(Domain|Registrar|Creation|Expiry|Name Server|Registrant|Admin|Abuse)[^:]*:\s*(.+)$"
    for match in re.finditer(key_pattern, output, re.MULTILINE):
        key, value = match.groups()
        data[key.strip()] = value.strip()
    return data