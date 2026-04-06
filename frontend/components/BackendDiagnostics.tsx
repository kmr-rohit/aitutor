"use client";

import { useState } from "react";

import { motion } from "framer-motion";

import { base64ToBlob, providerLLMTest, providerSTTTest, providerTTSPreview } from "@/lib/api";

export default function BackendDiagnostics() {
  const [llmPrompt, setLlmPrompt] = useState("Hinglish me cache invalidation simple explain karo");
  const [llmResult, setLlmResult] = useState("");
  const [sttResult, setSttResult] = useState("");
  const [status, setStatus] = useState("");

  const testLLM = async () => {
    setStatus("Testing LLM...");
    try {
      const res = await providerLLMTest(llmPrompt, "hld_practice");
      setLlmResult(res.answer);
      setStatus("LLM OK");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "LLM failed");
    }
  };

  const testTTS = async () => {
    setStatus("Testing TTS...");
    try {
      const res = await providerTTSPreview("Aaj hum HLD ko easy Hinglish me break karenge.");
      const audio = new Audio(URL.createObjectURL(base64ToBlob(res.audio_base64, "audio/wav")));
      await audio.play();
      setStatus(`TTS OK (${res.bytes_length} bytes)`);
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "TTS failed");
    }
  };

  const onUploadAudio = async (file: File | null) => {
    if (!file) return;
    setStatus("Testing STT...");
    try {
      const res = await providerSTTTest(file);
      setSttResult(`${res.text} [${res.lang}, ${res.confidence.toFixed(2)}]`);
      setStatus("STT OK");
    } catch (err) {
      setStatus(err instanceof Error ? err.message : "STT failed");
    }
  };

  return (
    <motion.section
      className="tool-card"
      initial={{ opacity: 0, y: 12 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.35 }}
    >
      <h3>Provider Checks</h3>
      <p className="card-sub">Validate backend providers before a live session.</p>

      <label>
        <span>LLM Prompt</span>
        <input value={llmPrompt} onChange={(e) => setLlmPrompt(e.target.value)} />
      </label>

      <div className="row actions">
        <button className="btn btn-ghost" onClick={testLLM}>
          LLM
        </button>
        <button className="btn btn-ghost" onClick={testTTS}>
          TTS
        </button>
        <label className="btn btn-ghost file">
          STT
          <input type="file" accept="audio/*" onChange={(e) => onUploadAudio(e.target.files?.[0] ?? null)} hidden />
        </label>
      </div>

      {status && <p className="status-text">{status}</p>}
      {llmResult && <p className="result-text">{llmResult}</p>}
      {sttResult && <p className="result-text">{sttResult}</p>}
    </motion.section>
  );
}
