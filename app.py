import os

import streamlit as st
import streamlit.components.v1 as components

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

st.set_page_config(
    page_title="Live Transcribe",
    page_icon="LT",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
<style>
  [data-testid="stAppViewContainer"] { background: #ffffff; }
  [data-testid="stHeader"] { display: none; }
  [data-testid="collapsedControl"] { display: none; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
  iframe { display: block; }
</style>
""",
    unsafe_allow_html=True,
)


def get_backend_url() -> str:
    try:
        return st.secrets["BACKEND_WS_URL"]
    except (KeyError, FileNotFoundError):
        return os.getenv("BACKEND_WS_URL", "ws://localhost:8000/ws/transcribe")


backend_url = get_backend_url()

transcript_component = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<style>
  :root {{
    --blue: #1a73e8;
    --blue-2: #eaf3ff;
    --text: #0f172a;
    --muted: #334155;
    --soft: #f8fbff;
    --line: #dbeafe;
    --button: #edf6ff;
    --danger: #ef4f67;
    --dark: #15202b;
    --green: #50c9a3;
    --yellow: #f0c94a;
  }}

  * {{ box-sizing: border-box; }}

  html, body {{
    margin: 0;
    min-height: 100%;
    background: #ffffff;
    color: var(--text);
    font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }}

  button, select, input {{
    font: inherit;
  }}

  button {{
    border: 0;
    cursor: pointer;
    background: transparent;
  }}

  .app {{
    min-height: 720px;
    display: flex;
    flex-direction: column;
    position: relative;
  }}

  .topbar {{
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 18px 0 18px;
  }}

  .brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 21px;
    font-weight: 750;
    color: #111827;
  }}

  .mark {{
    width: 34px;
    height: 34px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #1a73e8 0%, #50c9a3 100%);
    color: #ffffff;
    font-size: 14px;
    font-weight: 800;
  }}

  .nav {{
    display: flex;
    align-items: center;
    gap: 22px;
    font-size: 18px;
  }}

  .nav-link {{
    color: #050505;
    white-space: nowrap;
  }}

  .hero {{
    text-align: center;
    padding-top: 14px;
    border-bottom: 1px solid var(--line);
  }}

  .hero h1 {{
    margin: 0;
    font-size: 34px;
    line-height: 1.1;
    letter-spacing: 0;
    font-weight: 800;
  }}

  .hero p {{
    margin: 8px 0 18px;
    color: #263244;
    font-size: 18px;
  }}

  .main {{
    flex: 1;
    display: grid;
    grid-template-rows: auto 1fr auto;
    min-height: 500px;
    padding: 28px 24px 18px;
  }}

  .settings-row {{
    width: min(686px, calc(100vw - 48px));
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr auto;
    row-gap: 12px;
    align-items: center;
    font-size: 18px;
    color: #050505;
  }}

  .select-wrap {{
    position: relative;
  }}

  select {{
    appearance: none;
    height: 40px;
    min-width: 114px;
    border: 1px solid var(--line);
    border-radius: 6px;
    background: #f9fbff;
    padding: 0 40px 0 14px;
    color: #111827;
    font-size: 17px;
  }}

  .select-wrap svg {{
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    pointer-events: none;
    color: #64748b;
  }}

  .switch {{
    justify-self: end;
    width: 52px;
    height: 28px;
    border-radius: 999px;
    background: var(--blue);
    padding: 3px;
    transition: background .16s ease;
  }}

  .switch .knob {{
    margin-left: auto;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--blue);
    transition: transform .16s ease;
  }}

  .switch.off {{
    background: #cbd5e1;
  }}

  .switch.off .knob {{
    transform: translateX(-24px);
  }}

  .stage {{
    width: min(860px, calc(100vw - 48px));
    margin: 18px auto 0;
    min-height: 190px;
    display: flex;
    align-items: flex-start;
    justify-content: center;
  }}

  #transcript {{
    width: 100%;
    min-height: 150px;
    max-height: 190px;
    overflow-y: auto;
    display: block;
    padding: 10px;
    border: 1px solid #e5edf8;
    border-radius: 8px;
    background: #f8fbff;
  }}

  .transcript-empty {{
    min-height: 128px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #64748b;
    font-size: 15px;
    text-align: center;
  }}

  .segment, .partial-row {{
    border: 1px solid #d9e6f5;
    border-left: 4px solid var(--blue);
    border-radius: 8px;
    background: #ffffff;
    padding: 12px 14px;
    margin-bottom: 10px;
    box-shadow: 0 8px 22px rgba(15, 23, 42, .04);
  }}

  .partial-row {{
    color: #64748b;
    font-style: italic;
    border-left-color: #94a3b8;
  }}

  .speaker {{
    display: block;
    color: var(--blue);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .06em;
    text-transform: uppercase;
    margin-bottom: 4px;
  }}

  .controls {{
    display: grid;
    justify-content: center;
    justify-items: center;
    gap: 10px;
    margin-bottom: 18px;
  }}

  .hint {{
    position: relative;
    min-height: 38px;
    border-radius: 24px;
    padding: 8px 16px;
    background: var(--blue-2);
    color: #2a86f2;
    font-size: 16px;
    font-weight: 650;
  }}

  .hint::after {{
    content: "";
    position: absolute;
    left: 50%;
    bottom: -10px;
    transform: translateX(-50%);
    width: 0;
    height: 0;
    border-left: 11px solid transparent;
    border-right: 11px solid transparent;
    border-top: 11px solid var(--blue-2);
  }}

  .control-row {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 26px;
  }}

  .time-badge, .gear-button {{
    width: 56px;
    height: 56px;
    border-radius: 50%;
    background: #eaf3ff;
    color: var(--blue);
    display: flex;
    align-items: center;
    justify-content: center;
  }}

  .time-badge {{
    flex-direction: column;
    font-weight: 800;
    font-size: 20px;
    line-height: 1;
  }}

  .time-badge span {{
    margin-top: 5px;
    font-size: 12px;
    font-weight: 500;
  }}

  .mic-button {{
    width: 88px;
    height: 88px;
    border-radius: 50%;
    background: var(--danger);
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 16px 35px rgba(239, 79, 103, .22);
    transition: transform .16s ease, box-shadow .16s ease, background .16s ease;
  }}

  .mic-button:hover {{
    transform: translateY(-1px);
    box-shadow: 0 20px 38px rgba(239, 79, 103, .3);
  }}

  .mic-button.recording {{
    background: #111827;
    animation: pulse 1.2s infinite;
  }}

  @keyframes pulse {{
    0%, 100% {{ box-shadow: 0 0 0 0 rgba(17, 24, 39, .28); }}
    50% {{ box-shadow: 0 0 0 16px rgba(17, 24, 39, 0); }}
  }}

  .modal-backdrop {{
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, .2);
    padding: 20px;
    z-index: 10;
  }}

  .modal-backdrop.open {{
    display: flex;
  }}

  .modal {{
    width: min(460px, 100%);
    border-radius: 8px;
    background: #ffffff;
    border: 1px solid var(--line);
    box-shadow: 0 24px 60px rgba(15, 23, 42, .2);
    padding: 22px;
  }}

  .modal-head {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 18px;
  }}

  .modal h2 {{
    margin: 0;
    font-size: 22px;
  }}

  .field {{
    display: grid;
    gap: 8px;
    margin-top: 14px;
  }}

  .field label {{
    font-weight: 650;
  }}

  .field input {{
    height: 42px;
    border-radius: 6px;
    border: 1px solid var(--line);
    padding: 0 12px;
  }}

  .actions {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 18px;
  }}

  .action {{
    height: 38px;
    border-radius: 6px;
    padding: 0 13px;
    border: 1px solid var(--line);
    color: #0f172a;
    background: #ffffff;
  }}

  .action.primary {{
    background: var(--blue);
    color: #ffffff;
    border-color: var(--blue);
  }}

  .small-note {{
    color: #475569;
    line-height: 1.5;
    margin: 0;
  }}

  @media (max-width: 760px) {{
    .topbar {{
      height: auto;
      padding: 16px;
      align-items: flex-start;
      gap: 16px;
    }}

    .brand {{
      font-size: 22px;
    }}

    .nav {{
      gap: 8px;
      flex-wrap: wrap;
      justify-content: flex-end;
      font-size: 15px;
    }}

    .hero h1 {{
      font-size: 34px;
    }}

    .hero p {{
      padding: 0 18px;
      font-size: 16px;
    }}

    .main {{
      padding: 28px 16px 24px;
    }}

    .settings-row {{
      width: 100%;
      font-size: 17px;
    }}

    .controls {{ margin-bottom: 18px; }}
  }}
</style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div class="brand" aria-label="Live Transcribe home">
      <span class="mark" aria-hidden="true">LT</span>
      <span>Live Transcribe</span>
    </div>
    <nav class="nav" aria-label="Primary">
      <button class="nav-link" type="button" onclick="openModal('settingsModal')">Settings</button>
    </nav>
  </header>

  <section class="hero" aria-label="Live Transcribe">
    <h1>Live Transcribe</h1>
    <p>Real-time audio transcription - free, fast, and no account required.</p>
  </section>

  <main class="main">
    <div class="settings-row">
      <label for="languageSelect">Language</label>
      <span class="select-wrap">
        <select id="languageSelect" onchange="syncLanguage()">
          <option value="en" selected>English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="it">Italian</option>
          <option value="pt">Portuguese</option>
          <option value="ur">Urdu</option>
          <option value="ar">Arabic</option>
        </select>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m6 9 6 6 6-6"/></svg>
      </span>
      <span>Enhanced transcription</span>
      <button id="proSwitch" class="switch" type="button" role="switch" aria-checked="true" onclick="togglePro()">
        <span class="knob">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m20 6-11 11-5-5"/></svg>
        </span>
      </button>
    </div>

    <section class="stage" aria-live="polite">
      <div id="transcript">
        <div id="emptyState" class="transcript-empty">Press the microphone and start speaking.</div>
      </div>
    </section>

    <section class="controls" aria-label="Recording controls">
      <div id="hint" class="hint">Press and start talking</div>
      <div class="control-row">
        <div class="time-badge" aria-label="Session duration">
          <strong id="minutes">0</strong>
          <span>mins</span>
        </div>
        <button id="recordBtn" class="mic-button" type="button" onclick="toggleRecording()" aria-label="Start recording">
          <svg id="micIcon" width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/><path d="M8 22h8"/></svg>
        </button>
        <button class="gear-button" type="button" onclick="openModal('settingsModal')" aria-label="Open settings">
          <svg width="33" height="33" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.32-1.915"/><circle cx="12" cy="12" r="3"/></svg>
        </button>
      </div>
    </section>
  </main>

</div>

<div id="settingsModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="settingsTitle">
  <div class="modal">
    <div class="modal-head">
      <h2 id="settingsTitle">Settings</h2>
      <button type="button" onclick="closeModals()" aria-label="Close">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
      </button>
    </div>
    <div class="field">
      <label for="backendUrl">Backend WebSocket URL</label>
      <input id="backendUrl" value="{backend_url}" />
    </div>
    <div class="field">
      <label for="maxSpeakers">Max speakers</label>
      <input id="maxSpeakers" type="number" min="1" max="10" value="4" />
    </div>
    <div class="actions">
      <button class="action primary" type="button" onclick="saveSettings()">Save</button>
      <button class="action" type="button" onclick="copyTranscript()">Copy transcript</button>
      <button class="action" type="button" onclick="downloadTranscript()">Download</button>
      <button class="action" type="button" onclick="clearTranscript()">Clear</button>
    </div>
  </div>
</div>

<script>
const DEFAULT_BACKEND = "{backend_url}";
const stopIcon = '<svg width="39" height="39" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="6" y="6" width="12" height="12" rx="2"/></svg>';
const micIcon = '<svg width="45" height="45" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><path d="M12 19v3"/><path d="M8 22h8"/></svg>';

let ws = null;
let audioCtx = null;
let processor = null;
let micStream = null;
let recording = false;
let proEnabled = true;
let transcriptText = [];
let timer = null;
let seconds = 0;

function openModal(id) {{
  closeModals();
  const modal = document.getElementById(id);
  if (modal) modal.classList.add("open");
}}

function closeModals() {{
  document.querySelectorAll(".modal-backdrop").forEach((modal) => modal.classList.remove("open"));
}}

document.addEventListener("keydown", (event) => {{
  if (event.key === "Escape") closeModals();
}});

document.querySelectorAll(".modal-backdrop").forEach((modal) => {{
  modal.addEventListener("click", (event) => {{
    if (event.target === modal) closeModals();
  }});
}});

function syncLanguage() {{
  if (recording) document.getElementById("hint").textContent = "Language changes apply on next recording";
}}

function togglePro() {{
  proEnabled = !proEnabled;
  const sw = document.getElementById("proSwitch");
  sw.classList.toggle("off", !proEnabled);
  sw.setAttribute("aria-checked", proEnabled);
}}

function saveSettings() {{
  const maxSpeakers = Number(document.getElementById("maxSpeakers").value);
  if (!Number.isFinite(maxSpeakers) || maxSpeakers < 1 || maxSpeakers > 10) {{
    document.getElementById("hint").textContent = "Max speakers must be 1-10";
    return;
  }}
  closeModals();
  document.getElementById("hint").textContent = "Settings saved";
}}

function buildWsUrl() {{
  const raw = document.getElementById("backendUrl").value.trim() || DEFAULT_BACKEND;
  const url = new URL(raw);
  url.searchParams.set("max_speakers", document.getElementById("maxSpeakers").value || "4");
  return url.toString();
}}

function toggleRecording() {{
  if (recording) stopRecording();
  else startRecording();
}}

async function startRecording() {{
  const button = document.getElementById("recordBtn");
  button.disabled = true;
  document.getElementById("hint").textContent = "Connecting...";

  try {{
    const wsUrl = buildWsUrl();
    ws = new WebSocket(wsUrl);
    ws.onopen = async () => {{
      recording = true;
      button.disabled = false;
      button.classList.add("recording");
      button.innerHTML = stopIcon;
      button.setAttribute("aria-label", "Stop recording");
      document.getElementById("hint").textContent = "Listening...";
      setEmptyState("Listening... speak into your microphone.");
      startTimer();

      micStream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
      audioCtx = new AudioContext({{ sampleRate: 16000 }});
      const source = audioCtx.createMediaStreamSource(micStream);
      processor = audioCtx.createScriptProcessor(4096, 1, 1);
      processor.onaudioprocess = (event) => {{
        if (ws && ws.readyState === WebSocket.OPEN) {{
          ws.send(event.inputBuffer.getChannelData(0).buffer.slice(0));
        }}
      }};
      source.connect(processor);
      processor.connect(audioCtx.destination);
    }};

    ws.onmessage = (event) => {{
      const msg = JSON.parse(event.data);
      if (msg.type === "partial") updatePartial(msg.speaker, msg.text);
      if (msg.type === "final") addFinal(msg.speaker, msg.text);
    }};

    ws.onerror = () => {{
      document.getElementById("hint").textContent = "Cannot reach backend";
      cleanup();
    }};

    ws.onclose = () => {{
      if (recording) cleanup();
    }};
  }} catch (error) {{
    document.getElementById("hint").textContent = error.message;
    button.disabled = false;
    cleanup();
  }}
}}

function stopRecording() {{
  cleanup();
  document.getElementById("hint").textContent = "Stopped";
}}

function cleanup() {{
  recording = false;
  stopTimer();
  if (processor) {{
    processor.disconnect();
    processor = null;
  }}
  if (audioCtx) {{
    audioCtx.close();
    audioCtx = null;
  }}
  if (micStream) {{
    micStream.getTracks().forEach((track) => track.stop());
    micStream = null;
  }}
  if (ws) {{
    const closing = ws;
    ws = null;
    if (closing.readyState === WebSocket.OPEN || closing.readyState === WebSocket.CONNECTING) closing.close();
  }}
  const button = document.getElementById("recordBtn");
  button.disabled = false;
  button.classList.remove("recording");
  button.innerHTML = micIcon;
  button.setAttribute("aria-label", "Start recording");
}}

function showTranscript() {{
  document.getElementById("transcript").style.display = "block";
}}

function setEmptyState(text) {{
  showTranscript();
  const emptyState = document.getElementById("emptyState");
  if (emptyState) emptyState.textContent = text;
}}

function hideEmptyState() {{
  const emptyState = document.getElementById("emptyState");
  if (emptyState) emptyState.remove();
}}

function speakerName(speaker) {{
  return String(speaker || "speaker").replace(/_/g, " ");
}}

function updatePartial(speaker, text) {{
  showTranscript();
  hideEmptyState();
  const id = "partial-" + speaker;
  let row = document.getElementById(id);
  if (!row) {{
    row = document.createElement("div");
    row.id = id;
    row.className = "partial-row";
    document.getElementById("transcript").appendChild(row);
  }}
  row.innerHTML = '<span class="speaker">' + speakerName(speaker) + '</span>' + escapeHtml(text);
  scrollTranscript();
}}

function addFinal(speaker, text) {{
  showTranscript();
  hideEmptyState();
  const partial = document.getElementById("partial-" + speaker);
  if (partial) partial.remove();
  const div = document.createElement("div");
  div.className = "segment";
  div.innerHTML = '<span class="speaker">' + speakerName(speaker) + '</span>' + escapeHtml(text);
  document.getElementById("transcript").appendChild(div);
  transcriptText.push(speakerName(speaker) + ": " + text);
  scrollTranscript();
}}

function scrollTranscript() {{
  const box = document.getElementById("transcript");
  box.scrollTop = box.scrollHeight;
}}

function escapeHtml(value) {{
  return String(value).replace(/[&<>"']/g, (char) => ({{
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  }}[char]));
}}

function clearTranscript() {{
  transcriptText = [];
  const box = document.getElementById("transcript");
  box.innerHTML = '<div id="emptyState" class="transcript-empty">Press the microphone and start speaking.</div>';
  document.getElementById("hint").textContent = "Transcript cleared";
}}

async function copyTranscript() {{
  const text = transcriptText.join("\\n");
  if (!text) {{
    document.getElementById("hint").textContent = "Nothing to copy yet";
    return;
  }}
  await navigator.clipboard.writeText(text);
  document.getElementById("hint").textContent = "Transcript copied";
}}

function downloadTranscript() {{
  const text = transcriptText.join("\\n");
  if (!text) {{
    document.getElementById("hint").textContent = "Nothing to download yet";
    return;
  }}
  const blob = new Blob([text], {{ type: "text/plain" }});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "live-transcript.txt";
  link.click();
  URL.revokeObjectURL(url);
}}

function startTimer() {{
  seconds = 0;
  renderTime();
  timer = setInterval(() => {{
    seconds += 1;
    renderTime();
  }}, 1000);
}}

function stopTimer() {{
  if (timer) clearInterval(timer);
  timer = null;
}}

function renderTime() {{
  document.getElementById("minutes").textContent = Math.floor(seconds / 60);
}}
</script>
</body>
</html>
"""

components.html(transcript_component, height=720, scrolling=False)
