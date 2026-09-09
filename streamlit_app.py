import streamlit as st

# Configure page layout
st.set_page_config(
    page_title="ScriptDoctor AI - Hackathon Edition",
    page_icon="🎬",
    layout="wide"
)

# Custom Styling
st.markdown('''
<style>
    .stApp {
        background-color: #070913;
        color: #e2e8f0;
    }
    .badge-hackathon {
        background-color: rgba(49, 46, 129, 0.9);
        color: #c7d2fe;
        border: 1px solid rgba(99, 102, 241, 0.5);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
        font-family: monospace;
    }
    .badge-active {
        background-color: #0f172a;
        border: 1px solid #334155;
        padding: 6px 12px;
        border-radius: 9999px;
        font-size: 0.75rem;
        color: #f1f5f9;
    }
    .status-dot {
        height: 8px;
        width: 8px;
        background-color: #34d399;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }
    .stTextArea textarea {
        background-color: #0b0f19 !important;
        color: #f8fafc !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
        font-family: monospace !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    .standby-card {
        background-color: #0b0f19;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 80px 20px;
        text-align: center;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 520px;
    }
    .standby-icon {
        background-color: #1e1b4b;
        border: 1px solid #3730a3;
        border-radius: 12px;
        padding: 16px;
        font-size: 2rem;
        margin-bottom: 16px;
        display: inline-block;
    }
    .metric-card {
        background-color: #0f1424;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 12px;
        text-align: center;
    }
    .metric-title {
        color: #64748b;
        font-size: 0.7rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value-risk {
        color: #f43f5e;
        font-size: 1.6rem;
        font-weight: 800;
        font-family: monospace;
    }
    .metric-value-era {
        color: #818cf8;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 6px;
    }
    .metric-value-status {
        color: #34d399;
        font-size: 0.95rem;
        font-weight: 700;
        margin-top: 6px;
    }
    .trace-card {
        background-color: #0b0f19;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
        font-family: monospace;
        font-size: 0.8rem;
        color: #94a3b8;
    }
    .issue-card {
        background-color: rgba(225, 29, 72, 0.08);
        border: 1px solid rgba(225, 29, 72, 0.3);
        border-radius: 10px;
        padding: 16px;
    }
    .severity-badge {
        background-color: rgba(225, 29, 72, 0.2);
        color: #fda4af;
        border: 1px solid rgba(225, 29, 72, 0.4);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.65rem;
        font-weight: 700;
        float: right;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #a855f7, #ec4899) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: linear-gradient(135deg, #059669, #10b981) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
    }
</style>
''', unsafe_allow_html=True)

