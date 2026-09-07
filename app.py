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
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ScriptDoctor AI — Agentic Cinema Studio</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');
        body { font-family: 'Inter', sans-serif; }
        .font-mono { font-family: 'Fira Code', monospace; }
        .glass-panel { background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.08); }
        .glow-button { box-shadow: 0 0 25px rgba(99, 102, 241, 0.4); }
        .pulse-loader { animation: spin 0.75s linear infinite; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col selection:bg-indigo-500 selection:text-white">

    <!-- Header / Navbar -->
    <header class="border-b border-slate-800/80 bg-slate-900/70 sticky top-0 z-50 backdrop-blur-2xl px-8 py-3.5 flex justify-between items-center">
        <div class="flex items-center gap-3">
            <div class="h-10 w-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-xl text-white shadow-lg shadow-indigo-500/20">
                🎬
            </div>
            <div>
                <div class="flex items-center gap-2">
                    <h1 class="text-lg font-extrabold bg-gradient-to-r from-indigo-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">ScriptDoctor AI</h1>
                    <span class="px-2 py-0.5 text-[10px] font-bold tracking-wider rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">HACKATHON EDITION</span>
                </div>
                <p class="text-xs text-slate-400">Agentic Cinema Verification Fleet · Gemini 3.5 & Parallel MCP Grounding</p>
            </div>
        </div>
        <div class="flex items-center gap-3">
            <div class="hidden sm:flex items-center gap-2 text-xs text-slate-400 bg-slate-900/90 px-3 py-1.5 rounded-lg border border-slate-800">
                <span class="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                <span class="font-mono text-[11px]">Parallel MCP Search: Online</span>
            </div>
        </div>
    </header>

    <!-- Main Workspace -->
    <main class="flex-1 p-6 max-w-[1600px] mx-auto w-full grid grid-cols-1 lg:grid-cols-12 gap-6">

        <!-- Left Column: Screenplay Editor -->
        <div class="lg:col-span-6 flex flex-col gap-4">
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-film text-indigo-400 text-sm"></i>
                    <h2 class="text-xs font-bold tracking-wider text-slate-400 uppercase">Screenplay Scene Input</h2>
                </div>
                <div class="flex gap-2">
                    <button onclick="loadSample(1)" class="text-xs bg-slate-900 hover:bg-indigo-950/80 text-indigo-300 border border-slate-800 hover:border-indigo-500/40 px-3 py-1 rounded-lg transition font-medium">1998 Anachronism</button>
                    <button onclick="loadSample(2)" class="text-xs bg-slate-900 hover:bg-purple-950/80 text-purple-300 border border-slate-800 hover:border-purple-500/40 px-3 py-1 rounded-lg transition font-medium">1888 Victorian</button>
                </div>
            </div>

            <div class="relative flex-1 min-h-[520px] rounded-2xl glass-panel p-1 border border-slate-800/80 flex flex-col shadow-2xl">
                <div class="bg-slate-900/90 px-4 py-2.5 border-b border-slate-800/80 rounded-t-xl flex justify-between items-center text-xs text-slate-400 font-mono">
                    <span class="flex items-center gap-2"><i class="fa-solid fa-file-code text-indigo-400"></i> scene_script.fountain</span>
                    <span id="charCount">0 characters</span>
                </div>
                <textarea id="scriptInput" oninput="updateCharCount()" class="w-full flex-1 p-5 bg-transparent font-mono text-sm text-slate-200 focus:outline-none transition resize-none leading-relaxed tracking-wide placeholder:text-slate-600" placeholder="Paste screenplay excerpt here..."></textarea>
            </div>

            <button onclick="runAudit()" id="auditBtn" class="w-full py-3.5 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 font-bold rounded-xl text-white shadow-xl glow-button transition flex items-center justify-center gap-2 text-sm tracking-wide">
                <i class="fa-solid fa-wand-magic-sparkles"></i>
                <span>Execute Multi-Agent Screenplay Audit</span>
            </button>
        </div>

        <!-- Right Column: Audit Telemetry Dashboard -->
        <div class="lg:col-span-6 flex flex-col gap-4">
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-2">
                    <i class="fa-solid fa-chart-line text-purple-400 text-sm"></i>
                    <h2 class="text-xs font-bold tracking-wider text-slate-400 uppercase">Agent Audit Telemetry</h2>
                </div>
                <span id="riskBadge" class="hidden px-3 py-1 text-xs font-bold tracking-wider rounded-full uppercase"></span>
            </div>

            <div id="resultsContainer" class="w-full h-[520px] glass-panel border border-slate-800/80 rounded-2xl p-6 overflow-y-auto flex flex-col justify-center items-center relative shadow-2xl">
                
                <!-- Initial State -->
                <div id="placeholderText" class="text-center space-y-3 max-w-sm">
                    <div class="h-14 w-14 rounded-2xl bg-slate-900 border border-slate-800 flex items-center justify-center mx-auto text-slate-500 text-2xl shadow-inner">
                        <i class="fa-solid fa-microchip"></i>
                    </div>
                    <p class="text-slate-300 font-semibold text-sm">Agent Fleet Standby</p>
                    <p class="text-slate-500 text-xs leading-relaxed">Select a sample script or paste your scene text on the left, then click <strong>Execute Multi-Agent Screenplay Audit</strong> to start.</p>
                </div>

                <!-- Loading State -->
                <div id="loader" class="hidden flex flex-col items-center gap-4">
                    <div class="relative flex items-center justify-center">
                        <i class="fa-solid fa-circle-notch text-4xl text-indigo-500 pulse-loader"></i>
                        <i class="fa-solid fa-robot text-xs text-indigo-300 absolute"></i>
                    </div>
                    <p class="text-sm font-medium text-slate-300 animate-pulse">Running Gemini 3.5 & Parallel MCP Agent Fleet...</p>
                </div>

                <!-- Report Output Container -->
                <div id="auditOutput" class="hidden w-full text-left space-y-4"></div>
            </div>

            <!-- Auto-Fix Button -->
            <button id="applyFixBtn" onclick="applyFix()" class="hidden w-full py-3.5 bg-emerald-950/90 hover:bg-emerald-900 text-emerald-300 border border-emerald-500/40 rounded-xl text-sm font-bold transition flex items-center justify-center gap-2 shadow-xl">
                <i class="fa-solid fa-wand-magic"></i>
                <span>Auto-Remediate Script Anachronisms</span>
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
            updateCharCount();
        }

        function updateCharCount() {
            const val = document.getElementById('scriptInput').value;
            document.getElementById('charCount').innerText = `${val.length} characters`;
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

                riskBadge.className = "px-3 py-1 text-xs font-bold tracking-wider rounded-full border uppercase ";
                if (data.has_risk) {
                    riskBadge.classList.add('bg-red-500/10', 'text-red-400', 'border-red-500/30');
                    riskBadge.innerText = "CRITICAL RISK";
                    if (data.suggested_fix) {
                        currentFix = data.suggested_fix;
                        applyFixBtn.classList.remove('hidden');
                    }
                } else {
                    riskBadge.classList.add('bg-emerald-500/10', 'text-emerald-400', 'border-emerald-500/30');
                    riskBadge.innerText = "FULLY GROUNDED";
                }

                auditOutput.innerHTML = data.html_report;

            } catch (err) {
                loader.classList.add('hidden');
                placeholder.classList.remove('hidden');
                alert("Audit service encountered an error. Check backend logs.");
            }
        }

        function applyFix() {
            if (currentFix) {
                document.getElementById('scriptInput').value = currentFix;
                updateCharCount();
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
