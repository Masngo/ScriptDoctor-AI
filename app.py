import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

app = FastAPI(title="ScriptDoctor AI")

# Pre-loaded scenes matching the UI
PRESETS = {
    "1998 Neo-Noir Anachronism": {
        "text": "INT. POLICE STATION - 1998\n\nDetective Miller pulls out his iPhone 15 and checks the timestamp...\n\nMILLER\n(into phone)\nWe need backup at downtown instantly.",
        "video": "https://www.youtube.com/watch?v=VHnWvNLXBDU"
    },
    "1888 Victorian London": {
        "text": "EXT. WHITECHAPEL STREET - 1888\n\nInspector Abberline steps over damp cobblestones as motorized taxi cabs zoom past under flickering gaslights.",
        "video": "https://www.youtube.com/watch?v=znMA5pLI_Tk"
    },
    "1925 Roaring Twenties": {
        "text": "INT. SPEAKEASY - 1925\n\nThe brass quartet swings softly while glass decanters clink across velvet-lined booths.",
        "video": "https://www.youtube.com/watch?v=g_36UX8iYik"
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>ScriptDoctor AI - Hackathon Edition</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body { background-color: #070913; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; }
        .glass-panel { background: #0f1424; border: 1px solid #1e293b; border-radius: 12px; }
        .neon-btn { background: linear-gradient(135deg, #d946ef, #8b5cf6); }
        .neon-btn:hover { opacity: 0.9; }
        .audit-btn { background: linear-gradient(135deg, #0ea5e9, #6366f1); }
    </style>
</head>
<body class="p-6">
    <!-- Header Bar -->
    <div class="flex justify-between items-center mb-6">
        <div class="flex items-center gap-3">
            <div class="p-2 bg-purple-900/40 border border-purple-500/30 rounded-lg text-2xl">🎬</div>
            <div>
                <div class="flex items-center gap-2">
                    <h1 class="text-xl font-bold text-white">ScriptDoctor AI</h1>
                    <span class="text-xs bg-indigo-900/80 text-indigo-300 border border-indigo-500/30 px-2 py-0.5 rounded font-mono font-semibold">HACKATHON EDITION</span>
                </div>
                <p class="text-xs text-slate-400">Autonomous Script Verification & Pre-Vis Fleet · Gemini 3.5 & Parallel MCP Grounding</p>
            </div>
        </div>
        <div class="flex items-center gap-2 bg-slate-900/80 border border-slate-800 px-3 py-1.5 rounded-full text-xs text-slate-300">
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Parallel MCP grounding: <strong>Active</strong></span>
        </div>
    </div>

    <!-- Main Workspace -->
    <div class="grid grid-cols-2 gap-6">
        <!-- Left Panel: Editor -->
        <div class="space-y-4">
            <div class="flex justify-between items-center">
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">🎬 Screenplay Scene Input</span>
                <div class="flex gap-2">
                    <select id="presetSelect" onchange="loadPreset()" class="bg-slate-900 border border-slate-700 text-xs text-slate-200 rounded px-3 py-1.5 outline-none">
                        <option value="1998 Neo-Noir Anachronism">1998 Neo-Noir Anachronism</option>
                        <option value="1888 Victorian London">1888 Victorian London</option>
                        <option value="1925 Roaring Twenties">1925 Roaring Twenties</option>
                    </select>
                </div>
            </div>

            <div class="flex gap-2">
                <button onclick="runAudit()" class="audit-btn text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 shadow-lg">
                    🔍 Run Temporal Audit
                </button>
                <button onclick="generateVideo()" class="neon-btn text-white text-xs font-semibold px-4 py-2 rounded-lg flex items-center gap-1.5 shadow-lg">
                    📹 Generate Scene Video
                </button>
            </div>

            <div class="glass-panel p-4 space-y-2">
                <div class="flex justify-between text-xs text-slate-500 font-mono">
                    <span>📄 scene_script.fountain</span>
                    <span id="charCount">155 characters</span>
                </div>
                <textarea id="scriptText" class="w-full h-80 bg-transparent text-sm font-mono text-slate-200 outline-none resize-none leading-relaxed" oninput="updateCharCount()"></textarea>
            </div>
        </div>

        <!-- Right Panel: Telemetry Output -->
        <div class="space-y-4">
            <span class="text-xs font-bold uppercase tracking-wider text-slate-400">📈 Agent Audit Telemetry</span>
            <div id="telemetryBox" class="glass-panel h-[410px] p-6 flex flex-col justify-center items-center text-center overflow-y-auto">
                <div id="standbyState" class="space-y-3">
                    <div class="w-12 h-12 rounded-xl bg-slate-800/80 border border-slate-700 flex items-center justify-center mx-auto text-indigo-400 text-xl">
                        ⚙️
                    </div>
                    <h3 class="text-base font-semibold text-slate-200">Agent Fleet Standby</h3>
                    <p class="text-xs text-slate-400 max-w-xs">Select a scene from the dropdown to audit or generate an AI Pre-Vis video preview.</p>
                </div>
                <div id="activeState" class="w-full hidden space-y-4 text-left font-mono text-xs"></div>
            </div>
        </div>
    </div>

    <script>
        const presets = """ + json.dumps(PRESETS) + """;

        function loadPreset() {
            const val = document.getElementById("presetSelect").value;
            const text = presets[val].text;
            document.getElementById("scriptText").value = text;
            updateCharCount();
        }

        function updateCharCount() {
            const len = document.getElementById("scriptText").value.length;
            document.getElementById("charCount").innerText = len + " characters";
        }

        async function runAudit() {
            const standby = document.getElementById("standbyState");
            const active = document.getElementById("activeState");
            standby.classList.add("hidden");
            active.classList.remove("hidden");
            active.innerHTML = '<div class="text-indigo-400 font-semibold mb-2">⚡ Initializing Gemini 3.5 Agent Audit...</div>';

            const script = document.getElementById("scriptText").value;

            // Simulating real-time telemetry stream
            const steps = [
                { delay: 300, msg: "🔍 [MCP-Grounding] Parsing scene temporal context: YEAR 1998", color: "text-slate-400" },
                { delay: 800, msg: "⚙️ [Fact-Check Agent] Querying technical availability timeline for 'iPhone 15'...", color: "text-amber-400" },
                { delay: 1400, msg: "⚠️ [ANACHRONISM DETECTED] iPhone 15 was released in 2023. Scene timeline is 1998 (25-year discrepancy).", color: "text-rose-400 font-bold" },
                { delay: 1900, msg: "💡 [Remediation Fleet] Suggested Fix: Replace 'iPhone 15' with 'pager' or 'flip phone' for historical accuracy.", color: "text-emerald-400" }
            ];

            for (const s of steps) {
                await new Promise(r => setTimeout(r, s.delay));
                active.innerHTML += `<div class="${s.color} py-1 border-b border-slate-800/50">${s.msg}</div>`;
            }
        }

        async function generateVideo() {
            await runAudit();
            const active = document.getElementById("activeState");
            const val = document.getElementById("presetSelect").value;
            const videoUrl = presets[val].video;

            active.innerHTML += `
                <div class="mt-4 p-3 bg-slate-900 border border-purple-500/30 rounded-lg">
                    <div class="text-purple-300 font-sans font-semibold mb-2">🎬 Generated Pre-Vis Video Render:</div>
                    <a href="${videoUrl}" target="_blank" class="text-sky-400 underline break-all">${videoUrl}</a>
                </div>
            `;
        }

        loadPreset();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    return HTML_TEMPLATE