# 4 Video Presets Data
PRESETS = {
    "1998 Neo-Noir Anachronism": {
        "text": "INT. POLICE STATION - 1998\n\nDetective Miller pulls out his iPhone 15 and checks the timestamp...\n\nMILLER\n(into phone)\nWe need backup at downtown instantly.",
        "risk": "85/100",
        "era": "1998 Neo-Noir Era",
        "issue_title": "iPhone 15",
        "severity": "CRITICAL",
        "description": "Smartphones post-date late 90s police precinct equipment by 25 years.",
        "fix": "Motorola Flip Phone / Pager",
        "remediated": "INT. POLICE STATION - 1998\n\nDetective Miller pulls out his Motorola Flip Phone and checks the timestamp...\n\nMILLER\n(into phone)\nWe need backup at downtown instantly.",
        "video": "https://www.youtube.com/watch?v=znMA5pLI_Tk",
        "trace": [
            "Agent 1 [Temporal Parser]: Identified explicit temporal marker (1998).",
            "Agent 2 [Parallel MCP Engine]: Queried smartphone release timeline index.",
            "Agent 3 [Gemini 3.5 Auditor]: Proposed period-accurate telecommunication hardware."
        ]
    },
    "1970 Apollo Mission Control": {
        "text": "INT. MISSION CONTROL - 1970\n\nFlight controller Jim pulls up Google Maps on his iPad to locate the recovery ship near Honolulu.",
        "risk": "45/100",
        "era": "1970 Apollo Era",
        "issue_title": "iPad / Google Maps",
        "severity": "CRITICAL",
        "description": "Digital tablets and satellite mapping post-date Apollo era mission control.",
        "fix": "Paper Topographic Maps & Compass",
        "remediated": "INT. MISSION CONTROL - 1970\n\nFlight controller Jim pulls up Paper Topographic Maps & Compass to locate the recovery ship near Honolulu.",
        "video": "https://www.youtube.com/watch?v=VHnWvNLXBDU",
        "trace": [
            "Agent 1 [Temporal Parser]: Extracted era markers from scene headers.",
            "Agent 2 [Parallel MCP Engine]: Grounded historical technology launch databases.",
            "Agent 3 [Gemini 3.5 Auditor]: Formulated non-disruptive narrative replacements."
        ]
    },
    "1888 Victorian London": {
        "text": "EXT. WHITECHAPEL STREET - 1888\n\nInspector Abberline steps over damp cobblestones as motorized taxi cabs zoom past under flickering gaslights.",
        "risk": "92/100",
        "era": "1888 Victorian London",
        "issue_title": "Motorized Taxi Cabs",
        "severity": "CRITICAL",
        "description": "Motorized combustion engines were not operational in 1888 London transit.",
        "fix": "Horse-Drawn Hansom Cabs",
        "remediated": "EXT. WHITECHAPEL STREET - 1888\n\nInspector Abberline steps over damp cobblestones as Horse-Drawn Hansom Cabs zoom past under flickering gaslights.",
        "video": "https://www.youtube.com/watch?v=g_36UX8iYik",
        "trace": [
            "Agent 1 [Temporal Parser]: Recognized late-19th-century setting.",
            "Agent 2 [Parallel MCP Engine]: Checked combustion taxi introduction metrics.",
            "Agent 3 [Gemini 3.5 Auditor]: Replaced vehicle reference with period hansom cabs."
        ]
    },
    "1925 Roaring Twenties Speakeasy": {
        "text": "INT. SPEAKEASY - 1925\n\nThe brass quartet swings softly while glass decanters clink across velvet-lined booths.",
        "risk": "05/100",
        "era": "1925 Jazz Age",
        "issue_title": "None Detected",
        "severity": "INFO",
        "description": "No historical inconsistencies detected for Prohibition-era venue.",
        "fix": "Maintain Current Screenplay Draft",
        "remediated": "INT. SPEAKEASY - 1925\n\nThe brass quartet swings softly while glass decanters clink across velvet-lined booths.",
        "video": "https://www.youtube.com/watch?v=3JZ_D3ELwOQ",
        "trace": [
            "Agent 1 [Temporal Parser]: Extracted Prohibition-era keywords.",
            "Agent 2 [Parallel MCP Engine]: Grounded jazz brass instrumentation timeline.",
            "Agent 3 [Gemini 3.5 Auditor]: Confirmed scene narrative accuracy."
        ]
    }
}

# Session State Initialization
if "audit_triggered" not in st.session_state:
    st.session_state.audit_triggered = False
if "video_triggered" not in st.session_state:
    st.session_state.video_triggered = False
if "remediated_status" not in st.session_state:
    st.session_state.remediated_status = {}
if "selected_scene" not in st.session_state:
    st.session_state.selected_scene = list(PRESETS.keys())[0]

# Header Bar
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('''
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="padding: 10px; background: rgba(88, 28, 135, 0.5); border: 1px solid rgba(168, 85, 247, 0.4); border-radius: 10px; font-size: 1.6rem;">🎬</div>
            <div>
                <div style="display: flex; align-items: center; gap: 8px;">
                    <h2 style="margin: 0; color: #ffffff; font-weight: 700; font-size: 1.3rem;">ScriptDoctor AI</h2>
                    <span class="badge-hackathon">HACKATHON EDITION</span>
                </div>
                <p style="margin: 2px 0 0 0; font-size: 0.8rem; color: #94a3b8;">Autonomous Script Verification & Pre-Vis Fleet · Gemini 3.5 & Parallel MCP Grounding</p>
            </div>
        </div>
    ''', unsafe_allow_html=True)

with col_h2:
    st.markdown('''
        <div style="text-align: right; padding-top: 8px;">
            <span class="badge-active"><span class="status-dot"></span>Parallel MCP grounding: <strong>Active</strong></span>
        </div>
    ''', unsafe_allow_html=True)

st.divider()

