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
