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

def get_backend_url() -> str:
    try:
        return st.secrets["BACKEND_WS_URL"]
    except (KeyError, FileNotFoundError):
        return os.getenv("BACKEND_WS_URL", "ws://localhost:8000/ws/transcribe")

backend_url = get_backend_url()
max_speakers = st.slider("Max speakers", min_value=1, max_value=6, value=2)

transcript_component = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<style>
  :root {{
    --bg:      #ffffff;
    --text:    #111827;
    --muted:   #9ca3af;
    --border:  #e5e7eb;
    --card:    #f9fafb;
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
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 24px 16px;
    gap: 24px;
  }}

  h1 {{
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -.5px;
  }}

  p.sub {{
    font-size: 14px;
    color: var(--muted);
    margin-top: 4px;
    text-align: center;
  }}

  /* ── Record button ── */
  .record-wrap {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }}

  #recordBtn {{
    width: 72px;
    height: 72px;
    border-radius: 50%;
    border: none;
    background: var(--accent);
    color: #fff;
    font-size: 28px;
    cursor: pointer;
    box-shadow: 0 4px 14px rgba(239,68,68,.4);
    transition: transform .15s, box-shadow .15s;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  #recordBtn:hover {{ transform: scale(1.07); box-shadow: 0 6px 20px rgba(239,68,68,.5); }}
  #recordBtn.recording {{
    background: #111827;
    box-shadow: 0 4px 14px rgba(0,0,0,.25);
    animation: pulse 1.4s infinite;
  }}
  @keyframes pulse {{
    0%,100% {{ box-shadow: 0 0 0 0 rgba(17,24,39,.4); }}
    50%      {{ box-shadow: 0 0 0 10px rgba(17,24,39,0); }}
  }}

  /* ── Status ── */
  #status {{
    font-size: 13px;
    color: var(--muted);
    display: flex;
    align-items: center;
    gap: 6px;
  }}
  .dot {{
    width: 7px; height: 7px;
    border-radius: 50%;
    background: var(--muted);
  }}
  .dot.live {{ background: var(--accent); animation: blink 1.1s infinite; }}
  @keyframes blink {{ 0%,100% {{ opacity:1 }} 50% {{ opacity:.2 }} }}

  /* ── Transcript ── */
  #transcript {{
    width: 100%;
    max-width: 680px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px 24px;
    min-height: 280px;
    max-height: 460px;
    overflow-y: auto;
    font-size: 15px;
    line-height: 1.8;
  }}

  #placeholder {{
    color: var(--muted);
    text-align: center;
    padding: 80px 0;
    font-size: 14px;
    user-select: none;
  }}

  .utterance {{
    display: flex;
    flex-direction: column;
    gap: 2px;
    margin-bottom: 16px;
    padding: 10px 14px;
    border-radius: 10px;
    background: #fff;
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
    font-size: 10px;
    font-weight: 700;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 2px;
  }}
  .s1 .speaker-tag {{ color: var(--s1); }}
  .s2 .speaker-tag {{ color: var(--s2); }}
  .s3 .speaker-tag {{ color: var(--s3); }}
  .s4 .speaker-tag {{ color: var(--s4); }}
  .s5 .speaker-tag {{ color: var(--s5); }}
  .s6 .speaker-tag {{ color: var(--s6); }}

  .partial-row {{
    padding: 6px 14px;
    margin-bottom: 8px;
    border-left: 2px solid var(--border);
    color: var(--muted);
    font-style: italic;
    font-size: 14px;
  }}
</style>
</head>
<body>

  <div style="text-align:center">
    <h1>Live Transcription</h1>
    <p class="sub">Real-time speech-to-text with speaker diarization</p>
  </div>

  <div class="record-wrap">
    <button id="recordBtn" onclick="toggleRecording()" title="Start / Stop recording">🎤</button>
    <div id="status">
      <div class="dot" id="dot"></div>
      <span id="statusText">Press to start</span>
    </div>
  </div>

  <div id="transcript">
    <div id="placeholder">Press the button above to begin live transcription</div>
    <div id="content" style="display:none"></div>
  </div>

<script>
const WS_URL      = "{backend_url}?max_speakers={max_speakers}";
const SPEAKER_CLS = ['s1','s2','s3','s4','s5','s6'];

let ws           = null;
let audioCtx     = null;
let processor    = null;
let micStream    = null;
let speakerIndex = {{}};
let colorCounter = 0;
let recording    = false;

function speakerClass(label) {{
  if (!(label in speakerIndex)) {{
    speakerIndex[label] = SPEAKER_CLS[colorCounter % SPEAKER_CLS.length];
    colorCounter++;
  }}
  return speakerIndex[label];
}}

function setStatus(text, live = false) {{
  document.getElementById('statusText').textContent = text;
  document.getElementById('dot').className = 'dot' + (live ? ' live' : '');
}}

function toggleRecording() {{
  if (recording) stopRecording();
  else startRecording();
}}

async function startRecording() {{
  const btn = document.getElementById('recordBtn');
  btn.disabled = true;
  setStatus('Connecting…');

  try {{
    ws = new WebSocket(WS_URL);

    ws.onopen = async () => {{
      recording = true;
      btn.disabled  = false;
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

  }} catch (err) {{
    setStatus('Error: ' + err.message);
    cleanup();
    document.getElementById('recordBtn').disabled = false;
  }}
}}

function stopRecording() {{
  cleanup();
  setStatus('Stopped');
}}

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
  const id  = 'partial-' + speaker;
  let   row = document.getElementById(id);
  if (!row) {{
    row = document.createElement('div');
    row.id = id;
    row.className = 'partial-row';
    document.getElementById('content').appendChild(row);
  }}
  const cls  = speakerClass(speaker);
  const name = speaker.replace(/_/g, ' ');
  row.innerHTML = `<strong class="${{cls}}" style="font-size:10px;text-transform:uppercase;letter-spacing:.06em">${{name}}</strong>: ${{text}}`;
}}

function addFinal(speaker, text) {{
  const partial = document.getElementById('partial-' + speaker);
  if (partial) partial.remove();
  const cls  = speakerClass(speaker);
  const name = speaker.replace(/_/g, ' ');
  const div  = document.createElement('div');
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

components.html(transcript_component, height=700, scrolling=False)
