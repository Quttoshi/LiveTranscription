import os
import streamlit as st
import streamlit.components.v1 as components

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

st.set_page_config(
    page_title="Live Transcription",
    page_icon="🎤",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Force clean white theme
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #f3f4f6; }
  [data-testid="stHeader"] { display: none; }
  [data-testid="collapsedControl"] { display: none; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

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
<style>
  :root {{
    --bg:      #f3f4f6;
    --white:   #ffffff;
    --text:    #111827;
    --muted:   #9ca3af;
    --border:  #e5e7eb;
    --accent:  #ef4444;
    --s1:      #16a34a;
    --s2:      #2563eb;
    --s3:      #ca8a04;
    --s4:      #db2777;
    --s5:      #7c3aed;
    --s6:      #ea580c;
  }}

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    background: var(--bg);
    color: var(--text);
    font-family: 'Inter', system-ui, sans-serif;
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 40px 16px;
  }}

  .card {{
    background: var(--white);
    border-radius: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,.08);
    padding: 40px 36px;
    width: 100%;
    max-width: 680px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 28px;
  }}

  /* ── Header ── */
  .header {{ text-align: center; }}
  .header h1 {{ font-size: 26px; font-weight: 700; letter-spacing: -.4px; }}
  .header p  {{ font-size: 14px; color: var(--muted); margin-top: 6px; }}

  /* ── Record button ── */
  .record-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }}

  #recordBtn {{
    width: 68px; height: 68px;
    border-radius: 50%;
    border: none;
    background: var(--accent);
    color: #fff;
    font-size: 26px;
    cursor: pointer;
    box-shadow: 0 4px 16px rgba(239,68,68,.35);
    transition: transform .15s, box-shadow .15s;
    display: flex; align-items: center; justify-content: center;
  }}
  #recordBtn:hover {{ transform: scale(1.08); box-shadow: 0 6px 22px rgba(239,68,68,.45); }}
  #recordBtn.recording {{
    background: #1f2937;
    box-shadow: 0 4px 16px rgba(0,0,0,.2);
    animation: pulse 1.4s infinite;
  }}
  @keyframes pulse {{
    0%,100% {{ box-shadow: 0 0 0 0 rgba(31,41,55,.35); }}
    50%      {{ box-shadow: 0 0 0 10px rgba(31,41,55,0); }}
  }}

  #status {{
    font-size: 13px; color: var(--muted);
    display: flex; align-items: center; gap: 6px;
  }}
  .dot {{
    width: 7px; height: 7px; border-radius: 50%; background: var(--muted);
  }}
  .dot.live {{ background: var(--accent); animation: blink 1.1s infinite; }}
  @keyframes blink {{ 0%,100%{{opacity:1}} 50%{{opacity:.2}} }}

  /* ── Slider ── */
  .slider-wrap {{
    width: 100%;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }}
  .slider-label {{
    font-size: 13px;
    font-weight: 500;
    color: var(--text);
    display: flex;
    justify-content: space-between;
  }}
  input[type=range] {{
    -webkit-appearance: none;
    width: 100%;
    height: 4px;
    border-radius: 2px;
    background: var(--border);
    outline: none;
    cursor: pointer;
  }}
  input[type=range]::-webkit-slider-thumb {{
    -webkit-appearance: none;
    width: 18px; height: 18px;
    border-radius: 50%;
    background: var(--accent);
    cursor: pointer;
    box-shadow: 0 1px 4px rgba(0,0,0,.15);
  }}

  /* ── Transcript ── */
  #transcript {{
    width: 100%;
    background: #f9fafb;
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 22px;
    min-height: 260px;
    max-height: 420px;
    overflow-y: auto;
    font-size: 15px;
    line-height: 1.8;
  }}

  #placeholder {{
    color: var(--muted);
    text-align: center;
    padding: 70px 0;
    font-size: 14px;
    user-select: none;
  }}

  .utterance {{
    display: flex; flex-direction: column; gap: 2px;
    margin-bottom: 14px; padding: 10px 14px;
    border-radius: 10px;
    background: var(--white);
    border: 1px solid var(--border);
    border-left: 3px solid transparent;
  }}
  .utterance.s1 {{ border-left-color: var(--s1); }}
  .utterance.s2 {{ border-left-color: var(--s2); }}
  .utterance.s3 {{ border-left-color: var(--s3); }}
  .utterance.s4 {{ border-left-color: var(--s4); }}
  .utterance.s5 {{ border-left-color: var(--s5); }}
  .utterance.s6 {{ border-left-color: var(--s6); }}

  .speaker-tag {{
    font-size: 10px; font-weight: 700;
    letter-spacing: .08em; text-transform: uppercase; margin-bottom: 2px;
  }}
  .s1 .speaker-tag {{ color: var(--s1); }}
  .s2 .speaker-tag {{ color: var(--s2); }}
  .s3 .speaker-tag {{ color: var(--s3); }}
  .s4 .speaker-tag {{ color: var(--s4); }}
  .s5 .speaker-tag {{ color: var(--s5); }}
  .s6 .speaker-tag {{ color: var(--s6); }}

  .partial-row {{
    padding: 6px 14px; margin-bottom: 8px;
    border-left: 2px solid var(--border);
    color: var(--muted); font-style: italic; font-size: 14px;
  }}
