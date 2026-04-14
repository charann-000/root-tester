# METATRON - Web-Based AI Penetration Testing Platform

A full-stack, web-based penetration testing platform inspired by the open-source CLI tool at github.com/sooryathejas/METATRON but rebuilt as a modern web application.

## Tech Stack

- **Frontend**: React.js + Vite + TailwindCSS
- **Backend**: Python - FastAPI
- **Database**: MariaDB with SQLAlchemy ORM
- **LLM**: API-based (Groq, OpenAI, or Anthropic - swappable via .env)
- **Real-time**: WebSockets for live scan output streaming
- **Search**: DuckDuckGo for CVE enrichment

## Project Structure

```
metatron-web/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py            # Configuration settings
│   ├── db.py                # SQLAlchemy models + CRUD
│   ├── auth_utils.py        # JWT helpers, password hashing
│   ├── tools.py             # 15 recon tools subprocess wrappers
│   ├── llm.py               # LLM API integration + agentic loop
│   ├── search.py            # DuckDuckGo CVE search
│   ├── report_generator.py # ReportLab PDF builder
│   ├── .env                # API keys, DB credentials
│   ├── routes/
│   │   ├── auth.py         # /api/auth/login, /register
│   │   ├── scan.py        # /api/scan (POST — start scan)
│   │   ├── history.py     # /api/history (GET/DELETE)
│   │   ├── report.py     # /api/report/{id} (GET — download PDF)
│   │   └── ws.py         # WebSocket /ws/scan/{id}
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/
    │   │   ├── Login.jsx
    │   │   ├── Register.jsx
    │   │   ├── Dashboard.jsx
    │   │   ├── NewScan.jsx
    │   │   ├── ScanLive.jsx  # live streaming output page
    │   │   ├── Results.jsx
    │   │   └── History.jsx
    │   ├── components/
    │   │   ├── Navbar.jsx
    │   │   ├── ToolSelector.jsx
    │   │   ├── VulnCard.jsx
    │   │   ├── RiskBadge.jsx
    │   │   └── LiveTerminal.jsx
    │   ├── hooks/
    │   │   ├── useWebSocket.js
    │   │   └── useAuth.js
    │   └── App.jsx
    └── package.json
```

## Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- MariaDB/MySQL

### Backend Setup

```bash
cd metatron-web/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Configure .env
# Edit .env with your database credentials and API keys

# Initialize database (will create tables)
python -c "from db import init_db; init_db()"

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd metatron-web/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Required Tools (for scanning)

Install these security tools on your system:
- nmap
- masscan
- rustscan
- nikto
- whatweb
- gobuster
- wfuzz
- dig
- dnsenum
- sublist3r
- sslscan
- testssl
- whois
- theHarvester

## Environment Variables

### Backend .env

```env
# Database
DB_HOST=localhost
DB_PORT=3306
DB_USER=metatron
DB_PASSWORD=metatron_pass
DB_NAME=metatron_db

# JWT
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# LLM (choose one: groq | openai | anthropic)
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.2

# App
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Features

- **15 Recon Tools**: nmap, masscan, rustscan, nikto, whatweb, gobuster, wfuzz, dig, dnsenum, sublist3r, sslscan, testssl, whois, theHarvester, curl
- **Tool Presets**: Quick Scan, Full Scan, Web Focus
- **Agentic Loop**: AI requests additional tools based on findings
- **CVE Enrichment**: DuckDuckGo search for patch information
- **PDF Reports**: Professional dark-themed reports
- **Real-time Streaming**: WebSocket-powered live terminal
- **JWT Authentication**: Secure login/register

## Disclaimer

METATRON is for authorized penetration testing only. Only scan systems you own or have explicit written permission to test. Unauthorized scanning is illegal.