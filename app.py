import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from script_doctor import run_screenplay_audit

app = FastAPI(title="ScriptDoctor AI")

class AuditRequest(BaseModel):
    script_text: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScriptDoctor AI - Agentic Cinema Fact-Checker</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .pulse-loader { animation: spin 1s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen font-sans flex flex-col">

    <!-- Header -->
    <header class="border-b border-slate-800 bg-slate-900/50 px-8 py-4 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <span class="text-3xl">🎬</span>
            <div>
                <h1 class="text-xl font-bold bg-gradient-to-r from-purple-400 to-indigo-400 bg-clip-text text-transparent">ScriptDoctor AI</h1>
                <p class="text-xs text-slate-400">Screenplay Fact-Checking & Anachronism Engine | Gemini 3.5 & Parallel MCP</p>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <span class="px-3 py-1 text-xs rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">Agentic Cinema Track</span>
        </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1 p-6 max-w-7xl mx-auto w-full grid grid-cols-1 md:grid-cols-2 gap-6">

        <!-- Left Column: Screenplay Input -->
        <div class="flex flex-col gap-4">
            <div class="flex justify-between items-center">
                <h2 class="text-sm font-semibold tracking-wide text-slate-300 uppercase"><i class="fa-solid fa-file-lines mr-2"></i> Screenplay Excerpt</h2>
                <div class="flex gap-2">
                    <button onclick="loadSample(1)" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded transition">Sample 1 (1998)</button>
                    <button onclick="loadSample(2)" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-2 py-1 rounded transition">Sample 2 (1888)</button>
                </div>
            </div>

            <textarea id="scriptInput" class="w-full h-[500px] p-4 bg-slate-900 border border-slate-800 rounded-xl font-mono text-sm text-slate-200 focus:outline-none focus:border-indigo-500 transition resize-none leading-relaxed" placeholder="Paste your screenplay scene here..."></textarea>

            <button onclick="runAudit()" id="auditBtn" class="w-full py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-semibold rounded-xl text-white shadow-lg shadow-indigo-500/20 transition flex items-center justify-center gap-2">
                <i class="fa-solid fa-wand-magic-sparkles"></i>
                <span>Run Real-Time Audit</span>
            </button>
        </div>

        <!-- Right Column: Audit Results -->
        <div class="flex flex-col gap-4">
            <div class="flex justify-between items-center">
                <h2 class="text-sm font-semibold tracking-wide text-slate-300 uppercase"><i class="fa-solid fa-shield-halved mr-2"></i> Real-Time Risk Audit & Citations</h2>
                <span id="riskBadge" class="hidden px-2.5 py-0.5 text-xs font-semibold rounded-full"></span>
            </div>

            <div id="resultsContainer" class="w-full h-[500px] bg-slate-900 border border-slate-800 rounded-xl p-5 overflow-y-auto flex flex-col justify-center items-center text-center">
                <p id="placeholderText" class="text-slate-500 italic text-sm">Paste a screenplay scene and click <span class="text-indigo-400">Run Real-Time Audit</span> to analyze errors.</p>
                <div id="loader" class="hidden flex flex-col items-center gap-3">
                    <i class="fa-solid fa-circle-notch text-3xl text-indigo-500 pulse-loader"></i>
                    <p class="text-sm text-slate-400">Scanning historical facts & Parallel MCP search...</p>
                </div>
                <div id="auditOutput" class="hidden w-full text-left space-y-4"></div>
            </div>
            
            <button id="applyFixBtn" onclick="applyFix()" class="hidden w-full py-2.5 bg-slate-800 hover:bg-slate-700 text-emerald-400 border border-emerald-500/30 rounded-xl text-sm font-medium transition flex items-center justify-center gap-2">
                <i class="fa-solid fa-check"></i>
                <span>Auto-Fix Script Anachronism</span>
            </button>
        </div>
    </main>

    <script>
        const samples = {
            1: "INT. POLICE STATION - 1998\\n\\nDetective Miller pulls out his iPhone 15 and checks the timestamp...\\n\\nMILLER\\n(into phone)\\nWe need backup at downtown instantly.",
            2: "EXT. LONDON STREET - 1888\\n\\nInspector Abberline watches yellow taxi cabs drive down the asphalt road, checking his digital G-Shock wrist watch."
        };

        function loadSample(num) {
            document.getElementById('scriptInput').value = samples[num];
        }

        loadSample(1);
        let currentFix = "";

        async function runAudit() {
            const scriptText = document.getElementById('scriptInput').value;
            const loader = document.getElementById('loader');
            const placeholder = document.getElementById('placeholderText');
            const auditOutput = document.getElementById('auditOutput');
            const riskBadge = document.getElementById('riskBadge');
            const applyFixBtn = document.getElementById('applyFixBtn');

            if (!scriptText.trim()) return;

            placeholder.classList.add('hidden');
            auditOutput.classList.add('hidden');
            applyFixBtn.classList.add('hidden');
            loader.classList.remove('hidden');

            try {
                const response = await fetch('/api/audit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ script_text: scriptText })
                });

                const data = await response.json();
                loader.classList.add('hidden');
                auditOutput.classList.remove('hidden');

                riskBadge.classList.remove('hidden', 'bg-red-500/20', 'text-red-400', 'bg-emerald-500/20', 'text-emerald-400');
                if (data.has_risk) {
                    riskBadge.className = "px-2.5 py-0.5 text-xs font-semibold rounded-full bg-red-500/20 text-red-400 border border-red-500/30";
                    riskBadge.innerText = "HIGH RISK DETECTED";
                    if (data.suggested_fix) {
                        currentFix = data.suggested_fix;
                        applyFixBtn.classList.remove('hidden');
                    }
                } else {
                    riskBadge.className = "px-2.5 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30";
                    riskBadge.innerText = "ACCURATE / LOW RISK";
                }

                auditOutput.innerHTML = data.html_report || `<div class="p-4 bg-slate-800 rounded-lg text-slate-300 text-sm whitespace-pre-line">${data.analysis}</div>`;

            } catch (err) {
                loader.classList.add('hidden');
                placeholder.classList.remove('hidden');
                alert("Audit failed. Check backend logs and API keys.");
            }
        }

        function applyFix() {
            if (currentFix) {
                document.getElementById('scriptInput').value = currentFix;
                document.getElementById('applyFixBtn').classList.add('hidden');
            }
        }
    </script>
</body>
</html>
    """

@app.post("/api/audit")
async def audit_endpoint(request: AuditRequest):
    try:
        result = await run_screenplay_audit(request.script_text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
