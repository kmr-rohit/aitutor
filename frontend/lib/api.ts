export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api";

export type SessionMode = "concept_learn" | "hld_practice" | "language_deep_dive" | "rapid_qa";

export type Session = {
  id: string;
  mode: SessionMode;
  topic: string;
  difficulty: string;
  created_at: string;
  status: string;
};

export type SessionReport = {
  session_id: string;
  summary: string;
  strengths: string[];
  improvement_areas: string[];
  next_20_min_plan: string[];
  quiz_questions: string[];
  rubric_scores: Record<string, number>;
  detailed_report: string;
};

export type ProviderLLMResponse = {
  answer: string;
  hints: string[];
  followups: string[];
};

export type ProviderTTSResponse = {
  audio_base64: string;
  bytes_length: number;
};

function requireOk(res: Response, fallback: string): void {
  if (res.ok) return;
  throw new Error(`${fallback} (status ${res.status})`);
}

export async function createSession(payload: {
  mode: SessionMode;
  topic: string;
  difficulty: string;
}): Promise<Session> {
  const res = await fetch(`${API_BASE}/sessions`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  requireOk(res, "Failed to create session");
  return res.json();
}

export async function endSession(sessionId: string): Promise<SessionReport> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/end`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({}),
  });
  requireOk(res, "Failed to end session");
  return res.json();
}

export async function scheduleNudge(payload: {
  user_id: string;
  channel: string;
  message: string;
  scheduled_for: string;
}): Promise<{ nudge_id: string; status: string }> {
  const res = await fetch(`${API_BASE}/nudges/schedule`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  requireOk(res, "Failed to schedule nudge");
  return res.json();
}

export async function providerLLMTest(text: string, mode: SessionMode): Promise<ProviderLLMResponse> {
  const res = await fetch(`${API_BASE}/providers/llm/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, mode }),
  });
  requireOk(res, "LLM provider test failed");
  return res.json();
}

export async function providerTTSPreview(text: string): Promise<ProviderTTSResponse> {
  const res = await fetch(`${API_BASE}/providers/tts/test`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, voice_id: "", language_style: "simple_hinglish" }),
  });
  requireOk(res, "TTS provider test failed");
  return res.json();
}

export async function providerSTTTest(file: File): Promise<{ text: string; lang: string; confidence: number }> {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/providers/stt/test`, {
    method: "POST",
    body: form,
  });
  requireOk(res, "STT provider test failed");
  return res.json();
}

export function sessionWsUrl(sessionId: string): string {
  const raw = `${API_BASE}/sessions/${sessionId}/voice`;
  if (raw.startsWith("https://")) return raw.replace("https://", "wss://");
  if (raw.startsWith("http://")) return raw.replace("http://", "ws://");
  return raw;
}

export function base64ToBlob(base64: string, mimeType: string): Blob {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Blob([bytes], { type: mimeType });
}

export async function blobToBase64(blob: Blob): Promise<string> {
  const arr = await blob.arrayBuffer();
  let binary = "";
  const bytes = new Uint8Array(arr);
  for (let i = 0; i < bytes.byteLength; i += 1) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary);
}
