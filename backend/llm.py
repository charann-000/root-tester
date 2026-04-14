import os
import json
from typing import Optional, Dict, Any, List
from openai import OpenAI
from config import get_settings

settings = get_settings()

SYSTEM_PROMPT = """You are METATRON, an expert AI penetration testing assistant. Your role is to analyze the output of various security scanning tools and provide structured vulnerability assessments.

When analyzing tool outputs, you must:
1. Output ONLY valid JSON - no prose, no markdown code fences
2. Be evidence-based - never hallucinate CVEs or vulnerabilities not supported by the tool output
3. Use the exact JSON schema specified in each analysis request
4. Assign realistic CVSS scores based on the severity of findings
5. Map vulnerabilities to known CVEs when evidence supports it

JSON Output Schema:
{
  "target": "string",
  "scan_timestamp": "ISO8601 timestamp",
  "overall_risk_level": "Critical|High|Medium|Low|Info",
  "executive_summary": "2-3 sentence summary of findings",
  "vulnerabilities": [
    {
      "vuln_id": "VLN-001",
      "name": "Vulnerability name",
      "severity": "Critical|High|Medium|Low|Info",
      "cvss_score": 0.0,
      "cve_ids": ["CVE-XXXX-XXXX"],
      "affected_port": "80/tcp",
      "affected_service": "Apache httpd",
      "description": "What the vulnerability is",
      "evidence": "Raw tool output supporting this finding",
      "attack_vector": "Network|Adjacent|Local|Physical",
      "exploitability": "High|Medium|Low"
    }
  ],
  "attack_surface": {
    "open_ports": [{"port": "80", "protocol": "tcp", "service": "http"}],
    "technologies": ["Apache 2.4.49", "PHP 7.4"],
    "dns_records": {"A": "1.2.3.4", "MX": "mail.target.com"},
    "security_headers": {"hsts": false, "csp": false, "xframe": false}
  },
  "exploit_suggestions": [
    {
      "vuln_id": "VLN-001",
      "exploit_name": "metasploit module or tool name",
      "tool": "metasploit/nmap/custom",
      "payload": "example payload if applicable",
      "difficulty": "High|Medium|Low"
    }
  ],
  "fixes": [
    {
      "vuln_id": "VLN-001",
      "fix_summary": "Short fix description",
      "fix_detail": "Detailed remediation steps",
      "patch_ref": "URL to patch/advisory",
      "priority": "Immediate|Short-term|Long-term"
    }
  ],
  "additional_recon_suggested": [
    {"tool": "gobuster", "command": "gobuster dir -u http://target -w wordlist", "reason": "Discover hidden directories"}
  ],
  "pentest_notes": "Any chaining observations or further testing recommendations"
}

Temperature should be 0.2 for consistent structured output. Always prioritize evidence over theoretical vulnerabilities."""

def get_llm_client() -> OpenAI:
    provider = os.getenv("LLM_PROVIDER", "groq")
    
    if provider == "groq":
        return OpenAI(
            api_key=os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY),
            base_url="https://api.groq.com/openai/v1"
        )
    elif provider == "openai":
        return OpenAI(
            api_key=os.getenv("OPENAI_API_KEY", settings.OPENAI_API_KEY)
        )
    elif provider == "anthropic":
        return OpenAI(
            api_key=os.getenv("ANTHROPIC_API_KEY", settings.ANTHROPIC_API_KEY),
            base_url="https://api.anthropic.com/v1"
        )
    else:
        return OpenAI(
            api_key=os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY),
            base_url="https://api.groq.com/openai/v1"
        )

async def analyze_with_llm(tool_results: Dict[str, Any], target: str) -> Dict[str, Any]:
    client = get_llm_client()
    model = os.getenv("LLM_MODEL", settings.LLM_MODEL)
    temperature = float(os.getenv("LLM_TEMPERATURE", str(settings.LLM_TEMPERATURE)))
    
    combined_output = ""
    for tool_name, result in tool_results.items():
        if isinstance(result, dict):
            output = result.get("output", "")
            error = result.get("error", "")
            combined_output += f"\n\n=== {tool_name.upper()} ===\n"
            if output:
                combined_output += output
            if error:
                combined_output += f"\nERROR: {error}"
    
    prompt = f"""Analyze the following security scan tool outputs for target: {target}

{combined_output}

{SYSTEM_PROMPT}

Return your analysis as valid JSON only. Include all fields in the schema."""

    try:
        if settings.LLM_PROVIDER == "anthropic":
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze these results for {target}:\n{combined_output}"}
                ],
                temperature=temperature,
                max_tokens=8192
            )
            response = completion.choices[0].message.content
        else:
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze these results for {target}:\n{combined_output}"}
                ],
                temperature=temperature,
                max_tokens=8192
            )
            response = completion.choices[0].message.content
        
        if "```json" in response:
            response = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            response = response.split("```")[1].split("```")[0]
        
        analysis = json.loads(response.strip())
        return analysis
    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse LLM response as JSON: {str(e)}",
            "target": target,
            "overall_risk_level": "Unknown",
            "vulnerabilities": [],
            "additional_recon_suggested": []
        }
    except Exception as e:
        return {
            "error": f"LLM analysis failed: {str(e)}",
            "target": target,
            "overall_risk_level": "Unknown",
            "vulnerabilities": [],
            "additional_recon_suggested": []
        }

async def agentic_loop(
    target: str, 
    initial_results: Dict[str, Any], 
    scan_id: int,
    auto_recon: bool = True
) -> Dict[str, Any]:
    if not auto_recon:
        return initial_results
    
    loop_count = 0
    max_loops = 3
    current_results = initial_results.copy()
    analysis = initial_results.get("llm_analysis", {})
    
    while analysis.get("additional_recon_suggested") and loop_count < max_loops:
        loop_count += 1
        
        for suggestion in analysis["additional_recon_suggested"]:
            tool = suggestion.get("tool")
            cmd = suggestion.get("command", "")
            
            if tool and tool in ["gobuster", "nikto", "wfuzz", "nmap", "sslscan"]:
                from tools import run_tool_by_name
                result = await run_tool_by_name(tool, target)
                current_results[tool] = result
        
        analysis = await analyze_with_llm(current_results, target)
    
    return analysis