</style>
</head>
<body>
<div class="card">

  <div class="header">
    <h1>Live Transcription</h1>
    <p>Real-time speech-to-text with speaker diarization</p>
  </div>

  <div class="record-wrap">
    <button id="recordBtn" onclick="toggleRecording()">🎤</button>
    <div id="status">
      <div class="dot" id="dot"></div>
      <span id="statusText">Press to start</span>
    </div>
  </div>

  <div class="slider-wrap">
    <div class="slider-label">
      <span>Max Speakers</span>
      <span id="speakerVal">2</span>
    </div>
    <input type="range" id="speakerSlider" min="1" max="6" value="2"
      oninput="document.getElementById('speakerVal').textContent = this.value">
  </div>

  <div id="transcript">
    <div id="placeholder">Press the button above to begin live transcription</div>
    <div id="content" style="display:none"></div>
  </div>

</div>

<script>
const BASE_URL    = "{backend_url}";
const SPEAKER_CLS = ['s1','s2','s3','s4','s5','s6'];

let ws=null, audioCtx=null, processor=null, micStream=null;
let speakerIndex={{}}, colorCounter=0, recording=false;

function speakerClass(label) {{
  if (!(label in speakerIndex)) speakerIndex[label] = SPEAKER_CLS[colorCounter++ % SPEAKER_CLS.length];
  return speakerIndex[label];
}}

function setStatus(text, live=false) {{
  document.getElementById('statusText').textContent = text;
  document.getElementById('dot').className = 'dot' + (live ? ' live' : '');
}}

function toggleRecording() {{
  if (recording) stopRecording(); else startRecording();
}}

async function startRecording() {{
  const btn = document.getElementById('recordBtn');
  const maxSpeakers = document.getElementById('speakerSlider').value;
  const WS_URL = BASE_URL + '?max_speakers=' + maxSpeakers;
  btn.disabled = true;
  setStatus('Connecting…');
  try {{
    ws = new WebSocket(WS_URL);
    ws.onopen = async () => {{
      recording = true;
      btn.disabled = false;
      btn.classList.add('recording');
      btn.textContent = '⏹';
      setStatus('Live', true);
      document.getElementById('placeholder').style.display = 'none';
      document.getElementById('content').style.display = 'block';
      micStream = await navigator.mediaDevices.getUserMedia({{ audio: true }});
      audioCtx  = new AudioContext({{ sampleRate: 16000 }});
      const src = audioCtx.createMediaStreamSource(micStream);
      processor = audioCtx.createScriptProcessor(4096, 1, 1);
      processor.onaudioprocess = (e) => {{
        if (ws && ws.readyState === WebSocket.OPEN)
          ws.send(e.inputBuffer.getChannelData(0).buffer.slice(0));
      }};
      src.connect(processor);
      processor.connect(audioCtx.destination);
    }};
    ws.onmessage = (e) => {{
      const msg = JSON.parse(e.data);
      if      (msg.type === 'partial') updatePartial(msg.speaker, msg.text);
      else if (msg.type === 'final')   addFinal(msg.speaker, msg.text);
    }};
    ws.onerror = () => {{ setStatus('⚠ Cannot reach backend'); cleanup(); }};
    ws.onclose = () => {{ if (audioCtx) cleanup(); }};
  }} catch(err) {{
    setStatus('Error: ' + err.message);
    cleanup();
    btn.disabled = false;
  }}
}}

function stopRecording() {{ cleanup(); setStatus('Stopped'); }}

function cleanup() {{
  recording = false;
  if (processor) {{ processor.disconnect(); processor = null; }}
  if (audioCtx)  {{ audioCtx.close();       audioCtx  = null; }}
  if (micStream) {{ micStream.getTracks().forEach(t => t.stop()); micStream = null; }}
  if (ws)        {{ ws.close();             ws        = null; }}
  const btn = document.getElementById('recordBtn');
  btn.disabled = false;
  btn.classList.remove('recording');
  btn.textContent = '🎤';
}}

function updatePartial(speaker, text) {{
  const id = 'partial-' + speaker;
  let row = document.getElementById(id);
  if (!row) {{
    row = document.createElement('div');
    row.id = id; row.className = 'partial-row';
    document.getElementById('content').appendChild(row);
  }}
  const cls = speakerClass(speaker);
  const name = speaker.replace(/_/g, ' ');
  row.innerHTML = `<strong class="${{cls}}" style="font-size:10px;text-transform:uppercase;letter-spacing:.06em">${{name}}</strong>: ${{text}}`;
}}

function addFinal(speaker, text) {{
  document.getElementById('partial-' + speaker)?.remove();
  const cls = speakerClass(speaker);
  const name = speaker.replace(/_/g, ' ');
  const div = document.createElement('div');
  div.className = `utterance ${{cls}}`;
  div.innerHTML = `<span class="speaker-tag">${{name}}</span><span>${{text}}</span>`;
  document.getElementById('content').appendChild(div);
  const box = document.getElementById('transcript');
  box.scrollTop = box.scrollHeight;
}}
</script>
</body>
</html>
"""

components.html(transcript_component, height=750, scrolling=False)
