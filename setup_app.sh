#!/usr/bin/env bash
set -e

# Navigate to project root
cd ~/Desktop/ScriptDoctor-AI

echo " Creating directory structure..."
mkdir -p src/agents src/tools src/templates tests

echo " Writing requirements.txt..."
cat << 'REQ' > requirements.txt
google-genai>=0.1.0
fastapi>=0.110.0
uvicorn>=0.28.0
python-dotenv>=1.0.0
httpx>=0.27.0
pydantic>=2.6.0
jinja2>=3.1.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
REQ

echo " Writing .env.example..."
cat << 'ENV' > .env.example
GEMINI_API_KEY=your_gemini_api_key_here
PARALLEL_API_KEY=your_parallel_api_key_here
ENV

echo " Writing Dockerfile..."
cat << 'DOCKER' > Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
DOCKER

echo " Writing src/tools/parallel_mcp.py..."
cat << 'PARALLEL' > src/tools/parallel_mcp.py
import os
import httpx
from typing import Dict, Any, List

class ParallelSearchTool:
    """Parallel Search MCP client for low-latency web research."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("PARALLEL_API_KEY", "")
        # Parallel Search MCP Endpoint
        self.mcp_url = "https://search.parallel.ai/mcp"

    async def execute_search(self, objective: str, search_queries: List[str]) -> Dict[str, Any]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "method": "tools/call",
            "params": {
                "name": "web_search",
                "arguments": {
                    "objective": objective,
                    "search_queries": search_queries,
                    "max_results": 3,
                    "excerpts": {"max_chars_per_result": 1200}
                }
            }
        }

        async with httpx.AsyncClient(timeout=12.0) as client:
            try:
                response = await client.post(self.mcp_url, json=payload, headers=headers)
                if response.status_code == 200:
                    return response.json()
                return {"error": f"Parallel API status: {response.status_code}"}
            except Exception as e:
                return {"error": f"Parallel Search failed: {str(e)}"}
PARALLEL

echo " Writing src/agents/script_doctor.py..."
cat << 'AGENT' > src/agents/script_doctor.py
import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List
from src.tools.parallel_mcp import ParallelSearchTool

class FactAssertion(BaseModel):
    line_number: int
    claim: str
    category: str = Field(description="HISTORICAL, MEDICAL, LEGAL_IP, or TECHNICAL")
    search_objective: str
    search_queries: List[str]

class ExtractedClaims(BaseModel):
    scene_location: str
    scene_time_period: str
    assertions: List[FactAssertion]

class AuditIssue(BaseModel):
    line_number: int
    claim: str
    severity: str = Field(description="HIGH, MEDIUM, or LOW")
    fact_check_verdict: str
    citations: List[str]
    suggested_rewrite: str

class ScriptAuditReport(BaseModel):
    scene_summary: str
    total_issues_found: int
    overall_risk_score: str
    audit_issues: List[AuditIssue]

class ScriptDoctorEngine:
    def __init__(self):
        self.client = genai.Client()
        self.parallel_tool = ParallelSearchTool()
        self.model_id = "gemini-3.5-flash"

    async def analyze_script_scene(self, script_text: str) -> ScriptAuditReport:
        extractor_prompt = f"""
        Extract factual, historical, medical, technical, or legal IP assertions from this screenplay.
        Formulate target search objectives for Parallel Search.
        
        SCREENPLAY:
        {script_text}
        """

        extraction_response = self.client.models.generate_content(
            model=self.model_id,
            contents=extractor_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ExtractedClaims,
                temperature=0.1
            )
        )
        
        extracted_data = ExtractedClaims.model_validate_json(extraction_response.text)

        grounding_data = []
        for assertion in extracted_data.assertions:
            search_result = await self.parallel_tool.execute_search(
                objective=assertion.search_objective,
                search_queries=assertion.search_queries
            )
            grounding_data.append({
                "line_number": assertion.line_number,
                "claim": assertion.claim,
                "category": assertion.category,
                "web_evidence": search_result
            })

        synthesis_prompt = f"""
        Synthesize the original script text with live ground-truth evidence provided by Parallel MCP.
        
        ORIGINAL SCRIPT:
        {script_text}
        
        PARALLEL WEB EVIDENCE:
        {json.dumps(grounding_data, indent=2)}
        
        Generate a line-by-line Script Coverage Audit with severity scores, citations, and screenwriter rewrites.
        """

        synthesis_response = self.client.models.generate_content(
            model=self.model_id,
            contents=synthesis_prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ScriptAuditReport,
                temperature=0.2
            )
        )

        return ScriptAuditReport.model_validate_json(synthesis_response.text)
AGENT

echo " Writing app.py..."
cat << 'APP' > app.py
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from src.agents.script_doctor import ScriptDoctorEngine

app = FastAPI(title="ScriptDoctor AI")
engine = ScriptDoctorEngine()

class ScriptRequest(BaseModel):
    script_text: str

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ScriptDoctor AI - Real-Time Screenplay Fact Check</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-slate-950 text-slate-100 font-sans p-8">
        <div class="max-w-6xl mx-auto">
            <header class="flex justify-between items-center mb-8 pb-4 border-b border-slate-800">
                <div>
                    <h1 class="text-3xl font-extrabold text-indigo-400 tracking-tight">🎬 ScriptDoctor AI</h1>
                    <p class="text-slate-400 text-sm mt-1">Screenplay Fact-Checking & IP Verification Engine | Gemini 3.5 & Parallel MCP</p>
                </div>
                <span class="bg-indigo-900/60 border border-indigo-700 text-indigo-300 text-xs px-3 py-1 rounded-full font-mono">Parallel Track</span>
            </header>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="flex flex-col">
                    <label class="block mb-2 text-sm font-semibold text-slate-300">Screenplay Excerpt</label>
                    <textarea id="scriptInput" rows="18" class="w-full p-4 bg-slate-900 rounded-lg border border-slate-800 text-sm font-mono focus:outline-none focus:border-indigo-500 text-slate-200 leading-relaxed resize-none" placeholder="INT. POLICE STATION - 1998&#10;&#10;Detective Miller pulls out his iPhone 15 and checks the timestamp..."></textarea>
                    <button onclick="analyzeScript()" class="mt-4 w-full bg-indigo-600 hover:bg-indigo-500 font-bold py-3 px-6 rounded-lg transition shadow-lg shadow-indigo-900/30">Run ScriptDoctor Audit</button>
                </div>
                <div class="flex flex-col">
                    <label class="block mb-2 text-sm font-semibold text-slate-300">Real-Time Risk Audit & Citations</label>
                    <div id="results" class="w-full h-[470px] p-5 bg-slate-900 rounded-lg border border-slate-800 overflow-y-auto text-sm">
                        <p class="text-slate-500 italic text-center mt-32">Paste a screenplay scene and click Run Audit to view real-time factual analysis.</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function analyzeScript() {
                const text = document.getElementById('scriptInput').value;
                const resultsDiv = document.getElementById('results');
                if(!text) return alert('Please enter script text!');
                
                resultsDiv.innerHTML = '<div class="flex items-center justify-center h-full"><p class="text-indigo-400 animate-pulse font-medium">Analyzing scene with Gemini Enterprise & Parallel Search MCP...</p></div>';
                
                try {
                    const res = await fetch('/api/audit', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({script_text: text})
                    });
                    const data = await res.json();
                    
                    let html = `<div class="mb-5 pb-3 border-b border-slate-800 flex justify-between items-center">
                        <div>
                            <h3 class="font-bold text-base text-slate-200">Scene Risk Profile</h3>
                            <p class="text-xs text-slate-400 mt-1">${data.scene_summary}</p>
                        </div>
                        <span class="px-3 py-1 bg-red-950/80 border border-red-700 text-red-300 font-bold text-xs rounded">${data.overall_risk_score}</span>
                    </div>`;
                    
                    data.audit_issues.forEach(issue => {
                        html += `<div class="mb-4 p-4 bg-slate-950 rounded-lg border-l-4 ${issue.severity === 'HIGH' ? 'border-red-500' : 'border-amber-500'} border-y border-r border-slate-800/80">
                            <div class="flex justify-between font-semibold text-xs mb-2">
                                <span class="text-slate-400 font-mono">LINE ${issue.line_number}</span>
                                <span class="${issue.severity === 'HIGH' ? 'text-red-400' : 'text-amber-400'} font-bold">${issue.severity} RISK</span>
                            </div>
                            <p class="font-medium text-slate-200 mb-2">"${issue.claim}"</p>
                            <p class="text-xs text-slate-400 mb-3 leading-relaxed">${issue.fact_check_verdict}</p>
                            <div class="text-xs text-indigo-300 bg-indigo-950/40 p-3 rounded border border-indigo-900/40">
                                <strong class="text-indigo-200 block mb-1">Suggested Rewrite:</strong> ${issue.suggested_rewrite}
                            </div>
                        </div>`;
                    });
                    resultsDiv.innerHTML = html;
                } catch(e) {
                    resultsDiv.innerHTML = '<p class="text-red-400">Error conducting script audit.</p>';
                }
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/audit")
async def audit_script(request: ScriptRequest):
    try:
        report = await engine.analyze_script_scene(request.script_text)
        return report.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
APP

echo " Writing tests/test_app.py..."
cat << 'TEST' > tests/test_app.py
import pytest
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_homepage_render():
    response = client.get("/")
    assert response.status_code == 200
    assert "ScriptDoctor AI" in response.text
TEST

echo " Creating module __init__ files..."
touch src/__init__.py src/agents/__init__.py src/tools/__init__.py

echo " Staging, committing, and pushing code to GitHub..."
git add .
git commit -m "feat: complete ScriptDoctor AI bi-agent engine, UI, Dockerfile, and Parallel MCP integration"
git push origin main

echo " All code generated and pushed successfully!"