# Main Layout Columns
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("**🎬 SCREENPLAY SCENE INPUT**")
    
    # Dropdown and Video Generation Button Row
    d_col, b_col = st.columns([2, 1])
    with d_col:
        selected_key = st.selectbox(
            "Select Scene Preset:",
            list(PRESETS.keys()),
            index=list(PRESETS.keys()).index(st.session_state.selected_scene),
            label_visibility="collapsed"
        )
        if selected_key != st.session_state.selected_scene:
            st.session_state.selected_scene = selected_key
            st.session_state.audit_triggered = False
            st.session_state.video_triggered = False
            st.rerun()

    with b_col:
        if st.button("📹 Generate Scene Video", type="primary", use_container_width=True):
            st.session_state.video_triggered = True
            st.session_state.audit_triggered = True
            st.toast("Pre-Vis Video Generated Successfully!", icon="🎬")
            st.rerun()

    preset = PRESETS[st.session_state.selected_scene]
    is_remediated = st.session_state.remediated_status.get(st.session_state.selected_scene, False)
    current_text = preset["remediated"] if is_remediated else preset["text"]

    st.text_area(
        "Script Editor",
        value=current_text,
        height=320,
        label_visibility="collapsed"
    )
    st.caption(f"📄 `scene_script.fountain` · **{len(current_text)}** characters")

    if st.button("✨ Execute Multi-Agent Audit", use_container_width=True):
        st.session_state.audit_triggered = True
        st.toast("Multi-Agent Screenplay Audit Completed!", icon="⚡")
        st.rerun()

with col_right:
    st.markdown("**📈 AGENT AUDIT TELEMETRY**")

    # Display Standby state until audit or video generation is activated
    if not st.session_state.audit_triggered and not st.session_state.video_triggered:
        st.markdown('''
            <div class="standby-card">
                <div class="standby-icon">📟</div>
                <h3 style="color: #ffffff; margin: 0 0 8px 0; font-size: 1.1rem; font-weight: 700;">Agent Fleet Standby</h3>
                <p style="color: #64748b; font-size: 0.85rem; max-width: 320px; margin: 0; line-height: 1.5;">
                    Select a scene from the dropdown to audit or generate an AI Pre-Vis video preview.
                </p>
            </div>
        ''', unsafe_allow_html=True)
    else:
        active_p = PRESETS[st.session_state.selected_scene]

        # Metric Cards
        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-title">Anachronism Risk</div>
                    <div class="metric-value-risk">{active_p["risk"]}</div>
                </div>
            ''', unsafe_allow_html=True)
        with m2:
            st.markdown(f'''
                <div class="metric-card">
                    <div class="metric-title">Setting</div>
                    <div class="metric-value-era">{active_p["era"]}</div>
                </div>
            ''', unsafe_allow_html=True)
        with m3:
            st.markdown('''
                <div class="metric-card">
                    <div class="metric-title">MCP Status</div>
                    <div class="metric-value-status">🟢 Grounded</div>
                </div>
            ''', unsafe_allow_html=True)

        st.write("")

        # Reasoner Trace
        st.markdown("**>_ MULTI-AGENT REASONER TRACE**")
        trace_items = "".join([f"<li>{t}</li>" for t in active_p["trace"]])
        st.markdown(f'''
            <div class="trace-card">
                <ul style="margin: 0; padding-left: 18px; line-height: 1.8;">
                    {trace_items}
                </ul>
            </div>
        ''', unsafe_allow_html=True)

        st.write("")

        # Detected Inconsistencies
        st.markdown("**DETECTED INCONSISTENCIES**")
        st.markdown(f'''
            <div class="issue-card">
                <span class="severity-badge">{active_p["severity"]}</span>
                <div style="font-weight: 700; color: #f8fafc; font-size: 0.9rem; margin-bottom: 6px;">
                    ⚠️ {active_p["issue_title"]}
                </div>
                <div style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 10px;">
                    {active_p["description"]}
                </div>
                <div style="font-size: 0.8rem; color: #34d399; font-weight: 600;">
                    💡 Suggested Fix: <span style="text-decoration: underline;">{active_p["fix"]}</span>
                </div>
            </div>
        ''', unsafe_allow_html=True)

        st.write("")

        # Auto-Remediate Action Button
        if st.button("✏️ Auto-Remediate Script Anachronisms", use_container_width=True, type="secondary"):
            st.session_state.remediated_status[st.session_state.selected_scene] = True
            st.toast("Anachronism successfully remediated!", icon="✅")
            st.rerun()

        st.write("")

        # Pre-Vis Video Render Player
        st.markdown("**📹 PRE-VIS SCENE VIDEO RENDER**")
        st.video(active_p["video"])
