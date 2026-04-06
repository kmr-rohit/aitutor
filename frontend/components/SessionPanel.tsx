"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { AnimatePresence, motion } from "framer-motion";

import {
  SessionMode,
  SessionReport,
  base64ToBlob,
  blobToBase64,
  createSession,
  endSession,
  sessionWsUrl,
} from "@/lib/api";

type Message = {
  role: "learner" | "tutor";
  text: string;
};

const modeOptions: { label: string; value: SessionMode }[] = [
  { label: "HLD", value: "hld_practice" },
  { label: "Language", value: "language_deep_dive" },
  { label: "Concept", value: "concept_learn" },
  { label: "Rapid", value: "rapid_qa" },
];

function guessAudioMime(audioBase64: string): string {
  const head = atob(audioBase64.slice(0, 96));
  if (head.startsWith("RIFF") && head.includes("WAVE")) return "audio/wav";
  if (head.startsWith("ID3")) return "audio/mpeg";
  if (head.startsWith("OggS")) return "audio/ogg";
  if (head.startsWith("fLaC")) return "audio/flac";
  if (head.length >= 8 && head.slice(4, 8) === "ftyp") return "audio/mp4";
  const bytes = new Uint8Array(
    Array.from(head.slice(0, 2)).map((c) => c.charCodeAt(0)),
  );
  if (bytes.length >= 2 && bytes[0] === 0xff && (bytes[1] & 0xe0) === 0xe0) return "audio/mpeg";
  return "audio/wav";
}

async function playBase64Audio(audioBase64: string): Promise<void> {
  const guessed = guessAudioMime(audioBase64);
  const candidates = [guessed, "audio/mpeg", "audio/wav", "audio/mp4", "audio/ogg", "audio/flac"];
  let lastError: unknown = null;

  for (const mime of [...new Set(candidates)]) {
    const blob = base64ToBlob(audioBase64, mime);
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    audio.setAttribute("playsinline", "true");
    try {
      await audio.play();
      audio.onended = () => URL.revokeObjectURL(url);
      return;
    } catch (err) {
      lastError = err;
      URL.revokeObjectURL(url);
    }
  }

  throw lastError ?? new Error("Audio playback failed");
}

function reportToText(report: SessionReport): string {
  const scoreLines = Object.entries(report.rubric_scores)
    .map(([k, v]) => `- ${k}: ${v}/10`)
    .join("\n");

  return [
    "Session Report",
    "",
    `Summary: ${report.summary}`,
    "",
    "Strengths:",
    ...report.strengths.map((s) => `- ${s}`),
    "",
    "Improvement Areas:",
    ...report.improvement_areas.map((s) => `- ${s}`),
    "",
    "Next 20-Min Plan:",
    ...report.next_20_min_plan.map((s) => `- ${s}`),
    "",
    "Quick Quiz:",
    ...report.quiz_questions.map((s) => `- ${s}`),
    "",
    "Rubric:",
    scoreLines,
    "",
    "Detailed Report:",
    report.detailed_report || "N/A",
    "",
  ].join("\n");
}

export default function SessionPanel() {
  const [mode, setMode] = useState<SessionMode>("hld_practice");
  const [topic, setTopic] = useState("Design scalable notification service");
  const [difficulty, setDifficulty] = useState("intermediate");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [report, setReport] = useState<SessionReport | null>(null);
  const [loading, setLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [connection, setConnection] = useState("idle");
  const [error, setError] = useState("");
  const [recorderMime, setRecorderMime] = useState("not-initialized");
  const [voiceStatus, setVoiceStatus] = useState<"idle" | "sent" | "ok" | "failed">("idle");
  const [voiceStatusText, setVoiceStatusText] = useState("Waiting for mic input");
  const [audioUnlocked, setAudioUnlocked] = useState(false);
  const [installPrompt, setInstallPrompt] = useState<any>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const pcmChunksRef = useRef<Float32Array[]>([]);
  const awaitingVoiceResponseRef = useRef(false);

  const wsUrl = useMemo(() => (sessionId ? sessionWsUrl(sessionId) : null), [sessionId]);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
    if (!AudioCtx) {
      setRecorderMime("audio-context-unsupported");
      return;
    }
    const ctx = new AudioCtx();
    setRecorderMime(`audio/wav;rate=${ctx.sampleRate}`);
    void ctx.close();

    return () => {
      wsRef.current?.close();
      mediaRecorderRef.current?.stop();
      mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
      processorRef.current?.disconnect();
      sourceRef.current?.disconnect();
      void audioContextRef.current?.close();
    };
  }, []);

  useEffect(() => {
    const handler = (e: any) => {
      e.preventDefault();
      setInstallPrompt(e);
    };
    window.addEventListener("beforeinstallprompt", handler as EventListener);
    return () => window.removeEventListener("beforeinstallprompt", handler as EventListener);
  }, []);

  const unlockAudio = async () => {
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) return;
      const ctx = new AudioCtx();
      await ctx.resume();
      const buffer = ctx.createBuffer(1, 1, 22050);
      const src = ctx.createBufferSource();
      src.buffer = buffer;
      src.connect(ctx.destination);
      src.start(0);
      setAudioUnlocked(true);
      setVoiceStatusText("Audio playback enabled");
      await ctx.close();
    } catch {
      setVoiceStatusText("Tap Enable Sound again");
    }
  };

  const startSession = async () => {
    if (!audioUnlocked) await unlockAudio();
    setLoading(true);
    setError("");

    try {
      const session = await createSession({ mode, topic, difficulty });
      setSessionId(session.id);
      setMessages([]);
      setReport(null);

      const ws = new WebSocket(sessionWsUrl(session.id));
      ws.onopen = () => setConnection("connected");
      ws.onclose = () => setConnection("closed");
      ws.onerror = () => setConnection("error");
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.error) {
          setError(String(data.error));
          if (String(data.error).startsWith("stt_failed")) {
            setVoiceStatus("failed");
            setVoiceStatusText(String(data.error));
            awaitingVoiceResponseRef.current = false;
          }
          return;
        }

        if (data.text) {
          setMessages((prev) => [...prev, { role: "tutor", text: data.text }]);
          if (awaitingVoiceResponseRef.current) {
            setVoiceStatus("ok");
            setVoiceStatusText("Voice query transcribed and answered successfully");
            awaitingVoiceResponseRef.current = false;
          }
        }

        if (data.audio_base64) {
          void playBase64Audio(data.audio_base64).catch(() => {
            setVoiceStatusText("Audio blocked/unsupported. Tap Enable Sound and retry.");
          });
        }
      };

      wsRef.current = ws;
      setConnection("connecting");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start session");
    } finally {
      setLoading(false);
    }
  };

  const sendTextTurn = () => {
    if (!input.trim() || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;

    wsRef.current.send(
      JSON.stringify({
        role: "learner",
        text: input.trim(),
        language_style: "simple_hinglish",
      }),
    );

    setMessages((prev) => [...prev, { role: "learner", text: input.trim() }]);
    setInput("");
  };

  const encodeWav = (samples: Float32Array, sampleRate: number): Blob => {
    const bytesPerSample = 2;
    const blockAlign = bytesPerSample;
    const buffer = new ArrayBuffer(44 + samples.length * bytesPerSample);
    const view = new DataView(buffer);

    const writeString = (offset: number, value: string) => {
      for (let i = 0; i < value.length; i += 1) {
        view.setUint8(offset + i, value.charCodeAt(i));
      }
    };

    writeString(0, "RIFF");
    view.setUint32(4, 36 + samples.length * bytesPerSample, true);
    writeString(8, "WAVE");
    writeString(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, 1, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, 16, true);
    writeString(36, "data");
    view.setUint32(40, samples.length * bytesPerSample, true);

    let offset = 44;
    for (let i = 0; i < samples.length; i += 1) {
      const s = Math.max(-1, Math.min(1, samples[i]));
      view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
      offset += 2;
    }

    return new Blob([view], { type: "audio/wav" });
  };

  const mergePcmChunks = (chunks: Float32Array[]): Float32Array => {
    const total = chunks.reduce((sum, c) => sum + c.length, 0);
    const merged = new Float32Array(total);
    let offset = 0;
    for (const chunk of chunks) {
      merged.set(chunk, offset);
      offset += chunk.length;
    }
    return merged;
  };

  const startRecording = async () => {
    if (!sessionId || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      setError("Start session first and wait for websocket to connect.");
      return;
    }

    setError("");

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;

      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (!AudioCtx) {
        throw new Error("AudioContext not supported in this browser");
      }

      const audioContext = new AudioCtx();
      const source = audioContext.createMediaStreamSource(stream);
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      pcmChunksRef.current = [];

      processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        pcmChunksRef.current.push(new Float32Array(inputData));
      };

      source.connect(processor);
      processor.connect(audioContext.destination);

      audioContextRef.current = audioContext;
      sourceRef.current = source;
      processorRef.current = processor;
      setRecorderMime(`audio/wav;rate=${audioContext.sampleRate}`);
      setIsRecording(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Microphone access failed");
    }
  };

  const stopRecording = async () => {
    const context = audioContextRef.current;
    const sampleRate = context?.sampleRate ?? 44100;

    processorRef.current?.disconnect();
    sourceRef.current?.disconnect();
    await context?.close();
    processorRef.current = null;
    sourceRef.current = null;
    audioContextRef.current = null;

    const merged = mergePcmChunks(pcmChunksRef.current);
    const wavBlob = encodeWav(merged, sampleRate);
    const audioBase64 = await blobToBase64(wavBlob);

    wsRef.current?.send(
      JSON.stringify({
        role: "learner",
        audio_base64: audioBase64,
        audio_mime_type: "audio/wav",
        audio_filename: "voice-input.wav",
        language_style: "simple_hinglish",
      }),
    );

    awaitingVoiceResponseRef.current = true;
    setVoiceStatus("sent");
    setVoiceStatusText("Voice sent (audio/wav). Waiting for STT + tutor response...");
    setMessages((prev) => [...prev, { role: "learner", text: "[Voice message sent]" }]);

    mediaStreamRef.current?.getTracks().forEach((t) => t.stop());
    mediaStreamRef.current = null;
    pcmChunksRef.current = [];
    setIsRecording(false);
  };

  const finishSession = async () => {
    if (!sessionId) return;
    try {
      const result = await endSession(sessionId);
      setReport(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to end session");
    } finally {
      wsRef.current?.close();
      wsRef.current = null;
      setConnection("closed");
    }
  };

  const downloadReport = () => {
    if (!report) return;
    const text = reportToText(report);
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `session-report-${report.session_id}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <section className="voice-app">
      <div className="voice-topbar">
        <div>
          <p className="tiny">AI Tutor</p>
          <h2>Learning Session</h2>
        </div>
        <span className={`chip chip-${connection}`}>{connection}</span>
      </div>

      <div className="row actions">
        {!audioUnlocked && (
          <button className="btn btn-ghost" onClick={unlockAudio}>
            Enable Sound
          </button>
        )}
        {installPrompt && (
          <button
            className="btn btn-ghost"
            onClick={async () => {
              await installPrompt.prompt();
              setInstallPrompt(null);
            }}
          >
            Install App
          </button>
        )}
      </div>

      <div className="orb-wrap">
        <motion.div
          className="orb-ring"
          animate={{ scale: [1, 1.1, 1], opacity: [0.5, 0.9, 0.5] }}
          transition={{ duration: 2.2, repeat: Infinity, ease: "easeInOut" }}
        />
        <motion.div
          className="orb-core"
          animate={{ scale: [1, 1.04, 1] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        >
          <span>{isRecording ? "Recording" : "Ready"}</span>
        </motion.div>
      </div>

      <div className="compat-panel">
        <p className="tiny">Audio Compatibility</p>
        <p className="line">Recorder: {recorderMime}</p>
        <div className={`chip chip-${voiceStatus}`}>{voiceStatus}</div>
        <p className="line muted">{voiceStatusText}</p>
      </div>

      <div className="row mode-row">
        <select value={mode} onChange={(e) => setMode(e.target.value as SessionMode)}>
          {modeOptions.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
        <input value={difficulty} onChange={(e) => setDifficulty(e.target.value)} placeholder="difficulty" />
      </div>
      <input value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Topic for this session" />

      <div className="row actions">
        <button className="btn btn-primary" disabled={loading} onClick={startSession}>
          {loading ? "Starting..." : "Start"}
        </button>
        <button className="btn btn-ghost" onClick={finishSession}>
          End + Report
        </button>
      </div>

      <div className="chat-area">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.p className="placeholder" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              Ask anything in voice or text.
            </motion.p>
          )}

          {messages.map((m, idx) => (
            <motion.div
              key={`${m.role}-${idx}`}
              className={`msg msg-${m.role}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
            >
              <strong>{m.role === "tutor" ? "Tutor" : "You"}</strong>
              <p>{m.text}</p>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      <div className="composer">
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type your follow-up..." />
        <button className="btn btn-ghost" onClick={sendTextTurn}>
          Send
        </button>
        {!isRecording ? (
          <button className="btn btn-voice" onClick={startRecording}>
            Hold Mic
          </button>
        ) : (
          <button className="btn btn-danger" onClick={stopRecording}>
            Stop + Send
          </button>
        )}
      </div>

      {wsUrl && <p className="status-text">WS: {wsUrl}</p>}
      {error && <p className="status-text error">{error}</p>}

      {report && (
        <motion.section className="report-panel" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
          <h3>Session Report</h3>
          <p>{report.summary}</p>
          <p className="tiny">Detailed Report</p>
          <p className="detail">{report.detailed_report}</p>
          <div className="row actions">
            <button className="btn btn-ghost" onClick={downloadReport}>
              Download .txt
            </button>
          </div>
        </motion.section>
      )}
    </section>
  );
}
